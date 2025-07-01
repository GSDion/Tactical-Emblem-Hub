from flask import render_template, request, redirect, session, flash
from flask import redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import re
# Import schemas
from .models import User
from flask import Blueprint
# db and csrf variables
from extensions import db
from flask_login import login_user, logout_user, login_required, current_user
import sqlalchemy as sa

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
            flash("All fields are required.")
            return render_template("users/signup.html")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!")
            return render_template("users/signup.html")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only letters and numbers!")
            return render_template("users/signup.html")
        elif password != confirm_password:
            flash("Your password fields do not match!")
            return render_template("users/signup.html")

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Username already taken!")
            return render_template("users/signup.html")
           
        if User.query.filter_by(email=email).first():
            flash("Email already registered!")
            return render_template("users/signup.html")
           

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
            flash("An error occurred. Please try again.")
            return render_template("users/signup.html")
        
    return render_template('users/signup.html')

# LOGIN
# Need to put both POST and GET methods or the error "The method is not allowed for the requested URL" will occur
'''
When an address is entered in the browser and enter is hit, a GET is being performed.
If you are trying to access that API endpoint directly in your browser, you will 
have a method problem because your route explicitly states it is limited to "POST"
'''
@bp.route('/login', methods=["POST", "GET"])
def login():
    # Get email and password data
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # Check if email exists
    user = User.query.filter_by(email=email).first()

    # check if hashed_password equals entered password
    if not user or not check_password_hash(user.password_hash, password):
        flash("Please check your login details and try again.")
        return render_template("users/login.html")
        

    # User has passed all checks, Create a session and Log the user in 
    login_user(user, remember=remember)
    flash("You have been logged in!")
    return redirect(url_for('main.index'))


# LOGOUT
@bp.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out! Goodbye!")
    return redirect(url_for('main.index'))

@bp.route('/faq')
def faq():
    return render_template('faq.html')

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/profile/<username>', methods=["POST", "GET"])
@login_required
def profile(username):

    # Populate fields with current email, username, and image.
    if request.method == "GET":
        # Filter by username
        user = db.first_or_404(sa.select(User).where(User.username == username))
        # Get and define user's email and username
        user_email = user.email
        user_image = user.image
        print(username)
        print(user_email)
        # Print the current email and username
        return render_template('profile.html', user=user, username=username, user_email=user_email, user_image=user_image)
    
    
    # Edit either the image, email, username, or password of an account
    if request.method == "POST":

        return render_template('profile.html')

# CREATE TEAM

# EDIT TEAM
