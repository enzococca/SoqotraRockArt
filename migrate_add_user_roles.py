#!/usr/bin/env python3
"""
Database migration script to add user roles and approval system.

This script adds:
1. is_approved column to users table
2. role column to users table
3. Creates orthophotos table if it doesn't exist

Run this on the production database BEFORE deploying the new code.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

def run_migration(database_url):
    """Run the migration to add user roles."""

    print("=" * 70)
    print("Database Migration: Adding User Roles and Approval System")
    print("=" * 70)

    engine = create_engine(database_url)
    inspector = inspect(engine)

    with engine.connect() as conn:
        # Check if users table exists
        if 'users' not in inspector.get_table_names():
            print("ERROR: users table does not exist!")
            return False

        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"\nExisting columns in users table: {existing_columns}")

        # Add is_approved column if it doesn't exist
        if 'is_approved' not in existing_columns:
            print("\n1. Adding 'is_approved' column...")
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN is_approved BOOLEAN DEFAULT FALSE NOT NULL
            """))
            print("   ✓ Added is_approved column")

            # Create index
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_is_approved
                ON users(is_approved)
            """))
            print("   ✓ Created index on is_approved")

            # Approve all existing users by default
            conn.execute(text("""
                UPDATE users SET is_approved = TRUE
            """))
            print("   ✓ Approved all existing users")
        else:
            print("\n1. Column 'is_approved' already exists - skipping")

        # Add role column if it doesn't exist
        if 'role' not in existing_columns:
            print("\n2. Adding 'role' column...")
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN role VARCHAR(20) DEFAULT 'viewer' NOT NULL
            """))
            print("   ✓ Added role column")

            # Create index
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_role
                ON users(role)
            """))
            print("   ✓ Created index on role")

            # Set first user as admin
            result = conn.execute(text("""
                UPDATE users
                SET role = 'admin'
                WHERE id = (SELECT MIN(id) FROM users)
                RETURNING username
            """))
            admin_user = result.fetchone()
            if admin_user:
                print(f"   ✓ Set user '{admin_user[0]}' as admin")
        else:
            print("\n2. Column 'role' already exists - skipping")

        # Create orthophotos table if it doesn't exist
        if 'orthophotos' not in inspector.get_table_names():
            print("\n3. Creating 'orthophotos' table...")
            conn.execute(text("""
                CREATE TABLE orthophotos (
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
                )
            """))
            print("   ✓ Created orthophotos table")

            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_orthophotos_name
                ON orthophotos(name)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_orthophotos_is_active
                ON orthophotos(is_active)
            """))
            print("   ✓ Created indexes on orthophotos")
        else:
            print("\n3. Table 'orthophotos' already exists - skipping")

        conn.commit()

    print("\n" + "=" * 70)
    print("Migration completed successfully!")
    print("=" * 70)
    return True


if __name__ == '__main__':
    # Get database URL from environment or command line
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
    else:
        database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("ERROR: No database URL provided!")
        print("\nUsage:")
        print("  python migrate_add_user_roles.py <database_url>")
        print("  or set DATABASE_URL environment variable")
        sys.exit(1)

    # Handle Render's postgres:// vs postgresql:// URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print(f"Connecting to database...")
    print(f"URL: {database_url[:50]}...")

    success = run_migration(database_url)
    sys.exit(0 if success else 1)
