"""
Main Flask application for Rock Art Database Manager.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import xlsxwriter
from io import BytesIO
from threading import Lock

from config import config
from models import db, User, RockArt, Image, TypeDescription
from forms import LoginForm, RegistrationForm, RockArtForm, ImageUploadForm, SearchForm
from utils import save_uploaded_image, delete_image_files, import_type_descriptions_from_excel

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Debug: Print Dropbox configuration at startup
print("=" * 70)
print("DROPBOX CONFIGURATION AT STARTUP")
print("=" * 70)
print(f"Environment: {env}")
print(f"USE_DROPBOX: {app.config.get('USE_DROPBOX', 'NOT SET')}")
print(f"DROPBOX_ACCESS_TOKEN: {'SET' if app.config.get('DROPBOX_ACCESS_TOKEN') else 'NOT SET'} ({len(app.config.get('DROPBOX_ACCESS_TOKEN', ''))} chars)")
print(f"DROPBOX_ORIGINAL_FOLDER: {app.config.get('DROPBOX_ORIGINAL_FOLDER', 'NOT SET')}")
print(f"DROPBOX_THUMBNAIL_FOLDER: {app.config.get('DROPBOX_THUMBNAIL_FOLDER', 'NOT SET')}")
print("=" * 70)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Dropbox link cache (in-memory cache for temporary links)
# Format: {filename: {'url': 'https://...', 'expires': datetime}}
_dropbox_link_cache = {}
_cache_lock = Lock()


def get_dropbox_temporary_link(dropbox_path):
    """
    Get a temporary link from Dropbox API with caching.

    Args:
        dropbox_path: Full path in Dropbox like '/Soqotra/ROCKART DATABASE/original_images/file.jpg'

    Returns:
        Temporary download URL (valid for 4 hours) or None if failed
    """
    # Check cache first
    with _cache_lock:
        if dropbox_path in _dropbox_link_cache:
            cached = _dropbox_link_cache[dropbox_path]
            if cached['expires'] > datetime.now():
                return cached['url']
            else:
                # Expired, remove from cache
                del _dropbox_link_cache[dropbox_path]

    # Generate new temporary link
    try:
        import dropbox
        dbx = dropbox.Dropbox(app.config['DROPBOX_ACCESS_TOKEN'])

        # Get temporary link (valid for 4 hours)
        result = dbx.files_get_temporary_link(dropbox_path)
        temp_url = result.link

        # Cache the link (expires in 3 hours to be safe)
        with _cache_lock:
            _dropbox_link_cache[dropbox_path] = {
                'url': temp_url,
                'expires': datetime.now() + timedelta(seconds=app.config['DROPBOX_LINK_CACHE_TIMEOUT'])
            }

        return temp_url

    except Exception as e:
        # Log error and return None to fallback to local
        print(f"Dropbox API Error for {dropbox_path}: {str(e)}")
        return None


def get_image_url(image_path):
    """
    Convert local image path to Dropbox URL if USE_DROPBOX is enabled.

    Args:
        image_path: Path like 'original_images\\_DSC3341.JPG' or 'thumbnails\\thumb__DSC3341.JPG'

    Returns:
        Full URL to image (Dropbox if enabled, otherwise local static URL)
    """
    if not image_path:
        return None

    # Debug logging
    use_dropbox = app.config.get('USE_DROPBOX', False)
    print(f"[get_image_url] USE_DROPBOX={use_dropbox}, path={image_path}")

    # If Dropbox is not enabled, return local static URL
    if not use_dropbox:
        # Convert backslash to forward slash for web URLs
        web_path = image_path.replace('\\', '/')
        print(f"[get_image_url] Returning static URL: {web_path}")
        return url_for('static', filename=web_path)

    # Extract filename from path (handle both / and \ separators)
    normalized_path = image_path.replace('\\', '/')
    filename = normalized_path.split('/')[-1]

    # Determine which Dropbox folder based on path
    # If path contains 'thumbnails', use thumbnail folder, otherwise use original folder
    if 'thumbnails' in normalized_path.lower():
        dropbox_folder = app.config['DROPBOX_THUMBNAIL_FOLDER']
    else:
        dropbox_folder = app.config['DROPBOX_ORIGINAL_FOLDER']

    # Construct full Dropbox path
    dropbox_path = f"{dropbox_folder}/{filename}"

    # Get temporary link from Dropbox API
    temp_url = get_dropbox_temporary_link(dropbox_path)

    if temp_url:
        # Use Markup to prevent HTML escaping
        from markupsafe import Markup
        print(f"[get_image_url] Successfully generated Dropbox URL for {filename}")
        return Markup(temp_url)
    else:
        # Fallback to local static URL if Dropbox API fails
        web_path = image_path.replace('\\', '/')
        print(f"[get_image_url] Dropbox API failed, falling back to static URL: {web_path}")
        return url_for('static', filename=web_path)


# Register Jinja2 filter
app.jinja_env.filters['image_url'] = get_image_url


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash(f'Welcome back, {user.username}!', 'success')

        # Redirect to next page or index
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logout current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
@login_required
def index():
    """Home page with dashboard."""
    total_records = RockArt.query.count()
    total_images = Image.query.count()
    recent_records = RockArt.query.order_by(RockArt.created_at.desc()).limit(5).all()

    return render_template('index.html',
                           total_records=total_records,
                           total_images=total_images,
                           recent_records=recent_records)


@app.route('/records')
@login_required
def records():
    """List all rock art records with pagination and search."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '', type=str)

    query = RockArt.query

    # Apply search filter if query exists
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            db.or_(
                RockArt.site.like(search_pattern),
                RockArt.motif.like(search_pattern),
                RockArt.panel.like(search_pattern),
                RockArt.groups.like(search_pattern),
                RockArt.type.like(search_pattern),
                RockArt.description.like(search_pattern)
            )
        )

    # Paginate results
    pagination = query.order_by(RockArt.created_at.desc()).paginate(
        page=page,
        per_page=app.config['RECORDS_PER_PAGE'],
        error_out=False
    )

    return render_template('records.html',
                           records=pagination.items,
                           pagination=pagination,
                           search_query=search_query)


@app.route('/record/<int:record_id>')
@login_required
def record_detail(record_id):
    """View detailed information about a specific record."""
    record = RockArt.query.get_or_404(record_id)
    return render_template('record_detail.html', record=record)


@app.route('/record/new', methods=['GET', 'POST'])
@login_required
def record_create():
    """Create a new rock art record."""
    form = RockArtForm()

    # Populate type choices
    types = TypeDescription.query.all()
    form.type.choices = [('', '-- Select Type --')] + [(t.type_name, t.type_name) for t in types]

    if form.validate_on_submit():
        record = RockArt(
            site=form.site.data,
            motif=form.motif.data,
            panel=form.panel.data,
            groups=form.groups.data,
            type=form.type.data,
            date=form.date.data,
            description=form.description.data
        )

        # Parse coordinates if provided
        if form.latitude.data and form.longitude.data:
            try:
                record.latitude = float(form.latitude.data)
                record.longitude = float(form.longitude.data)
            except ValueError:
                flash('Invalid coordinates format', 'warning')

        db.session.add(record)
        db.session.commit()

        flash('Record created successfully!', 'success')
        return redirect(url_for('record_detail', record_id=record.id))

    return render_template('record_form.html', form=form, title='New Record')


@app.route('/record/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def record_edit(record_id):
    """Edit an existing rock art record."""
    record = RockArt.query.get_or_404(record_id)
    form = RockArtForm(obj=record)

    # Populate type choices
    types = TypeDescription.query.all()
    form.type.choices = [('', '-- Select Type --')] + [(t.type_name, t.type_name) for t in types]

    if form.validate_on_submit():
        record.site = form.site.data
        record.motif = form.motif.data
        record.panel = form.panel.data
        record.groups = form.groups.data
        record.type = form.type.data
        record.date = form.date.data
        record.description = form.description.data

        # Parse coordinates if provided
        if form.latitude.data and form.longitude.data:
            try:
                record.latitude = float(form.latitude.data)
                record.longitude = float(form.longitude.data)
            except ValueError:
                flash('Invalid coordinates format', 'warning')

        db.session.commit()
        flash('Record updated successfully!', 'success')
        return redirect(url_for('record_detail', record_id=record.id))

    # Pre-populate coordinate fields
    if request.method == 'GET':
        if record.latitude:
            form.latitude.data = str(record.latitude)
        if record.longitude:
            form.longitude.data = str(record.longitude)

    return render_template('record_form.html', form=form, title='Edit Record', record=record)


@app.route('/record/<int:record_id>/delete', methods=['POST'])
@login_required
def record_delete(record_id):
    """Delete a rock art record and all associated images."""
    record = RockArt.query.get_or_404(record_id)

    # Delete all associated images from filesystem
    for image in record.images:
        delete_image_files(image.image_path, image.thumbnail_path)

    # Delete record (cascade will delete image records)
    db.session.delete(record)
    db.session.commit()

    flash('Record deleted successfully!', 'success')
    return redirect(url_for('records'))


# ============================================================================
# IMAGE ROUTES
# ============================================================================

@app.route('/record/<int:record_id>/upload', methods=['POST'])
@login_required
def image_upload(record_id):
    """Upload image to a record."""
    record = RockArt.query.get_or_404(record_id)

    if 'image' not in request.files:
        if request.is_json:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        flash('No file selected', 'danger')
        return redirect(url_for('record_detail', record_id=record_id))

    file = request.files['image']

    if file.filename == '':
        if request.is_json:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        flash('No file selected', 'danger')
        return redirect(url_for('record_detail', record_id=record_id))

    # Save image and create thumbnail
    original_path, thumbnail_path, original_filename = save_uploaded_image(file, record_id)

    if original_path and thumbnail_path:
        # Create image record
        image = Image(
            record_id=record_id,
            image_path=original_path,
            thumbnail_path=thumbnail_path,
            original_filename=original_filename
        )
        db.session.add(image)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'image_id': image.id})
        flash('Image uploaded successfully!', 'success')
    else:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error uploading image'}), 500
        flash('Error uploading image', 'danger')

    return redirect(url_for('record_detail', record_id=record_id))


@app.route('/image/<int:image_id>/delete', methods=['POST'])
@login_required
def image_delete(image_id):
    """Delete an image."""
    image = Image.query.get_or_404(image_id)
    record_id = image.record_id

    # Delete files from filesystem
    delete_image_files(image.image_path, image.thumbnail_path)

    # Delete database record
    db.session.delete(image)
    db.session.commit()

    flash('Image deleted successfully!', 'success')
    return redirect(url_for('record_detail', record_id=record_id))


@app.route('/image/<int:image_id>/view')
@login_required
def image_view(image_id):
    """View image with magnifier and screenshot capability."""
    image = Image.query.get_or_404(image_id)
    record = image.record
    return render_template('image_viewer.html', image=image, record=record)


# ============================================================================
# MAP ROUTES
# ============================================================================
# Map view moved to COG integration section below (line ~1152)
# Using new implementation with COG orthophoto support


@app.route('/viewer')
def public_viewer():
    """Public viewer accessible without login."""
    # Get all records with coordinates
    records = RockArt.query.filter(
        RockArt.latitude.isnot(None),
        RockArt.longitude.isnot(None)
    ).all()

    # Convert to GeoJSON
    features = []
    for record in records:
        # Get first image thumbnail URL if exists
        thumbnail_url = get_image_url(record.images[0].thumbnail_path) if record.images else None

        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [record.longitude, record.latitude]
            },
            'properties': {
                'id': record.id,
                'site': record.site,
                'motif': record.motif,
                'panel': record.panel,
                'groups': record.groups,
                'type': record.type,
                'date': record.date.strftime('%Y-%m-%d') if record.date else None,
                'description': record.description,
                'image_count': len(record.images),
                'thumbnail': thumbnail_url
            }
        })

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    # Check for basemap
    basemap_path = Path(app.static_folder) / 'basemaps' / 'soqotra.tif'
    has_basemap = basemap_path.exists()

    return render_template('public_viewer.html', geojson=geojson, has_basemap=has_basemap)


@app.route('/api/records/geojson')
@login_required
def api_records_geojson():
    """API endpoint returning records as GeoJSON."""
    records = RockArt.query.filter(
        RockArt.latitude.isnot(None),
        RockArt.longitude.isnot(None)
    ).all()

    features = []
    for record in records:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [record.longitude, record.latitude]
            },
            'properties': record.to_dict()
        })

    return jsonify({
        'type': 'FeatureCollection',
        'features': features
    })


# ============================================================================
# GEOPACKAGE UPLOAD
# ============================================================================

@app.route('/upload/geopackage', methods=['GET', 'POST'])
@login_required
def upload_geopackage():
    """Upload GeoPackage file to import coordinates."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_geopackage'))

        file = request.files['file']

        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_geopackage'))

        if not file.filename.endswith('.gpkg'):
            flash('Only GeoPackage (.gpkg) files are supported', 'danger')
            return redirect(url_for('upload_geopackage'))

        try:
            import geopandas as gpd
            import tempfile

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.gpkg') as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name

            # Read GeoPackage
            gdf = gpd.read_file(tmp_path)

            # Reproject to WGS84 (EPSG:4326) if needed
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            # Import coordinates
            imported = 0
            updated = 0
            errors = []

            for idx, row in gdf.iterrows():
                # Try to match by PtID, ptd, or motif field
                pt_id = row.get('PtID') or row.get('ptd') or row.get('motif') or row.get('Motif')
                site = row.get('site') or row.get('Site')

                if not pt_id:
                    continue

                # Find matching record
                record = RockArt.query.filter_by(motif=pt_id).first()

                if record:
                    # Extract coordinates (WGS84)
                    if hasattr(row.geometry, 'x') and hasattr(row.geometry, 'y'):
                        record.longitude = row.geometry.x  # Longitude first
                        record.latitude = row.geometry.y   # Latitude second
                        if site:
                            record.site = site
                        updated += 1
                else:
                    # Create new record
                    if site and hasattr(row.geometry, 'x'):
                        new_record = RockArt(
                            site=site,
                            motif=pt_id,
                            longitude=row.geometry.x,
                            latitude=row.geometry.y
                        )
                        db.session.add(new_record)
                        imported += 1

            db.session.commit()

            # Clean up
            os.unlink(tmp_path)

            flash(f'GeoPackage imported! {imported} new records, {updated} updated with coordinates.', 'success')
            return redirect(url_for('map_view'))

        except Exception as e:
            flash(f'Error importing GeoPackage: {str(e)}', 'danger')
            return redirect(url_for('upload_geopackage'))

    return render_template('upload_geopackage.html')


@app.route('/upload/basemap', methods=['GET', 'POST'])
@login_required
def upload_basemap():
    """Upload basemap (GeoTIFF, GeoPackage, or georeferenced image)."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_basemap'))

        file = request.files['file']

        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_basemap'))

        # Check file extension
        allowed = {'.tif', '.tiff', '.gpkg', '.jpg', '.jpeg', '.png'}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed:
            flash('Unsupported file format. Use: TIFF, GeoPackage, JPG, or PNG', 'danger')
            return redirect(url_for('upload_basemap'))

        try:
            # Create basemaps directory
            basemap_dir = Path(app.static_folder) / 'basemaps'
            basemap_dir.mkdir(parents=True, exist_ok=True)

            # Save as soqotra.tif (or appropriate extension)
            target_filename = f'soqotra{file_ext}'
            basemap_path = basemap_dir / target_filename

            # Backup existing if present
            if basemap_path.exists():
                backup_path = basemap_dir / f'soqotra_backup{file_ext}'
                basemap_path.rename(backup_path)

            file.save(basemap_path)

            flash(f'Basemap "{file.filename}" uploaded successfully!', 'success')
            return redirect(url_for('map_view'))

        except Exception as e:
            flash(f'Error uploading basemap: {str(e)}', 'danger')
            return redirect(url_for('upload_basemap'))

    return render_template('upload_basemap.html')


# ============================================================================
# EXPORT ROUTES
# ============================================================================

@app.route('/export/excel')
@login_required
def export_excel():
    """Export all records to Excel with thumbnails."""
    # Create in-memory output file
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Rock Art Records')

    # Formats
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2'})
    text_format = workbook.add_format({'text_wrap': True, 'valign': 'vcenter'})

    # Set column widths
    worksheet.set_column('A:A', 8)   # ID
    worksheet.set_column('B:B', 15)  # Site
    worksheet.set_column('C:C', 15)  # Motif
    worksheet.set_column('D:D', 12)  # Panel
    worksheet.set_column('E:E', 12)  # Groups
    worksheet.set_column('F:F', 20)  # Type
    worksheet.set_column('G:G', 12)  # Date
    worksheet.set_column('H:H', 40)  # Description
    worksheet.set_column('I:I', 30)  # Thumbnail

    # Write headers
    headers = ['ID', 'Site', 'Motif', 'Panel', 'Groups', 'Type', 'Date', 'Description', 'Thumbnail']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Write data
    row_num = 1
    records = RockArt.query.order_by(RockArt.id).all()

    for record in records:
        if record.images:
            # One row per image
            for image in record.images:
                # Write record data
                worksheet.write(row_num, 0, record.id)
                worksheet.write(row_num, 1, record.site or '')
                worksheet.write(row_num, 2, record.motif or '')
                worksheet.write(row_num, 3, record.panel or '')
                worksheet.write(row_num, 4, record.groups or '')
                worksheet.write(row_num, 5, record.type or '')
                worksheet.write(row_num, 6, record.date.strftime('%Y-%m-%d') if record.date else '')
                worksheet.write(row_num, 7, record.description or '', text_format)

                # Insert thumbnail if it exists
                thumbnail_path = Path(app.static_folder) / image.thumbnail_path
                if thumbnail_path.exists():
                    worksheet.set_row(row_num, 150)  # Set row height for image
                    try:
                        worksheet.insert_image(row_num, 8, str(thumbnail_path),
                                               {'x_scale': 0.75, 'y_scale': 0.75})
                    except Exception as e:
                        print(f"Error inserting image: {e}")

                row_num += 1
        else:
            # Record without images
            worksheet.write(row_num, 0, record.id)
            worksheet.write(row_num, 1, record.site or '')
            worksheet.write(row_num, 2, record.motif or '')
            worksheet.write(row_num, 3, record.panel or '')
            worksheet.write(row_num, 4, record.groups or '')
            worksheet.write(row_num, 5, record.type or '')
            worksheet.write(row_num, 6, record.date.strftime('%Y-%m-%d') if record.date else '')
            worksheet.write(row_num, 7, record.description or '', text_format)
            row_num += 1

    workbook.close()
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'rockart_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )


@app.route('/record/<int:record_id>/export/pdf')
@login_required
def export_record_pdf(record_id):
    """Export single record to PDF with images."""
    record = RockArt.query.get_or_404(record_id)

    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        # Create PDF
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0d6efd'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"{record.site} - {record.motif}", title_style))
        story.append(Spacer(1, 0.3*inch))

        # Record data table
        data = [
            ['Field', 'Value'],
            ['ID', str(record.id)],
            ['Site', record.site or '-'],
            ['Motif', record.motif or '-'],
            ['Panel', record.panel or '-'],
            ['Groups', record.groups or '-'],
            ['Type', record.type or '-'],
            ['Date', record.date.strftime('%Y-%m-%d') if record.date else '-'],
        ]

        if record.latitude and record.longitude:
            data.append(['Coordinates', f"{record.latitude:.6f}, {record.longitude:.6f}"])

        t = Table(data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))

        # Description
        if record.description:
            story.append(Paragraph('<b>Description:</b>', styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(record.description, styles['BodyText']))
            story.append(Spacer(1, 0.3*inch))

        # Images
        if record.images:
            story.append(Paragraph(f'<b>Images ({len(record.images)}):</b>', styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))

            for img in record.images:
                img_path = Path(app.static_folder) / img.image_path
                if img_path.exists():
                    try:
                        rl_img = RLImage(str(img_path), width=5*inch, height=3.5*inch)
                        story.append(rl_img)
                        story.append(Paragraph(f'<i>{img.original_filename}</i>', styles['Italic']))
                        story.append(Spacer(1, 0.2*inch))
                    except:
                        pass

        # Build PDF
        doc.build(story)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{record.site}_{record.motif}.pdf'
        )

    except ImportError:
        flash('PDF export requires reportlab library. Please install it.', 'warning')
        return redirect(url_for('record_detail', record_id=record_id))
    except Exception as e:
        flash(f'Error creating PDF: {str(e)}', 'danger')
        return redirect(url_for('record_detail', record_id=record_id))


@app.route('/record/<int:record_id>/print')
@login_required
def print_record(record_id):
    """Print-friendly view of record."""
    record = RockArt.query.get_or_404(record_id)
    return render_template('record_print.html', record=record)


# ============================================================================
# TRANSLATION ROUTES
# ============================================================================

@app.route('/record/<int:record_id>/translate', methods=['POST'])
@login_required
def translate_record(record_id):
    """Translate record description."""
    record = RockArt.query.get_or_404(record_id)

    target_lang = request.form.get('target_lang', 'it')  # Default to Italian

    if not record.description:
        flash('No description to translate', 'warning')
        return redirect(url_for('record_detail', record_id=record_id))

    try:
        from deep_translator import GoogleTranslator

        # Detect source language and translate
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(record.description)

        # Append translation to description
        record.description = f"{record.description}\n\n--- Translation ({target_lang}) ---\n{translated}"
        db.session.commit()

        flash(f'Translation added successfully!', 'success')
    except Exception as e:
        flash(f'Translation error: {str(e)}', 'danger')

    return redirect(url_for('record_detail', record_id=record_id))


# ============================================================================
# DATABASE MANAGEMENT ROUTES
# ============================================================================

@app.route('/databases')
@login_required
def list_databases():
    """List all available databases."""
    db_dir = Path(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '').replace('/rockart.db', ''))
    databases = []

    if db_dir.exists():
        for db_file in db_dir.glob('*.db'):
            databases.append({
                'name': db_file.name,
                'path': str(db_file),
                'size': db_file.stat().st_size,
                'modified': datetime.fromtimestamp(db_file.stat().st_mtime)
            })

    return render_template('databases.html', databases=databases)


@app.route('/database/switch', methods=['POST'])
@login_required
def switch_database():
    """Switch to a different database."""
    db_name = request.form.get('db_name')

    if not db_name:
        flash('No database specified', 'danger')
        return redirect(url_for('list_databases'))

    try:
        import shutil

        current_db_name = 'rockart.db'
        current_db_path = Path(app.root_path) / current_db_name
        new_db_path = Path(app.root_path) / db_name

        if not new_db_path.exists():
            flash(f'Database "{db_name}" not found', 'danger')
            return redirect(url_for('list_databases'))

        # Backup current database
        if current_db_path.exists():
            backup_name = f'{current_db_name}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            backup_path = Path(app.root_path) / backup_name
            shutil.copy2(current_db_path, backup_path)
            flash(f'Current database backed up as: {backup_name}', 'info')

        # Replace with new database
        shutil.copy2(new_db_path, current_db_path)

        flash(f'Switched to database: {db_name}. Please refresh and login with the new database credentials.', 'success')
        return redirect(url_for('logout'))

    except Exception as e:
        flash(f'Error switching database: {str(e)}', 'danger')
        return redirect(url_for('list_databases'))


@app.route('/database/upload', methods=['GET', 'POST'])
@login_required
def upload_database():
    """Upload an existing database file."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_database'))

        file = request.files['file']

        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_database'))

        if not file.filename.endswith('.db'):
            flash('Only .db files are supported', 'danger')
            return redirect(url_for('upload_database'))

        try:
            # Save uploaded database
            filename = secure_filename(file.filename)
            db_path = Path(app.root_path) / filename
            make_active = request.form.get('make_active') == '1'

            if db_path.exists() and not make_active:
                flash(f'Database "{filename}" already exists. Please rename it.', 'warning')
                return redirect(url_for('upload_database'))

            file.save(db_path)

            # If user wants to make this database active
            if make_active:
                current_db_name = 'rockart.db'  # Default database name
                current_db_path = Path(app.root_path) / current_db_name

                # Backup current database if it exists
                if current_db_path.exists():
                    import shutil
                    from datetime import datetime
                    backup_name = f'{current_db_name}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                    backup_path = Path(app.root_path) / backup_name
                    shutil.copy2(current_db_path, backup_path)
                    flash(f'Current database backed up as: {backup_name}', 'info')

                # Replace current database with uploaded one
                import shutil
                shutil.copy2(db_path, current_db_path)

                flash(f'Database "{filename}" uploaded and activated! Please refresh the page and login with the new database credentials.', 'success')
                return redirect(url_for('logout'))  # Force logout to refresh session
            else:
                flash(f'Database "{filename}" uploaded successfully!', 'success')
                return redirect(url_for('list_databases'))

        except Exception as e:
            flash(f'Error uploading database: {str(e)}', 'danger')
            return redirect(url_for('upload_database'))

    return render_template('upload_database.html')


@app.route('/database/create', methods=['GET', 'POST'])
@login_required
def create_database():
    """Create a new empty database."""
    if request.method == 'POST':
        db_name = request.form.get('db_name')

        if not db_name:
            flash('Database name is required', 'danger')
            return redirect(url_for('create_database'))

        # Sanitize filename
        db_name = secure_filename(db_name)
        if not db_name.endswith('.db'):
            db_name += '.db'

        db_path = Path(app.root_path) / db_name

        if db_path.exists():
            flash('Database already exists', 'warning')
            return redirect(url_for('create_database'))

        try:
            # Create new database with same schema
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rockart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site TEXT NOT NULL,
                    motif TEXT NOT NULL,
                    panel TEXT,
                    groups TEXT,
                    type TEXT,
                    date DATE,
                    description TEXT,
                    latitude REAL,
                    longitude REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    thumbnail_path TEXT NOT NULL,
                    original_filename TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (record_id) REFERENCES rockart(id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS type_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            ''')

            conn.commit()
            conn.close()

            flash(f'Database "{db_name}" created successfully!', 'success')
            return redirect(url_for('list_databases'))

        except Exception as e:
            flash(f'Error creating database: {str(e)}', 'danger')
            return redirect(url_for('create_database'))

    return render_template('create_database.html')


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/types/<type_name>/description')
@login_required
def api_type_description(type_name):
    """Get description for a specific type."""
    type_desc = TypeDescription.query.filter_by(type_name=type_name).first()
    if type_desc:
        return jsonify({'description': type_desc.description})
    return jsonify({'description': ''}), 404


# ============================================================================
# MAP AND COG ENDPOINTS
# ============================================================================

@app.route('/map')
@login_required
def map_view():
    """Display map with COG orthophoto and rock art points."""
    return render_template('map.html', title='Map View')


@app.route('/map-simple')
@login_required
def map_simple():
    """Display simple map without COG (for debugging)."""
    return render_template('map_simple.html', title='Map View (Simple)')


@app.route('/api/cog-url')
def get_cog_url():
    """Return COG URL from Dropbox."""
    # For now, use direct Dropbox link (will be configurable via env var)
    cog_url = os.getenv('DROPBOX_COG_URL')

    if not cog_url:
        # Fallback: try to get temporary Dropbox link
        try:
            if os.getenv('USE_DROPBOX') == 'true':
                dropbox_path = '/tiles/orthophoto_shp042_cog.tif'
                temp_link = get_dropbox_temporary_link(dropbox_path)
                if temp_link:
                    return jsonify({'url': temp_link})
        except Exception as e:
            print(f"Error getting COG URL: {e}")

        return jsonify({'error': 'COG URL not configured'}), 500

    return jsonify({'url': cog_url})


@app.route('/api/points')
def get_points():
    """Return all rock art points with coordinates as GeoJSON."""
    records = RockArt.query.filter(
        RockArt.latitude.isnot(None),
        RockArt.longitude.isnot(None)
    ).all()

    features = []
    for record in records:
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [record.longitude, record.latitude]
            },
            'properties': {
                'id': record.id,
                'site': record.site,
                'motif': record.motif,
                'panel': record.panel,
                'groups': record.groups,
                'type': record.type,
                'description': record.description,
                'date': record.date.strftime('%Y-%m-%d') if record.date else None
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return jsonify(geojson)


@app.route('/api/cog-proxy')
def cog_proxy():
    """Proxy COG requests from Dropbox to bypass CORS issues."""
    import requests
    from flask import Response, request as flask_request

    cog_url = os.getenv('DROPBOX_COG_URL')
    if not cog_url:
        print("ERROR: DROPBOX_COG_URL environment variable not set")
        return jsonify({'error': 'COG URL not configured. Please set DROPBOX_COG_URL environment variable.'}), 503

    # Get range header from client request (for COG byte-range requests)
    range_header = flask_request.headers.get('Range')

    headers = {}
    if range_header:
        headers['Range'] = range_header

    print(f"COG Proxy: Requesting from Dropbox: {cog_url[:50]}... (Range: {range_header})")

    try:
        # Stream from Dropbox
        response = requests.get(cog_url, headers=headers, stream=True, timeout=30)

        print(f"COG Proxy: Dropbox response status: {response.status_code}")

        # Check if Dropbox returned an error
        if response.status_code >= 400:
            error_text = response.text[:200] if response.text else "No error details"
            print(f"COG Proxy: Dropbox error: {response.status_code} - {error_text}")
            return jsonify({
                'error': f'Dropbox returned {response.status_code}',
                'details': error_text
            }), 503

        # Create response with CORS headers
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        flask_response = Response(
            generate(),
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'image/tiff')
        )

        # Add CORS headers
        flask_response.headers['Access-Control-Allow-Origin'] = '*'
        flask_response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        flask_response.headers['Access-Control-Allow-Headers'] = 'Range'
        flask_response.headers['Access-Control-Expose-Headers'] = 'Content-Range, Content-Length, Accept-Ranges'

        # Copy important headers from Dropbox response
        if 'Content-Range' in response.headers:
            flask_response.headers['Content-Range'] = response.headers['Content-Range']
        if 'Content-Length' in response.headers:
            flask_response.headers['Content-Length'] = response.headers['Content-Length']
        if 'Accept-Ranges' in response.headers:
            flask_response.headers['Accept-Ranges'] = response.headers['Accept-Ranges']

        return flask_response

    except requests.exceptions.Timeout:
        print("COG Proxy: Request to Dropbox timed out")
        return jsonify({'error': 'Request to Dropbox timed out'}), 503
    except requests.exceptions.RequestException as e:
        print(f"COG Proxy: Request error: {e}")
        return jsonify({'error': f'Failed to fetch from Dropbox: {str(e)}'}), 503
    except Exception as e:
        print(f"COG Proxy: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/cog-proxy', methods=['OPTIONS'])
def cog_proxy_options():
    """Handle CORS preflight for COG proxy."""
    from flask import Response
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Range'
    return response


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database with tables and default data."""
    with app.app_context():
        db.create_all()

        # Create default admin user if no users exist
        if User.query.count() == 0:
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user (username: admin, password: admin123)")

        # Import type descriptions if list_type.xlsx exists
        excel_path = Path(__file__).parent.parent / 'list_type.xlsx'
        if excel_path.exists() and TypeDescription.query.count() == 0:
            type_descriptions = import_type_descriptions_from_excel(excel_path)
            for type_name, description in type_descriptions.items():
                type_desc = TypeDescription(type_name=type_name, description=description)
                db.session.add(type_desc)
            db.session.commit()
            print(f"Imported {len(type_descriptions)} type descriptions from Excel")


@app.cli.command()
def initdb():
    """Initialize the database."""
    init_db()
    print("Database initialized successfully!")


if __name__ == '__main__':
    # Create upload directories
    app.config['ORIGINAL_FOLDER'].mkdir(parents=True, exist_ok=True)
    app.config['THUMBNAIL_FOLDER'].mkdir(parents=True, exist_ok=True)

    # Initialize database
    init_db()

    # Run app
    app.run(debug=True)
