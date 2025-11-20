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

# Initialize database (if needed)
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database tables created successfully')
"

echo "✅ Build completed successfully!"
