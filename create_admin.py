"""
Script to create the first admin user.
Run this after deployment:
    python create_admin.py
"""
import sys
from app import app, db, User

def create_admin():
    """Create admin user interactively."""
    print("=== Create Admin User ===\n")
    
    username = input("Enter username (default: admin): ").strip() or "admin"
    email = input("Enter email: ").strip()
    
    if not email:
        print("❌ Email is required!")
        sys.exit(1)
    
    password = input("Enter password: ").strip()
    if not password:
        print("❌ Password is required!")
        sys.exit(1)
        
    password_confirm = input("Confirm password: ").strip()
    if password != password_confirm:
        print("❌ Passwords do not match!")
        sys.exit(1)
    
    # Create user
    with app.app_context():
        # Check if user already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"❌ User '{username}' already exists!")
            sys.exit(1)
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"\n✅ Admin user '{username}' created successfully!")
        print(f"   Email: {email}")
        print(f"\nYou can now login at: http://your-app-url.onrender.com/login")

if __name__ == '__main__':
    create_admin()
