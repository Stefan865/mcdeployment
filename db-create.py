from flask import current_app
from app import db, Users  # Adjust the import path according to your project structure
import bcrypt
from app import app  # Import the Flask app object from app.py


def create_tables():
    with app.app_context():  # Use app.app_context() to push an application context
        db.create_all()
        print("Tables created successfully.")


def insert_test_data():
    with app.app_context():  # Again, use app.app_context() here
        hashed_password = bcrypt.hashpw(b'testpassword', bcrypt.gensalt()).decode('utf-8')
        user1 = Users(username='user1', email='user1@example.com', password=hashed_password,
                      server_name='Server1', ip_address='192.168.1.1', tier='Basic')
        user2 = Users(username='user2', email='user2@example.com', password=hashed_password,
                      server_name='Server2', ip_address='192.168.1.2', tier='Premium')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        print("Test data inserted successfully.")


if __name__ == '__main__':
    create_tables()
    insert_test_data()
