from flask import render_template, current_app as app

@app.route('/')
def index():
    return render_template('index.html')

# SIGNUP
@app.route('/signup')
def signup():
    return render_template('signup.html')

# LOGIN
@app.route('/login')
def login():
    return render_template('login.html')

# CREATE TEAM

# EDIT TEAM
