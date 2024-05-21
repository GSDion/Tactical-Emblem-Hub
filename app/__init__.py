from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Initialize CSRFProtect instance
csrf = CSRFProtect()

def create_app():
    # Create a new Flask application instance
    app = Flask(__name__)
    
    # Load configuration settings from config.py's Config class
    app.config.from_object('config.Config')

    # Initialize the SQLAlchemy instance with the app
    db.init_app(app)

    # Initialize CSRF protection for the app
    csrf.init_app(app)

    with app.app_context():
        # Import routes (views) after app is created to avoid circular imports
        from . import routes
        
        # Create all database tables defined in models.py
        db.create_all()

    # Return the Flask app instance
    return app
