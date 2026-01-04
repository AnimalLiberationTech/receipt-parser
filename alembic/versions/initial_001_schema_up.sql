-- Initial Schema Migration (Non-conflicting tables)
-- Revision ID: initial_001_schema
-- Revises: legacy_000_schema
-- Create Date: 2026-01-03
--
-- This migration creates tables that DON'T conflict with legacy schema.
-- Conflicting tables (shop, user, etc.) are in migration 002.

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- Country codes (ISO 3166-1 alpha-2)
CREATE TYPE country_code AS ENUM ('md');

-- Currency codes (ISO 4217)
CREATE TYPE currency_code AS ENUM ('mdl');

-- Item barcode status
CREATE TYPE item_barcode_status AS ENUM ('pending', 'missing', 'irrelevant', 'added');

-- Quantity unit
CREATE TYPE quantity_unit AS ENUM ('pcs', 'kg', 'g', 'l', 'ml', 'm', 'cm');

-- User rights groups
CREATE TYPE user_rights_group AS ENUM (
    'normal',
    'tester',
    'content_moderator',
    'everything_moderator',
    'administrator'
);

-- Gender
CREATE TYPE gender AS ENUM ('male', 'female', 'transgender', 'non-binary', 'other');

-- Identity provider
CREATE TYPE identity_provider AS ENUM ('google');

-- OSM object type
CREATE TYPE osm_type AS ENUM ('node', 'way', 'relation');

-- ============================================================================
-- TABLES (Non-conflicting with legacy schema)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Schema: src/schemas/receipt.py
-- ----------------------------------------------------------------------------
CREATE TABLE receipt (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    company_id TEXT NOT NULL,
    company_name TEXT NOT NULL,
    country_code country_code NOT NULL,
    cash_register_id TEXT NOT NULL,
    key TEXT NOT NULL,
    currency_code currency_code NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    receipt_url TEXT NOT NULL,
    shop_id UUID,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_receipt_user_id ON receipt (user_id);
CREATE INDEX idx_receipt_date ON receipt (date);
CREATE INDEX idx_receipt_country_code ON receipt (country_code);
CREATE INDEX idx_receipt_shop_id ON receipt (shop_id);
CREATE INDEX idx_receipt_data ON receipt USING GIN (data);

-- ----------------------------------------------------------------------------
-- Schema: src/schemas/purchased_item.py
-- ----------------------------------------------------------------------------
CREATE TABLE purchased_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id TEXT NOT NULL REFERENCES receipt(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    quantity DECIMAL(12, 3) NOT NULL,
    quantity_unit quantity_unit DEFAULT 'pcs',
    price DECIMAL(12, 2) NOT NULL,
    item_id UUID NOT NULL,  -- References shop_item
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchased_item_receipt_id ON purchased_item (receipt_id);
CREATE INDEX idx_purchased_item_item_id ON purchased_item (item_id) WHERE item_id IS NOT NULL;

-- ----------------------------------------------------------------------------
-- Schema: src/schemas/shop_item.py
-- ----------------------------------------------------------------------------
CREATE TABLE shop_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL,
    name TEXT NOT NULL,
    status item_barcode_status NOT NULL DEFAULT 'pending',
    barcode TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shop_item_shop_id ON shop_item (shop_id);
CREATE INDEX idx_shop_item_name ON shop_item (name);
CREATE INDEX idx_shop_item_barcode ON shop_item (barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_shop_item_status ON shop_item (status);

-- ----------------------------------------------------------------------------
-- Schema: src/schemas/receipt_url.py
-- ----------------------------------------------------------------------------
CREATE TABLE receipt_url (
    id TEXT PRIMARY KEY,  -- MD5 hash of url
    url TEXT NOT NULL,
    receipt_id TEXT NOT NULL REFERENCES receipt(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_receipt_url_receipt_id ON receipt_url (receipt_id);

-- ============================================================================
-- TRIGGERS FOR updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_receipt_updated_at
    BEFORE UPDATE ON receipt
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_purchased_item_updated_at
    BEFORE UPDATE ON purchased_item
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shop_item_updated_at
    BEFORE UPDATE ON shop_item
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
