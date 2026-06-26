-- ForgeGuard AI — database bootstrap
-- SQLAlchemy handles DDL via Base.metadata.create_all; this file handles
-- any DB-level config needed before the app starts.

-- Ensure the app user has full access
GRANT ALL PRIVILEGES ON DATABASE forgeguard_db TO forgeguard;
