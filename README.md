# Soqotra Rock Art Database - Web Application

A modern web-based database management system for cataloging and managing Soqotra rock art archaeological data, built with Flask and deployed on Render/Railway.

## Features

### Core Functionality
- ✅ **Full CRUD Operations** - Create, read, update, and delete rock art records
- ✅ **User Authentication** - Secure login/registration system with Flask-Login
- ✅ **Image Management** - Upload, store, and display images with automatic thumbnail generation
- ✅ **Advanced Search** - Full-text search across all record fields
- ✅ **Pagination** - Efficient browsing of large datasets
- ✅ **Geospatial Visualization** - Interactive map view with Leaflet.js
- ✅ **Excel Export** - Export records with embedded thumbnails
- ✅ **Responsive Design** - Mobile-friendly Bootstrap 5 interface

### Technical Features
- SQLAlchemy ORM with PostgreSQL (production) / SQLite (development)
- RESTful API endpoints for data access
- Automatic image thumbnail generation with Pillow
- GeoJSON support for mapping
- Type descriptions auto-fill from database
- Secure file uploads with validation
- Session management with Flask-Login

## Installation

### Prerequisites
- Python 3.11+
- pip
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd database-rockart/web-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and set your SECRET_KEY
   ```

5. **Initialize database**
   ```bash
   flask initdb
   ```

   This creates:
   - Database tables
   - Default admin user (username: `admin`, password: `admin123`)
   - Type descriptions (if `list_type.xlsx` exists in parent directory)

6. **Run development server**
   ```bash
   python app.py
   ```

   Application will be available at: `http://localhost:5000`

## Deployment

### Deploy to Render

1. **Create a new Web Service** on [Render](https://render.com)

2. **Connect your GitHub repository**

3. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variables:**
     ```
     FLASK_ENV=production
     SECRET_KEY=your-secure-random-key-here
     ```

4. **Add PostgreSQL database:**
   - Create a new PostgreSQL instance
   - Render will automatically set `DATABASE_URL` environment variable

5. **Initialize database:**
   After first deployment, run in Render Shell:
   ```bash
   flask initdb
   ```

### Deploy to Railway

1. **Create new project** on [Railway](https://railway.app)

2. **Deploy from GitHub** repository

3. **Add PostgreSQL database** (Railway will auto-configure `DATABASE_URL`)

4. **Set environment variables:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secure-random-key-here
   ```

5. **Initialize database:**
   Use Railway's CLI or web console:
   ```bash
   railway run flask initdb
   ```

## Project Structure

```
web-app/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── models.py                 # Database models (SQLAlchemy)
├── forms.py                  # WTForms form definitions
├── utils.py                  # Helper functions
├── requirements.txt          # Python dependencies
├── Procfile                  # Deployment configuration
├── runtime.txt               # Python version specification
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles
│   ├── js/
│   │   └── app.js           # Custom JavaScript
│   └── uploads/
│       ├── originals/       # Full-size images
│       └── thumbnails/      # Thumbnail images (200x200px)
└── templates/
    ├── base.html            # Base template
    ├── login.html           # Login page
    ├── register.html        # Registration page
    ├── index.html           # Dashboard
    ├── records.html         # Records list
    ├── record_detail.html   # Record detail view
    ├── record_form.html     # Create/Edit form
    └── map.html             # Map visualization
```

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - User email
- `password_hash` - Hashed password
- `is_active` - Account status
- `created_at` - Registration timestamp

### RockArt Table
- `id` - Primary key
- `site` - Site identifier (required)
- `motif` - Motif identifier (required)
- `panel` - Panel reference
- `groups` - Groups classification
- `type` - Rock art type
- `date` - Date of record
- `description` - Detailed description
- `latitude` - Geographic latitude
- `longitude` - Geographic longitude
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### Images Table
- `id` - Primary key
- `record_id` - Foreign key to RockArt
- `image_path` - Relative path to original image
- `thumbnail_path` - Relative path to thumbnail
- `original_filename` - Original upload filename
- `uploaded_at` - Upload timestamp

### TypeDescription Table
- `id` - Primary key
- `type_name` - Rock art type name (unique)
- `description` - Type description

## Usage

### Default Credentials
After initialization:
- **Username:** `admin`
- **Password:** `admin123`

**⚠️ Important:** Change the admin password immediately after first login!

### Creating Records
1. Navigate to "New Record" from dashboard or records page
2. Fill in required fields (Site, Motif)
3. Optionally add coordinates for map visualization
4. Select type to auto-fill description (if type descriptions are loaded)
5. Click "Save"

### Uploading Images
1. Open a record detail page
2. Click "Upload" button in Images section
3. Select image file (JPG, PNG, GIF - max 16MB)
4. Thumbnail will be automatically generated

### Map Visualization
- Records with latitude/longitude will appear on the map
- Click markers to view record details
- Map uses OpenStreetMap tiles

### Exporting Data
- Click "Export" button to download Excel file
- File includes all records with embedded thumbnail images
- Images maintain aspect ratio in Excel

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Records
- `GET /records` - List records (with pagination and search)
- `GET /record/<id>` - View record details
- `GET /record/new` - Create record form
- `POST /record/new` - Create record
- `GET /record/<id>/edit` - Edit record form
- `POST /record/<id>/edit` - Update record
- `POST /record/<id>/delete` - Delete record

### Images
- `POST /record/<id>/upload` - Upload image
- `POST /image/<id>/delete` - Delete image

### Map & Export
- `GET /map` - Map view
- `GET /api/records/geojson` - GeoJSON API
- `GET /export/excel` - Export to Excel
- `GET /api/types/<name>/description` - Get type description

## Configuration

### Environment Variables

- `FLASK_ENV` - Set to `production` or `development`
- `SECRET_KEY` - Secret key for sessions (required)
- `DATABASE_URL` - Database connection string (auto-set by hosting)
- `MAX_CONTENT_LENGTH` - Max upload size in bytes (default: 16MB)

### Upload Settings

Configure in `config.py`:
```python
THUMBNAIL_SIZE = (200, 200)  # Thumbnail dimensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
```

### Map Settings

Default center and zoom:
```python
DEFAULT_MAP_CENTER = [12.5, 54.0]  # Soqotra coordinates
DEFAULT_MAP_ZOOM = 10
```

## Migrating Data from Desktop App

To import data from the PyQt5 desktop application:

1. **Export from desktop app** using the Export functionality

2. **Import type descriptions:**
   - Copy `list_type.xlsx` to parent directory
   - Run `flask initdb` to import types

3. **Manual data migration:**
   ```python
   # Connect to old SQLite database
   import sqlite3
   old_conn = sqlite3.connect('path/to/old/rockart.db')

   # Transfer records (write custom migration script)
   # See database-rockart/import_images.py for reference
   ```

## Troubleshooting

### Database initialization fails
```bash
# Drop and recreate database
flask initdb
```

### Images not displaying
- Check that upload directories exist and are writable
- Verify `UPLOAD_FOLDER` path in configuration
- Check file permissions

### PostgreSQL connection issues on Render/Railway
- Ensure `DATABASE_URL` environment variable is set
- Check that URL uses `postgresql://` (not `postgres://`)
- Verify database service is running

## Development

### Running Tests
```bash
pytest  # (when tests are added)
```

### Code Style
```bash
flake8 app.py models.py forms.py utils.py
```

### Database Migrations
For schema changes, use Flask-Migrate (to be added):
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## Technologies Used

- **Backend:** Flask 3.0, SQLAlchemy, Flask-Login
- **Database:** PostgreSQL (production), SQLite (development)
- **Frontend:** Bootstrap 5, Leaflet.js
- **Image Processing:** Pillow
- **Export:** xlsxwriter
- **Geospatial:** GeoPandas
- **Deployment:** Gunicorn, Render/Railway

## License

GNU General Public License v3.0

## Support

For issues or questions, please open an issue on GitHub.

## Roadmap

- [ ] Add database migration system (Flask-Migrate)
- [ ] Implement user roles and permissions
- [ ] Add bulk import/export functionality
- [ ] Support for GeoPackage file upload
- [ ] Translation feature (Google Translator integration)
- [ ] Database synchronization between instances
- [ ] Advanced filtering and sorting
- [ ] RESTful API with authentication
- [ ] Mobile app support
- [ ] PDF export functionality
