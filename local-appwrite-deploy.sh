#!/usr/bin/env bash
#
# Local Development Deployment Script
# Deploys Appwrite Functions locally and migrates PostgreSQL database
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
MIGRATION_TARGET="003_conflicting_schema"
SKIP_DOCKER=false
SKIP_MIGRATION=true
SKIP_FUNCTIONS=false
RESTORE_DATA=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            MIGRATION_TARGET="$2"
            shift 2
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-migration)
            SKIP_MIGRATION=true
            shift
            ;;
        --skip-functions)
            SKIP_FUNCTIONS=true
            shift
            ;;
        --restore-data)
            RESTORE_DATA="$2"
            shift 2
            ;;
        --down)
            log_info "Stopping local services..."
            docker compose -f docker-compose.local.yml down
            log_success "Services stopped"
            exit 0
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --target <revision>   Migration target revision (default: legacy_000_schema)"
            echo "  --skip-docker         Skip starting Docker containers"
            echo "  --skip-migration      Skip database migration"
            echo "  --skip-functions      Skip function deployment"
            echo "  --restore-data <file> Restore data from SQL backup file"
            echo "  --down                Stop all local services"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Load environment variables from .env file
if [ -f "$SCRIPT_DIR/.env" ]; then
    log_info "Loading environment variables from .env"
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
else
    log_warning ".env file not found, using defaults"
    export LOCAL_POSTGRES_HOST="localhost"
    export LOCAL_POSTGRES_PORT="5432"
    export LOCAL_POSTGRES_DB="receipt_local"
    export LOCAL_POSTGRES_USER="postgres"
    export LOCAL_POSTGRES_PASSWORD="postgres"
fi

export ENV_NAME="local"

# Start Docker containers
if [ "$SKIP_DOCKER" = false ]; then
    log_info "Starting Docker containers..."

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi

    docker compose -f docker-compose.local.yml up -d

    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    until docker exec receipt-parser-postgres pg_isready -U postgres > /dev/null 2>&1; do
        sleep 1
    done
    log_success "PostgreSQL is ready"
fi

# Run database migration
if [ "$SKIP_MIGRATION" = false ]; then
    log_info "Running database migration to: $MIGRATION_TARGET"

    # Run migration using uv
    uv run python migrations.py --env local --db postgres --action up --revision "$MIGRATION_TARGET" --no-backup

    log_success "Database migration completed"
fi

# Restore data from backup if specified
if [ -n "$RESTORE_DATA" ]; then
    if [ ! -f "$RESTORE_DATA" ]; then
        log_error "Data file not found: $RESTORE_DATA"
        exit 1
    fi

    log_info "Restoring data from: $RESTORE_DATA"

    # Check if we need to reorder the data file
    ORDERED_FILE="${RESTORE_DATA%.sql}_ordered.sql"
    if [ ! -f "$ORDERED_FILE" ]; then
        log_info "Reordering data file to respect foreign key constraints..."
        uv run python reorder_data_import.py "$RESTORE_DATA"
    fi

    # Use the ordered file if it exists
    if [ -f "$ORDERED_FILE" ]; then
        DATA_FILE="$ORDERED_FILE"
    else
        DATA_FILE="$RESTORE_DATA"
    fi

    # Restore using psql
    PGPASSWORD="${LOCAL_POSTGRES_PASSWORD:-postgres}" psql \
        -h "${LOCAL_POSTGRES_HOST:-localhost}" \
        -p "${LOCAL_POSTGRES_PORT:-5432}" \
        -U "${LOCAL_POSTGRES_USER:-postgres}" \
        -d "${LOCAL_POSTGRES_DB:-receipt_local}" \
        -f "$DATA_FILE"

    log_success "Data restore completed"
fi

# Deploy Appwrite Functions locally
if [ "$SKIP_FUNCTIONS" = false ]; then
    log_info "Deploying Appwrite Functions locally..."

    FUNCTIONS_DIR="$SCRIPT_DIR/appwrite_functions"
    BUILD_DIR="$SCRIPT_DIR/.local_functions"

    # Create build directory
    mkdir -p "$BUILD_DIR"

    # Process each function
    for func_dir in "$FUNCTIONS_DIR"/*/; do
        if [ -d "$func_dir" ]; then
            func_name=$(basename "$func_dir")
            log_info "Building function: $func_name"

            func_build_dir="$BUILD_DIR/$func_name"
            mkdir -p "$func_build_dir"

            # Copy function files
            cp -r "$func_dir"/* "$func_build_dir/"

            # Copy src directory for imports
            if [ -d "$SCRIPT_DIR/src" ]; then
                cp -r "$SCRIPT_DIR/src" "$func_build_dir/"
            fi

            # Create .env file for function
            cat > "$func_build_dir/.env" << EOF
ENV_NAME=local
LOCAL_POSTGRES_HOST=host.docker.internal
LOCAL_POSTGRES_PORT=${LOCAL_POSTGRES_PORT:-5432}
LOCAL_POSTGRES_DB=${LOCAL_POSTGRES_DB:-receipt_local}
LOCAL_POSTGRES_USER=${LOCAL_POSTGRES_USER:-postgres}
LOCAL_POSTGRES_PASSWORD=${LOCAL_POSTGRES_PASSWORD:-postgres}
EOF

            # Install dependencies in function directory
            if [ -f "$func_build_dir/requirements.txt" ]; then
                log_info "Installing dependencies for $func_name..."
                pip install -q -r "$func_build_dir/requirements.txt" -t "$func_build_dir/.pythonlibs" 2>/dev/null || true
            fi

            log_success "Function $func_name built successfully"
        fi
    done

    log_success "All functions deployed to $BUILD_DIR"

    # Print info about testing functions
    echo ""
    log_info "To test functions locally, run:"
    echo "  uv run python local_appwrite_functions.py parse_from_url --body '{\"url\": \"...\", \"user_id\": \"...\"}'"
fi

echo ""
log_success "Local deployment completed!"
echo ""
echo "Services:"
echo "  - PostgreSQL: localhost:${LOCAL_POSTGRES_PORT:-5432} (user: ${LOCAL_POSTGRES_USER:-postgres}, db: ${LOCAL_POSTGRES_DB:-receipt_local})"
echo ""
echo "Test functions locally:"
echo "  uv run python local_appwrite_functions.py parse_from_url --body '{\"url\": \"...\", \"user_id\": \"...\"}'"
echo ""
echo "To stop services: $0 --down"

