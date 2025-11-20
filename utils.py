"""
Utility functions for the Rock Art application.
"""
import os
from pathlib import Path
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def create_thumbnail(image_path, thumbnail_path, size=(200, 200)):
    """
    Create a thumbnail from an image.

    Args:
        image_path: Path to the original image
        thumbnail_path: Path where thumbnail will be saved
        size: Tuple of (width, height) for thumbnail
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Create thumbnail maintaining aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save as JPEG
            img.save(thumbnail_path, 'JPEG', quality=85)
            return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False


def save_uploaded_image(file, record_id):
    """
    Save uploaded image and create thumbnail.

    Args:
        file: FileStorage object from Flask
        record_id: ID of the associated rock art record

    Returns:
        Tuple of (original_path, thumbnail_path, original_filename) or (None, None, None) on error
    """
    if not file or not allowed_file(file.filename):
        return None, None, None

    # Secure the filename
    original_filename = secure_filename(file.filename)
    filename = f"{record_id}_{original_filename}"

    # Create paths
    original_folder = current_app.config['ORIGINAL_FOLDER']
    thumbnail_folder = current_app.config['THUMBNAIL_FOLDER']

    # Ensure directories exist
    original_folder.mkdir(parents=True, exist_ok=True)
    thumbnail_folder.mkdir(parents=True, exist_ok=True)

    # Save original image
    original_path = original_folder / filename
    file.save(original_path)

    # Create thumbnail
    thumbnail_filename = f"thumb_{filename}"
    # Force .jpg extension for thumbnails
    thumbnail_filename = Path(thumbnail_filename).stem + '.jpg'
    thumbnail_path = thumbnail_folder / thumbnail_filename

    if create_thumbnail(original_path, thumbnail_path, current_app.config['THUMBNAIL_SIZE']):
        # Return relative paths for database storage
        rel_original = f"uploads/originals/{filename}"
        rel_thumbnail = f"uploads/thumbnails/{thumbnail_filename}"
        return rel_original, rel_thumbnail, original_filename
    else:
        # Clean up if thumbnail creation failed
        if original_path.exists():
            original_path.unlink()
        return None, None, None


def delete_image_files(image_path, thumbnail_path):
    """
    Delete image and thumbnail files from filesystem.

    Args:
        image_path: Relative path to original image
        thumbnail_path: Relative path to thumbnail

    Returns:
        True if successful, False otherwise
    """
    try:
        static_folder = Path(current_app.static_folder)

        # Delete original image
        original = static_folder / image_path
        if original.exists():
            original.unlink()

        # Delete thumbnail
        thumbnail = static_folder / thumbnail_path
        if thumbnail.exists():
            thumbnail.unlink()

        return True
    except Exception as e:
        print(f"Error deleting image files: {e}")
        return False


def parse_geopackage_filename(filename):
    """
    Parse filename to extract site and motif.
    Example: 'SHP412_M011_Mixed motifs_2.JPG' -> site='SHP412', motif='M011'

    Args:
        filename: Original filename

    Returns:
        Tuple of (site, motif) or (None, None)
    """
    import re
    match = re.match(r'^([^_]+)_([^_]+)_.*', filename)
    if match:
        return match.group(1), match.group(2)
    return None, None


def import_type_descriptions_from_excel(excel_path):
    """
    Import type descriptions from Excel file.

    Args:
        excel_path: Path to Excel file with Type and Description columns

    Returns:
        Dictionary mapping type names to descriptions
    """
    try:
        import pandas as pd
        df = pd.read_excel(excel_path, sheet_name='Sheet1')
        return dict(zip(df['Type'], df['Description']))
    except Exception as e:
        print(f"Error importing type descriptions: {e}")
        return {}
