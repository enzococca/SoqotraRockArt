"""
Database models for the Rock Art application.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class RockArt(db.Model):
    """Rock art record model."""
    __tablename__ = 'rockart'

    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(100), nullable=False, index=True)
    motif = db.Column(db.String(100), nullable=False, index=True)
    panel = db.Column(db.String(100))
    groups = db.Column(db.String(100))
    type = db.Column(db.String(100), index=True)
    date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Geospatial data (optional)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Relationships
    images = db.relationship('Image', back_populates='record', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<RockArt {self.site} - {self.motif}>'

    def to_dict(self):
        """Convert record to dictionary."""
        return {
            'id': self.id,
            'site': self.site,
            'motif': self.motif,
            'panel': self.panel,
            'groups': self.groups,
            'type': self.type,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'image_count': len(self.images)
        }


class Image(db.Model):
    """Image model for rock art photos."""
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('rockart.id'), nullable=False, index=True)
    image_path = db.Column(db.String(255), nullable=False)
    thumbnail_path = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    record = db.relationship('RockArt', back_populates='images')

    def __repr__(self):
        return f'<Image {self.original_filename}>'

    def to_dict(self):
        """Convert image to dictionary."""
        return {
            'id': self.id,
            'record_id': self.record_id,
            'image_path': self.image_path,
            'thumbnail_path': self.thumbnail_path,
            'original_filename': self.original_filename,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class TypeDescription(db.Model):
    """Type descriptions for rock art types."""
    __tablename__ = 'type_descriptions'

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<TypeDescription {self.type_name}>'
