#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p static/uploads/originals
mkdir -p static/uploads/thumbnails
mkdir -p static/basemaps

# Initialize database and create admin user
python -c "
from app import app, db, User
with app.app_context():
    # Create tables
    db.create_all()
    print('✅ Database tables created successfully')

    # Create default admin user if not exists
    existing_admin = User.query.filter_by(username='admin').first()
    if not existing_admin:
        admin = User(username='admin', email='admin@soqotra-rockart.org')
        admin.set_password('SoqotraRockArt2025!')
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created successfully')
        print('   Username: admin')
        print('   Password: SoqotraRockArt2025!')
        print('   ⚠️  Please change the password after first login!')
    else:
        print('ℹ️  Admin user already exists')
"

echo "✅ Build completed successfully!"
