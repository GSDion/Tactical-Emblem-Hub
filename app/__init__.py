from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from extensions import db, csrf

# db and csrf have been defined outside any function or class,
# so they are accessible globally throughout the application.
# Initialize SQLAlchemy instance


# Initialize CSRFProtect instance


def create_app():
    ''' 
    The db object is linked to the app instance. 
    This ensures that db knows how to connect to the database using the configuration provided by the app
    '''
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
        # Import models AFTER db initialization
        from . import models
        
        # Create all database tables defined in models.py
        # DO not need to manually create tables. SQLAlchemy, 
        # together with db.create_all() or Flask-Migrate, 
        # will handle this. Just need to define models in Python, 
        # and the framework will map them to database tables
        db.create_all()

        # Import routes AFTER models
        # Import and register the blueprint
        from .routes import bp
        app.register_blueprint(routes.bp)

    # Return the Flask app instance
    return app
