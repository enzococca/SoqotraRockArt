"""
Configuration settings for the Flask application.
"""
import os
from pathlib import Path

basedir = Path(__file__).parent.absolute()


class Config:
    """Base configuration."""

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{basedir / "rockart.db"}'

    # Fix for Render PostgreSQL URLs (postgres:// -> postgresql://)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = basedir / 'static' / 'uploads'
    ORIGINAL_FOLDER = UPLOAD_FOLDER / 'originals'
    THUMBNAIL_FOLDER = UPLOAD_FOLDER / 'thumbnails'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Thumbnail settings
    THUMBNAIL_SIZE = (200, 200)

    # Pagination
    RECORDS_PER_PAGE = 20

    # Map settings
    DEFAULT_MAP_CENTER = [12.5, 54.0]  # Soqotra coordinates
    DEFAULT_MAP_ZOOM = 10

    # Dropbox settings for remote image hosting
    USE_DROPBOX = os.environ.get('USE_DROPBOX', 'True').lower() == 'true'

    # Dropbox API Access Token
    # MUST be set in environment variables - no fallback as tokens expire
    DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN')

    # Dropbox folder paths (relative to Dropbox root)
    DROPBOX_ORIGINAL_FOLDER = '/Soqotra/ROCKART DATABASE/original_images'
    DROPBOX_THUMBNAIL_FOLDER = '/Soqotra/ROCKART DATABASE/thumbnails'

    # Cache settings for Dropbox temporary links (valid for 4 hours)
    DROPBOX_LINK_CACHE_TIMEOUT = 3600 * 3  # 3 hours (refresh before expiration)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
