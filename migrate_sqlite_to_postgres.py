#!/usr/bin/env python3
"""
Script to migrate data from local SQLite database to PostgreSQL on Render.

Usage:
    python migrate_sqlite_to_postgres.py <sqlite_db_path> <postgres_url>

Example:
    python migrate_sqlite_to_postgres.py /path/to/rockart.db "postgresql://user:pass@host:5432/dbname"

You can get the PostgreSQL URL from Render dashboard -> Database -> Connection Info -> External Database URL
"""
import sys
import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app import db, User, RockArt, Image, TypeDescription

def connect_sqlite(sqlite_path):
    """Connect to SQLite database."""
    try:
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        print(f"✅ Connected to SQLite: {sqlite_path}")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to SQLite: {e}")
        sys.exit(1)

def connect_postgres(postgres_url):
    """Connect to PostgreSQL database."""
    try:
        engine = create_engine(postgres_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Test connection
        session.execute(text("SELECT 1"))
        print(f"✅ Connected to PostgreSQL")
        return session, engine
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        sys.exit(1)

def migrate_users(sqlite_conn, pg_session):
    """Migrate users table."""
    cursor = sqlite_conn.cursor()

    # Check if users table exists in SQLite
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("ℹ️  No 'users' table in SQLite, skipping user migration")
        return 0

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    migrated = 0
    skipped = 0

    for row in rows:
        try:
            # Check if user already exists
            existing = pg_session.query(User).filter_by(username=row['username']).first()
            if existing:
                print(f"⚠️  User '{row['username']}' already exists, skipping")
                skipped += 1
                continue

            user = User(
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                is_active=row.get('is_active', True),
                created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else datetime.utcnow()
            )
            pg_session.add(user)
            migrated += 1
        except Exception as e:
            print(f"❌ Error migrating user '{row['username']}': {e}")

    pg_session.commit()
    print(f"✅ Migrated {migrated} users ({skipped} skipped)")
    return migrated

def migrate_rockart(sqlite_conn, pg_session):
    """Migrate rockart records."""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM rockart")
    rows = cursor.fetchall()

    migrated = 0
    id_mapping = {}  # Map old IDs to new IDs

    for row in rows:
        try:
            # Check if record already exists (by site and motif)
            existing = pg_session.query(RockArt).filter_by(
                site=row['site'],
                motif=row['motif']
            ).first()

            if existing:
                print(f"⚠️  Record {row['id']} ({row['site']} - {row['motif']}) already exists, skipping")
                id_mapping[row['id']] = existing.id
                continue

            record = RockArt(
                site=row['site'],
                motif=row['motif'],
                panel=row.get('panel'),
                groups=row.get('groups'),
                type=row.get('type'),
                date=datetime.strptime(row['date'], '%Y-%m-%d').date() if row.get('date') else None,
                description=row.get('description'),
                latitude=row.get('latitude'),
                longitude=row.get('longitude'),
                created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else datetime.utcnow(),
                updated_at=datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else datetime.utcnow()
            )
            pg_session.add(record)
            pg_session.flush()  # Get the new ID

            id_mapping[row['id']] = record.id
            migrated += 1

            if migrated % 100 == 0:
                print(f"  ... migrated {migrated} records so far")

        except Exception as e:
            print(f"❌ Error migrating record {row['id']}: {e}")

    pg_session.commit()
    print(f"✅ Migrated {migrated} rock art records")
    return id_mapping

def migrate_images(sqlite_conn, pg_session, id_mapping):
    """Migrate images with updated foreign keys."""
    cursor = sqlite_conn.cursor()

    # Check if images table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
    if not cursor.fetchone():
        print("ℹ️  No 'images' table in SQLite, skipping image migration")
        return 0

    cursor.execute("SELECT * FROM images")
    rows = cursor.fetchall()

    migrated = 0
    skipped = 0

    for row in rows:
        try:
            old_record_id = row['record_id']

            # Map old record_id to new record_id
            if old_record_id not in id_mapping:
                print(f"⚠️  Image {row['id']}: parent record {old_record_id} not found, skipping")
                skipped += 1
                continue

            new_record_id = id_mapping[old_record_id]

            # Check if image already exists
            existing = pg_session.query(Image).filter_by(
                record_id=new_record_id,
                image_path=row['image_path']
            ).first()

            if existing:
                skipped += 1
                continue

            image = Image(
                record_id=new_record_id,
                image_path=row['image_path'],
                thumbnail_path=row['thumbnail_path'],
                original_filename=row.get('original_filename'),
                uploaded_at=datetime.fromisoformat(row['uploaded_at']) if row.get('uploaded_at') else datetime.utcnow()
            )
            pg_session.add(image)
            migrated += 1

            if migrated % 100 == 0:
                print(f"  ... migrated {migrated} images so far")

        except Exception as e:
            print(f"❌ Error migrating image {row['id']}: {e}")

    pg_session.commit()
    print(f"✅ Migrated {migrated} images ({skipped} skipped)")
    return migrated

def migrate_type_descriptions(sqlite_conn, pg_session):
    """Migrate type descriptions."""
    cursor = sqlite_conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='type_descriptions'")
    if not cursor.fetchone():
        print("ℹ️  No 'type_descriptions' table in SQLite, skipping")
        return 0

    cursor.execute("SELECT * FROM type_descriptions")
    rows = cursor.fetchall()

    migrated = 0

    for row in rows:
        try:
            # Check if type already exists
            existing = pg_session.query(TypeDescription).filter_by(
                type_name=row['type_name']
            ).first()

            if existing:
                continue

            type_desc = TypeDescription(
                type_name=row['type_name'],
                description=row.get('description')
            )
            pg_session.add(type_desc)
            migrated += 1
        except Exception as e:
            print(f"❌ Error migrating type '{row['type_name']}': {e}")

    pg_session.commit()
    print(f"✅ Migrated {migrated} type descriptions")
    return migrated

def main():
    if len(sys.argv) < 3:
        print("Usage: python migrate_sqlite_to_postgres.py <sqlite_db_path> <postgres_url>")
        print("\nExample:")
        print('  python migrate_sqlite_to_postgres.py ./rockart.db "postgresql://user:pass@host:5432/dbname"')
        print("\nGet PostgreSQL URL from: Render Dashboard → Database → Connection Info → External Database URL")
        sys.exit(1)

    sqlite_path = sys.argv[1]
    postgres_url = sys.argv[2]

    print("=" * 70)
    print("🔄 Starting Migration from SQLite to PostgreSQL")
    print("=" * 70)
    print(f"Source: {sqlite_path}")
    print(f"Target: {postgres_url[:30]}...{postgres_url[-20:]}")
    print()

    # Connect to databases
    sqlite_conn = connect_sqlite(sqlite_path)
    pg_session, pg_engine = connect_postgres(postgres_url)

    # Create tables in PostgreSQL if they don't exist
    print("\n📋 Creating tables in PostgreSQL (if needed)...")
    try:
        db.metadata.create_all(pg_engine)
        print("✅ Tables ready")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("Starting data migration...")
    print("=" * 70)

    # Migrate in order (respecting foreign keys)
    print("\n1️⃣  Migrating Users...")
    users_count = migrate_users(sqlite_conn, pg_session)

    print("\n2️⃣  Migrating Rock Art Records...")
    id_mapping = migrate_rockart(sqlite_conn, pg_session)

    print("\n3️⃣  Migrating Images...")
    images_count = migrate_images(sqlite_conn, pg_session, id_mapping)

    print("\n4️⃣  Migrating Type Descriptions...")
    types_count = migrate_type_descriptions(sqlite_conn, pg_session)

    # Summary
    print("\n" + "=" * 70)
    print("✅ Migration completed successfully!")
    print("=" * 70)
    print(f"📊 Summary:")
    print(f"   - Users:           {users_count}")
    print(f"   - Rock Art Records: {len(id_mapping)}")
    print(f"   - Images:          {images_count}")
    print(f"   - Type Descriptions: {types_count}")
    print("=" * 70)

    # Close connections
    sqlite_conn.close()
    pg_session.close()

    print("\n✅ All done! You can now deploy your application on Render.")
    print("   The data is now in your PostgreSQL database.")

if __name__ == '__main__':
    main()
