-- Legacy Schema Migration - DOWNGRADE
-- WARNING: This will delete all legacy tables!

-- Drop tables
DROP TABLE IF EXISTS "user_quiz" CASCADE;
DROP TABLE IF EXISTS "user_contribution" CASCADE;
DROP TABLE IF EXISTS "public" CASCADE;
DROP TABLE IF EXISTS "shops_validation_queue" CASCADE;
DROP TABLE IF EXISTS "shop" CASCADE;
DROP TABLE IF EXISTS "product_scan" CASCADE;
DROP TABLE IF EXISTS "product_presence_vote" CASCADE;
DROP TABLE IF EXISTS "product_like_table" CASCADE;
DROP TABLE IF EXISTS "product_change" CASCADE;
DROP TABLE IF EXISTS "product_at_shop" CASCADE;
DROP TABLE IF EXISTS "product" CASCADE;
DROP TABLE IF EXISTS "news_piece_table" CASCADE;
DROP TABLE IF EXISTS "news_piece_product_at_shop" CASCADE;
DROP TABLE IF EXISTS "moderator_task" CASCADE;

-- Drop sequences
DROP SEQUENCE IF EXISTS user_quiz_id_seq CASCADE;
DROP SEQUENCE IF EXISTS user_contribution_id_seq CASCADE;
DROP SEQUENCE IF EXISTS shops_validation_queue_id_seq CASCADE;
DROP SEQUENCE IF EXISTS shop_id_seq CASCADE;
DROP SEQUENCE IF EXISTS product_scan_id_seq CASCADE;
DROP SEQUENCE IF EXISTS product_presence_vote_id_seq CASCADE;
DROP SEQUENCE IF EXISTS product_like_table_id_seq CASCADE;
DROP SEQUENCE IF EXISTS product_id_seq CASCADE;
DROP SEQUENCE IF EXISTS product_change_id_seq CASCADE;
DROP SEQUENCE IF EXISTS product_at_shop_id_seq CASCADE;
DROP SEQUENCE IF EXISTS news_piece_table_id_seq CASCADE;
DROP SEQUENCE IF EXISTS news_piece_product_at_shop_id_seq CASCADE;
DROP SEQUENCE IF EXISTS moderator_task_id_seq CASCADE;
