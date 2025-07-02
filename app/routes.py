from flask import abort, render_template, request, redirect, session, flash
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
    if current_user.username != username:
        abort(403)

    if request.method == "POST":
        
        errors = False

        # Initialize variables
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm-password', '').strip()

        # --- VALIDATION CHECKS (Only for provided fields) ---
        # Email validation (only if email field was modified)
        if 'email' in request.form and new_email:
            if not re.match(r'[^@]+@[^@]+\.[^@]+', new_email):
                flash("Invalid email address!", "error")
                errors = True
            elif User.query.filter(User.email == new_email, User.id != current_user.id).first():
                flash("Email already registered!", "error")
                errors = True

        # Username validation (only if username field was modified)
        if 'username' in request.form and new_username:
            if not re.match(r'^[A-Za-z0-9_]+$', new_username):
                flash("Username must contain only letters, numbers and underscores!", "error")
                errors = True
            elif User.query.filter(User.username == new_username, User.id != current_user.id).first():
                flash("Username already taken!", "error")
                errors = True

        # Password validation (only if password field was modified)
        if 'password' in request.form and new_password:
            if new_password != confirm_password:
                flash("Passwords don't match!", "error")
                errors = True
            elif len(new_password) < 8:
                flash("Password must be at least 8 characters!", "error")
                errors = True

        if errors:
            return render_template("users/profile.html")

        # Edit either the email, username, or password of an account (All fields do not have to be filled)
        # Only update fields that were provided and non-empty
        if 'username' in request.form:
            # request.form['username'] : Gets the raw username value submitted in the HTML form 
            # (could be " new_username " with spaces) and stripes the trailing white space

            # current_user.username : Updates the username attribute of the SQLAlchemy 
            # current_user object in memory.

            # database is not changed yet
            current_user.username = new_username if new_username else current_user.username
        
        # Change Email 
        if 'email' in request.form:
            current_user.email = new_email if new_email else current_user.email

        # Change password with validaton
        if 'password' in request.form and new_password:
            current_user.password = generate_password_hash(new_password)

        try:
            # Now, the database has been changed.
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:  # Catches database errors (e.g., empty strings)
            db.session.rollback()
            flash("An error occurred. There may be invalid data. Fields cannot be empty.", "error")
        
        return redirect(url_for('main.profile', username=current_user.username))
        
    return render_template('users/profile.html')

# DELETE ACCOUNT
@bp.route('/delete/<username>', methods=["DELETE", "GET"])
@login_required
def delete_account(username):
    flash("Your account has been deleted! Goodbye!")
    return render_template('index.html')
# CREATE TEAM

# EDIT TEAM
