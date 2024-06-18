from app import app, db
from app import User, bcrypt  # Import User model and bcrypt from your app

with app.app_context():
    # Create the database tables
    db.create_all()

