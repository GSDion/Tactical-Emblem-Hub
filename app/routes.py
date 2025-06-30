from flask import render_template, request, redirect, session
from flask import redirect, url_for
from werkzeug.security import generate_password_hash
import re
# Import schemas
from .models import User
# Dont need this, just SQLALchemy for qeurying 
# from app.database import *
from flask import Blueprint
from extensions import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Validate form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        email = request.form.get("email")

        if not (username and password and email and confirm_password):
            return render_template("signup.html", message="All fields are required.")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return render_template("signup.html", message="Invalid email address!")
        elif not re.match(r'[A-Za-z0-9]+', username):
            return render_template("signup.html", message="Username must contain only letters and numbers!")
        elif password != confirm_password:
            return render_template("signup.html", message="Your password fields do not match!")

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            return render_template("signup.html", message="Username already taken!")
        if User.query.filter_by(email=email).first():
            return render_template("signup.html", message="Email already registered!")

        # Hash the password and create new user with SQLAlchemy
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role="user"  # Automatically assign role "user"
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
        except Exception as e:
            db.session.rollback()
            return render_template("signup.html", message="An error occurred. Please try again.")

    return render_template('users/signup.html')

# LOGIN
@bp.route('/login', methods=["GET"])
def login():
    # Get username and password data

    # Check if username exists

    # Match username with hashed_password, check if hashed_password equals entered password

    #create a session for the user



    return render_template('users/login.html')

# LOGOUT

@bp.route('/faq')
def faq():
    return render_template('faq.html')

@bp.route('/contact')
def contact():
    return render_template('contact.html')

# CREATE TEAM

# EDIT TEAM
