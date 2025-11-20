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
    DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN') or \
        'sl.u.AGHtkM2VUQVEdbDQOUzb0eOVAZCvFpvCPQmN_I3LWSiNJj8TmwfNu_DMxGaLvYKzsjfFL1bBgrh1vCe2UvZBYToVSkfHMwQtUPkd2S-NR1yYY_Zp8OzUXig5sHtBi1C9BWwf02PfzIMC8Rcy7Bx3IEy15cFTCOSdbb7TGBgtd4LCttwigkKBddB_D4HiREVOrPLtMxe6Ww3d1qmTxhToJRc6ST4oPSaqGCH8UUK_INmXSn9qx-ED24NibSrv4ppjZg-hqMwIymjPdewM5pxjrpMBQIL6iIAFjPoblRf8p4d4bz39FndCAbVbXflxewG55_C29I03RH2lb6Gm4pJdvaBHKq9Ub5NxolYnj_T1wdajMUbt-COFSe-HBajefYAfJguxD7ZIBLB-JVEBa8TQ6zstKA8IIMF2mbmB-6JpYNiCOugSof_p_yUgCOqU7z7xNJxAPxtdS8GR6aNvSjbbkIWSBuoNwNEopw9Mwg2JyOug1p5kglaPeX39ozLxsUv9bAm91OpNTfe1cd7aIIbjeEEnvXHFldop6v0Oofqc33R-RANpWvXC6Z7pjaZltq8hTsJhCF9zaEMXkUXzTL2qEqt8H7NjL4DHQS6vy9-WFMsvUdLdkoMEjvYo6Y38KEL4oY4uD5fcmowxgZ8_27iyqQddG_kWMqoSYGrSLHT4GYETztn0SEcxjrHnqvjamwEETmiVZrLsATX8VfkqcsZ6ukiVeVx5P6fIA0t3p_gNhI70Ky5_2oezuL8Q-pqCqA0euvviQooQVC_aFtgWvv1DmEXoIswDo3RoFmAMHX9b_R8NpSMKcQ__5qGc0cvHCOwViPrqkj7d9uH20Uv80werCbKaIWjX8DSzDo7TpEmCet2G6H4T9pfYUoGdCPyfkfIB_RXsR6Ig6kZ9FTmSnMOqt8o_XPr9a_5_XkL4Cuk8EZCwrwGnYCHrtlRaoa0kZRVsdfiTOaeeoAhKtfAcmhW2Xi6vaMED6XKb9E8-__XnhMD1ylCAm7S4LVasqEnm9RFvFHVZwRR1qv0sql5cGHRYnoHeUvIqP46rNa-EmJslZpgfRssXVJnJawdzX_D7sh8xComn25yOOidoqvv-lGYMtKYJ2T-4eP07c_JlVqAPi5ogOG2XRnXu4GP_4OUYZRwNaXpgvYRsC6MDsGnhMuz0num3pChikeMKbUrzvpeeS8poMFBKJL7L4kDfDSBaRDLldSKRAfseebZ86tbB73cfP3XLJkog-EE91IR1YxvmTDqRUuzcsLgVov_tiLIpNXoooCR6qL7LHgCootj7S91eRjDN'

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
