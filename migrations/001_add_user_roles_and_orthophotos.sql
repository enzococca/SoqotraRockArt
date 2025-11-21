-- Migration: Add user roles, approval system, and orthophotos table
-- Execute this on Render PostgreSQL database

-- ============================================================================
-- 1. ADD USER ROLES AND APPROVAL SYSTEM
-- ============================================================================

-- Add new columns to users table
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'viewer';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_approved ON users(is_approved);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Set first user as approved admin (change ID if needed)
UPDATE users SET is_approved = TRUE, role = 'admin' WHERE id = (SELECT MIN(id) FROM users);

-- ============================================================================
-- 2. CREATE ORTHOPHOTOS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS orthophotos (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    dropbox_path VARCHAR(500) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    file_size_mb FLOAT,

    -- Optional bounding box metadata
    bbox_xmin FLOAT,
    bbox_ymin FLOAT,
    bbox_xmax FLOAT,
    bbox_ymax FLOAT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_orthophotos_name ON orthophotos(name);
CREATE INDEX IF NOT EXISTS idx_orthophotos_active ON orthophotos(is_active);

-- Insert default orthophoto (SHP042)
INSERT INTO orthophotos (name, dropbox_path, description, is_active, file_size_mb)
VALUES (
    'SHP042 - Rock Art Site',
    '/Soqotra/tiles/orthophoto_shp042_final.tif',
    'High-resolution orthophoto of SHP042 rock art site with motifs',
    TRUE,
    32.9
)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES (run these to check migration success)
-- ============================================================================

-- Check users table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Check admin user
SELECT id, username, email, is_approved, role FROM users WHERE role = 'admin';

-- Check orthophotos table
SELECT * FROM orthophotos;
