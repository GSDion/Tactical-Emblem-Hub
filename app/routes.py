from flask import render_template, current_app as app
from flask import redirect, url_for

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

@app.route('/signup')
def signup():
    return render_template('signup.html')

# LOGIN
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# CREATE TEAM

# EDIT TEAM
