-- Conflicting Tables Migration (Tables that conflict with legacy schema)
-- Revision ID: 003_conflicting_schema
-- Revises: 002_shop_address
-- Create Date: 2026-01-04
--
-- Mapping:
--   src/schemas/user.py         -> "user" (ALTER existing table)
--   src/schemas/user_identity.py -> user_identity
--   src/schemas/user_session.py -> user_session

-- ============================================================================
-- ALTER EXISTING TABLES
-- ============================================================================

-- Add osm_data field to legacy shop table
ALTER TABLE shop ADD COLUMN IF NOT EXISTS osm_data JSONB DEFAULT NULL;

-- ============================================================================
-- ALTER EXISTING USER TABLE
-- ============================================================================
-- Schema: src/schemas/user.py
-- Existing fields: id, banned, google_id, login_generation, creation_time,
--   name, gender, birthday, eats_milk, eats_eggs, eats_honey, user_rights_group,
--   apple_id, langs_prioritized, self_description, has_avatar, avatar_id
-- Adding missing fields: email, data, updated_at
-- ----------------------------------------------------------------------------
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS data JSONB NOT NULL DEFAULT '{}';
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_user_email ON "user" (email);
CREATE INDEX IF NOT EXISTS idx_user_data ON "user" USING GIN (data);

-- ----------------------------------------------------------------------------
-- Table: user_identity
-- Schema: src/schemas/user_identity.py
-- ----------------------------------------------------------------------------
CREATE TABLE user_identity (
    id TEXT PRIMARY KEY,  -- Provider-specific user ID
    provider identity_provider NOT NULL,
    user_id UUID NOT NULL REFERENCES "user"(id),
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (provider, id)
);

CREATE INDEX idx_user_identity_provider ON user_identity (provider);
CREATE INDEX idx_user_identity_user_id ON user_identity (user_id);
CREATE INDEX idx_user_identity_data ON user_identity USING GIN (data);

-- ----------------------------------------------------------------------------
-- Table: user_session
-- Schema: src/schemas/user_session.py
-- ----------------------------------------------------------------------------
CREATE TABLE user_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_provider identity_provider NOT NULL,
    user_id UUID REFERENCES "user"(id),
    user_name TEXT,
    state TEXT,  -- For OAuth state parameter (Google)
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_session_identity_provider ON user_session (identity_provider);
CREATE INDEX idx_user_session_user_id ON user_session (user_id);
CREATE INDEX idx_user_session_state ON user_session (state) WHERE state IS NOT NULL;
CREATE INDEX idx_user_session_data ON user_session USING GIN (data);

-- ============================================================================
-- TRIGGERS FOR updated_at
-- ============================================================================

CREATE TRIGGER update_user_updated_at
    BEFORE UPDATE ON "user"
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_identity_updated_at
    BEFORE UPDATE ON user_identity
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_session_updated_at
    BEFORE UPDATE ON user_session
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

