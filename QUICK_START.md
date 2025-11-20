# Quick Start Guide - Soqotra Rock Art Web App

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
cd database-rockart/web-app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env and change SECRET_KEY
```

### 3. Initialize Database
```bash
flask initdb
```

This creates:
- ✅ SQLite database with all tables
- ✅ Default admin user: `admin` / `admin123`
- ✅ Type descriptions (if list_type.xlsx exists)

### 4. Run Application
```bash
python app.py
```

Visit: **http://localhost:5000**

---

## 📦 Deploy to GitHub + Render (FREE)

### Step 1: Push to GitHub

```bash
cd database-rockart/web-app
git init
git add .
git commit -m "Initial commit - Rock Art Web App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rockart-web.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `rockart-database`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free

5. Add PostgreSQL Database:
   - Click "New +" → "PostgreSQL"
   - Name: `rockart-db`
   - Plan: Free
   - Copy the **Internal Database URL**

6. Set Environment Variables in Web Service:
   ```
   FLASK_ENV=production
   SECRET_KEY=generate-a-random-key-here
   ```

7. Deploy and wait for build to complete

8. Initialize database via Render Shell:
   - Go to your web service → "Shell" tab
   - Run: `flask initdb`

9. Done! Your app is live at `https://rockart-database.onrender.com`

---

## 🎯 Key Features

### Authentication
- ✅ Login/Register system
- ✅ Secure password hashing
- ✅ Session management

### Records Management
- ✅ Create/Read/Update/Delete records
- ✅ Search across all fields
- ✅ Pagination for large datasets
- ✅ 8 fields: Site, Motif, Panel, Groups, Type, Date, Description, Coordinates

### Images
- ✅ Upload multiple images per record
- ✅ Automatic thumbnail generation (200x200px)
- ✅ Full-size image viewing
- ✅ Drag & drop support

### Map Visualization
- ✅ Interactive Leaflet.js map
- ✅ GeoJSON markers for all records with coordinates
- ✅ Click markers to view details

### Export
- ✅ Export all records to Excel
- ✅ Embedded thumbnail images in Excel
- ✅ Maintains formatting and row heights

---

## 📊 Default Credentials

**Username:** `admin`
**Password:** `admin123`

⚠️ **IMPORTANT:** Change this password immediately after first login!

---

## 🗂️ Project Structure

```
web-app/
├── app.py              # Main Flask app with all routes
├── models.py           # Database models (User, RockArt, Image, TypeDescription)
├── forms.py            # WTForms (Login, Register, RockArt, ImageUpload)
├── utils.py            # Helper functions (thumbnails, file handling)
├── config.py           # Configuration (dev/prod)
├── requirements.txt    # Dependencies
├── Procfile           # Deployment config
├── runtime.txt        # Python version
├── templates/         # HTML templates (Jinja2 + Bootstrap 5)
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── records.html
│   ├── record_detail.html
│   ├── record_form.html
│   └── map.html
└── static/
    ├── css/style.css  # Custom styles
    ├── js/app.js      # Custom JavaScript
    └── uploads/       # Image storage
```

---

## 🔗 Important URLs

- **Dashboard:** `/`
- **Records List:** `/records`
- **New Record:** `/record/new`
- **Map View:** `/map`
- **Export Excel:** `/export/excel`
- **Login:** `/login`
- **Register:** `/register`

---

## 💡 Tips

### Add Type Descriptions
Place `list_type.xlsx` in `database-rockart/` directory before running `flask initdb`. The file should have:
- Column A: `Type` (rock art type names)
- Column B: `Description` (descriptions)

### Change Admin Password
1. Login as admin
2. (Add user profile page - TODO)
3. Or use Python console:
```python
from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    user.set_password('new_secure_password')
    db.session.commit()
```

### Backup Database
```bash
# SQLite (development)
cp rockart.db rockart_backup.db

# PostgreSQL (production)
# Use Render/Railway backup features
```

---

## 🐛 Troubleshooting

### "No module named 'app'"
```bash
# Make sure you're in web-app directory
cd database-rockart/web-app
```

### Images not uploading
```bash
# Check upload directories exist
mkdir -p static/uploads/originals
mkdir -p static/uploads/thumbnails
```

### Database errors
```bash
# Reset database
rm rockart.db
flask initdb
```

### Port already in use
```bash
# Change port in app.py (last line):
app.run(debug=True, port=5001)
```

---

## 📚 Next Steps

1. ✅ Deploy to Render/Railway
2. ✅ Change default admin password
3. ✅ Import type descriptions from Excel
4. ✅ Create your first record
5. ✅ Upload images
6. ✅ Add coordinates for map visualization
7. ✅ Share the URL with your team!

---

## 🆘 Need Help?

- Check `README.md` for detailed documentation
- Review code comments in `app.py`
- Check Flask documentation: https://flask.palletsprojects.com/
- Bootstrap 5 docs: https://getbootstrap.com/docs/5.3/
- Leaflet.js docs: https://leafletjs.com/

Enjoy your new Rock Art Database! 🎨🗿
