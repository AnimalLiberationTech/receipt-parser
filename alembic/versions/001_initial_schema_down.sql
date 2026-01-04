-- Initial Schema Migration - DOWNGRADE (Non-conflicting tables)
-- Revision ID: initial_001_schema
-- Revises: legacy_000_schema
-- Create Date: 2026-01-03

-- Drop triggers
DROP TRIGGER IF EXISTS update_receipt_url_updated_at ON receipt_url;
DROP TRIGGER IF EXISTS update_shop_item_updated_at ON shop_item;
DROP TRIGGER IF EXISTS update_purchased_item_updated_at ON purchased_item;
DROP TRIGGER IF EXISTS update_receipt_updated_at ON receipt;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables
DROP TABLE IF EXISTS receipt_url CASCADE;
DROP TABLE IF EXISTS shop_item CASCADE;
DROP TABLE IF EXISTS purchased_item CASCADE;
DROP TABLE IF EXISTS receipt CASCADE;

-- Drop enum types
DROP TYPE IF EXISTS osm_type;
DROP TYPE IF EXISTS identity_provider;
DROP TYPE IF EXISTS gender;
DROP TYPE IF EXISTS user_rights_group;
DROP TYPE IF EXISTS quantity_unit;
DROP TYPE IF EXISTS item_barcode_status;
DROP TYPE IF EXISTS currency_code;
DROP TYPE IF EXISTS country_code;

