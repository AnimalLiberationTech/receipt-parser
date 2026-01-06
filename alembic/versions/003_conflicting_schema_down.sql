-- Conflicting Tables Migration - DOWNGRADE
-- Revision ID: 003_conflicting_schema
-- Revises: 002_shop_address
-- Create Date: 2026-01-04

-- Drop triggers
DROP TRIGGER IF EXISTS update_user_session_updated_at ON user_session;
DROP TRIGGER IF EXISTS update_user_identity_updated_at ON user_identity;
DROP TRIGGER IF EXISTS update_user_updated_at ON "user";

-- Drop tables (in reverse order due to foreign key constraints)
DROP TABLE IF EXISTS user_session CASCADE;
DROP TABLE IF EXISTS user_identity CASCADE;

-- Remove added columns from user table
DROP INDEX IF EXISTS idx_user_data;
DROP INDEX IF EXISTS idx_user_email;
ALTER TABLE "user" DROP COLUMN IF EXISTS updated_at;
ALTER TABLE "user" DROP COLUMN IF EXISTS data;
ALTER TABLE "user" DROP COLUMN IF EXISTS email;

-- Remove osm_data from shop table
ALTER TABLE shop DROP COLUMN IF EXISTS osm_data;

