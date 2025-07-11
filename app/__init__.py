from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_mail import Mail
from extensions import db, csrf, mail
from flask_login import LoginManager

# db and csrf need to be defined outside any function or class,
# so they are accessible globally throughout the application.

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
    # Intialize extensions
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app) # This should come after config is loaded

    login_manager = LoginManager()
    login_manager.login_view = 'bp.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # Initialize CSRF protection for the app
    # csrf.init_app(app)

    # Flask Mail
    # mail.init_app(app)

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
        # app.register_blueprint(routes.bp)
        app.register_blueprint(bp) # Use the imported bp directly


    # Return the Flask app instance
    return app
