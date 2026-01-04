#!/usr/bin/env python
"""Database backup script for PostgreSQL.

Creates a backup of the PostgreSQL database before migrations are performed.
Backups are stored in the `backups/` directory with timestamp and environment info.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_db_config(env: str) -> dict:
    """Get database configuration from environment variables."""
    env_upper = env.upper()
    return {
        "host": os.environ.get(f"{env_upper}_POSTGRES_HOST", "localhost"),
        "port": os.environ.get(f"{env_upper}_POSTGRES_PORT", "5432"),
        "database": os.environ.get(f"{env_upper}_POSTGRES_DB", "postgres"),
        "user": os.environ.get(f"{env_upper}_POSTGRES_USER", "postgres"),
        "password": os.environ.get(f"{env_upper}_POSTGRES_PASSWORD", "postgres"),
    }


def create_backup(env: str, backup_dir: str = "backups") -> str:
    """Create a PostgreSQL database backup using pg_dump.

    Args:
        env: Environment name (dev, test, stage, prod)
        backup_dir: Directory to store backups

    Returns:
        Path to the created backup file
    """
    config = get_db_config(env)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create backup directory if it doesn't exist
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)

    # Generate backup filename
    backup_file = backup_path / f"{config['database']}_r{timestamp}.sql"

    # Set PGPASSWORD environment variable for pg_dump
    env_vars = os.environ.copy()
    env_vars["PGPASSWORD"] = config["password"]

    # Build pg_dump command
    cmd = [
        "pg_dump",
        "-h", config["host"],
        "-p", config["port"],
        "-U", config["user"],
        "-d", config["database"],
        "-f", str(backup_file),
        "--no-owner",
        "--no-acl",
    ]

    print(f"Creating backup: {backup_file}")

    try:
        result = subprocess.run(
            cmd,
            env=env_vars,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Backup created successfully: {backup_file}")
        return str(backup_file)
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e.stderr}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print(
            "pg_dump not found. Please install PostgreSQL client tools.",
            file=sys.stderr,
        )
        raise


def restore_backup(backup_file: str, env: str) -> None:
    """Restore a PostgreSQL database from a backup file.

    Args:
        backup_file: Path to the backup file
        env: Environment name (dev, test, stage, prod)
    """
    config = get_db_config(env)

    # Set PGPASSWORD environment variable for psql
    env_vars = os.environ.copy()
    env_vars["PGPASSWORD"] = config["password"]

    # Build psql command
    cmd = [
        "psql",
        "-h", config["host"],
        "-p", config["port"],
        "-U", config["user"],
        "-d", config["database"],
        "-f", backup_file,
    ]

    print(f"Restoring backup: {backup_file}")

    try:
        result = subprocess.run(
            cmd,
            env=env_vars,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Backup restored successfully from: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Restore failed: {e.stderr}", file=sys.stderr)
        raise


def list_backups(backup_dir: str = "backups", env: str = None) -> list:
    """List available backups.

    Args:
        backup_dir: Directory containing backups
        env: Optional environment filter

    Returns:
        List of backup files
    """
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        return []

    backups = sorted(backup_path.glob("*.sql"), reverse=True)

    if env:
        backups = [b for b in backups if f"_{env}_" in b.name]

    return [str(b) for b in backups]


def cleanup_old_backups(backup_dir: str = "backups", keep: int = 10, env: str = None):
    """Remove old backups, keeping only the most recent ones.

    Args:
        backup_dir: Directory containing backups
        keep: Number of backups to keep
        env: Optional environment filter
    """
    backups = list_backups(backup_dir, env)

    if len(backups) <= keep:
        return

    to_remove = backups[keep:]
    for backup_file in to_remove:
        print(f"Removing old backup: {backup_file}")
        Path(backup_file).unlink()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PostgreSQL backup utility")
    parser.add_argument(
        "action",
        choices=["backup", "restore", "list", "cleanup"],
        help="Action to perform",
    )
    parser.add_argument(
        "--env",
        type=str,
        default="dev",
        help="Environment (dev, test, stage, prod)",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Backup file for restore action",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=10,
        help="Number of backups to keep for cleanup action",
    )

    args = parser.parse_args()

    os.environ.setdefault("ENV_NAME", args.env)

    if args.action == "backup":
        create_backup(args.env)
    elif args.action == "restore":
        if not args.file:
            print("--file is required for restore action", file=sys.stderr)
            sys.exit(1)
        restore_backup(args.file, args.env)
    elif args.action == "list":
        backups = list_backups(env=args.env)
        if backups:
            print(f"Available backups for {args.env}:")
            for b in backups:
                print(f"  {b}")
        else:
            print(f"No backups found for {args.env}")
    elif args.action == "cleanup":
        cleanup_old_backups(keep=args.keep, env=args.env)

