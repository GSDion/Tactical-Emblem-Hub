from flask import render_template, request, redirect, session, current_app as app
from flask import redirect, url_for
from werkzeug.security import generate_password_hash
import re
from config import Config
# from app import create_app

# Import app?
# app = create_app()
app.config.from_object(Config)
app.config["SECRET_KEY"]




@app.route('/')
def index():
    return render_template('index.html')


# INDEX: title_section
@app.route('/hero')
def title_section():
    return redirect(url_for('index',_anchor='title_page'))

# INDEX: about_section
@app.route('/about')
def about_section():
    return redirect(url_for('index',_anchor='about_page_title'))

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Validate form data
        # MAKE SURE THESE NAMES MATCH THE ONES IN SIGNUP.HTML
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        email = request.form.get("email")


        if not (username or not password or not email or not confirm_password):
            return render_template("signup.html", message="All fields are required.")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return render_template("signup.html", message="Invalid email address!")
        elif not re.match(r'[A-Za-z0-9]+', username):
            return render_template("signup.html", message="Username must contain only letters and numbers!")
        elif not (password == confirm_password):
            return render_template("signup.html", message="Your password fields do not match!")

        # Hash the password
        hashed_password = generate_password_hash(password)

        # AUTOMATICALLY ASSIGN ROLE "USER"
        # Store user data in the SQLite database 
        

        return redirect("/login")
    return render_template('users/signup.html')

# LOGIN
@app.route('/login')
def login():
    return render_template('users/login.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# CREATE TEAM

# EDIT TEAM
