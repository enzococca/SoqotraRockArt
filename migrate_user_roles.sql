-- Database migration script to add user roles and approval system
-- Run this on the production database BEFORE deploying the new code
-- Usage: psql <DATABASE_URL> -f migrate_user_roles.sql

BEGIN;

-- Add is_approved column to users table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='is_approved') THEN
        ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT FALSE NOT NULL;
        CREATE INDEX IF NOT EXISTS ix_users_is_approved ON users(is_approved);
        -- Approve all existing users by default
        UPDATE users SET is_approved = TRUE;
        RAISE NOTICE '✓ Added is_approved column and approved all existing users';
    ELSE
        RAISE NOTICE '✓ Column is_approved already exists';
    END IF;
END$$;

-- Add role column to users table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='role') THEN
        ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'viewer' NOT NULL;
        CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);
        -- Set first user as admin
        UPDATE users SET role = 'admin' WHERE id = (SELECT MIN(id) FROM users);
        RAISE NOTICE '✓ Added role column and set first user as admin';
    ELSE
        RAISE NOTICE '✓ Column role already exists';
    END IF;
END$$;

-- Create orthophotos table if it doesn't exist
CREATE TABLE IF NOT EXISTS orthophotos (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    dropbox_path VARCHAR(500) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    file_size_mb FLOAT,
    bbox_xmin FLOAT,
    bbox_ymin FLOAT,
    bbox_xmax FLOAT,
    bbox_ymax FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on orthophotos
CREATE INDEX IF NOT EXISTS ix_orthophotos_name ON orthophotos(name);
CREATE INDEX IF NOT EXISTS ix_orthophotos_is_active ON orthophotos(is_active);

-- Verify the changes
DO $$
DECLARE
    user_count INTEGER;
    admin_count INTEGER;
    approved_count INTEGER;
    ortho_exists BOOLEAN;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO admin_count FROM users WHERE role = 'admin';
    SELECT COUNT(*) INTO approved_count FROM users WHERE is_approved = TRUE;
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'orthophotos') INTO ortho_exists;

    RAISE NOTICE '';
    RAISE NOTICE '======================================================================';
    RAISE NOTICE 'Migration Summary:';
    RAISE NOTICE '======================================================================';
    RAISE NOTICE 'Total users: %', user_count;
    RAISE NOTICE 'Admin users: %', admin_count;
    RAISE NOTICE 'Approved users: %', approved_count;
    RAISE NOTICE 'Orthophotos table exists: %', ortho_exists;
    RAISE NOTICE '======================================================================';
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE '======================================================================';
END$$;

COMMIT;
