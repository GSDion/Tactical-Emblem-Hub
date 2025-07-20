from flask import abort, render_template, request, redirect, session, flash
from flask import redirect, url_for
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import re
# Import schemas
from .models import User, Contact_Message, Character, Character_Attribute, Character_Inventory, Team_Character, Team, User_Team, Game, Attribute,Inventory_Item, Strategy
from flask import Blueprint
# db and csrf variables
from extensions import db, mail
from flask_login import login_user, logout_user, login_required, current_user
import sqlalchemy as sa
from config import Config
from flask import current_app
from datetime import datetime, timezone

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

#About_page of INDEX
@bp.route('/about_section')
def about_section():
    return redirect(url_for('main.index', _anchor='about_page'))

#Title_page of INDEX
@bp.route('/title_section')
def title_section():
    return redirect(url_for('main.index', _anchor='title_page'))

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

@bp.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        # Getting data from the form
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Adding entries to the DB and committing
        contact_msg = Contact_Message(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(contact_msg)
        db.session.commit()

        # Sending message to gmail
        try:
            msg = Message(
                subject=f"Message from {name} at {email}",
                sender=email,
                recipients=current_app.config['MAIL_RECIPIENTS'],  # Must be a list
                body=f"Subject: {subject}\n\nMessage: {message}"
            )

            # Debugging
            print(f"""
            === Email Debug ===
            From: {email}
            To: {current_app.config['MAIL_RECIPIENTS']}
            Subject: Message from {name} at {email}
            Body:
            {subject}
            ---
            {message}
            === End Debug ===
            """)

            mail.send(msg)
            flash("Form Submission Successful!")
            return render_template("contact.html")
        except Exception as e:
            flash("Message could not be sent. Please try again later.")
            print(f"Error sending email: {e}")
            return render_template("contact.html")

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
@bp.route('/delete/<username>', methods=["POST"])
@login_required
def delete_account(username):
    if current_user.username != username:
        abort(403)
    # Query.delete() does not offer in-Python cascading
    # Need to query the database FIRST and THEN delete the user object directly
    # Cannot just delete the user by id
    # A line such as "User.query.filter_by(current_user.id).delete()" would not offer cascading
    # after "filter", you are still returned a Query object. Therefore, when you call `delete()`, 
    # you are calling `delete()` on the Query object (not the User object). 
    # This means a bulk delete (albeit probably with just a single row being deleted) was done
    # However, if cascading is done at database lvl, then the aforementioned line WOULD work
    user = db.session.query(User).filter(User.id == current_user.id).first()
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash("Your account has been deleted! Goodbye!")
    
    return redirect(url_for('main.index'))

# CREATE TEAM
@bp.route('/create-team', methods=['GET', 'POST'])
@login_required 
def create_team():
    """
    Multi-step team creation process:
    1. Team naming
    2. Game selection
    3. Character selection with attributes/inventory
    4. Strategy creation
    """
    
    # Initialize session data if this is the first step
    if 'form_data' not in session:
        session['form_data'] = {'user_id': current_user.id}  # Store the current user ID
    
    # Get current step from query parameters, default to step 1
    current_step = request.args.get('step', default=1, type=int)
    
    # Handle form submissions
    if request.method == 'POST':
        form_data = session['form_data']
        
        # STEP 1: Team naming
        if current_step == 1:
            form_data['team_name'] = request.form.get('team_name')
        
        # STEP 2: Game selection
        elif current_step == 2:
            form_data['game_id'] = request.form.get('game_id')
        
        # STEP 3: Character selection with customization
        elif current_step == 3:
            # Get list of selected character IDs
            form_data['character_ids'] = request.form.getlist('characters')
            form_data['character_data'] = {}
            
            # Store attributes and inventory for each character
            for char_id in form_data['character_ids']:
                form_data['character_data'][char_id] = {
                    # Dictionary of attribute IDs and their values
                    'attributes': {
                        attr_id: request.form.get(f'attr_value_{char_id}_{attr_id}')
                        for attr_id in request.form.getlist(f'attributes_{char_id}')
                    },
                    # Dictionary of inventory item IDs and quantities
                    'inventory': {
                        item_id: request.form.get(f'item_quantity_{char_id}_{item_id}', default=1)
                        for item_id in request.form.getlist(f'inventory_{char_id}')
                    }
                }
        
        # STEP 4: Strategy creation (final step)
        elif current_step == 4:
            form_data['strategy_description'] = request.form.get('strategy_description')
            # Process the complete form when reaching the final step
            return process_final_team_submission()
        
        # Update session data with new form data
        session['form_data'] = form_data
        
        # Handle the navigation between steps
        if 'next' in request.form and current_step < 4:
            # Move to next step
            return redirect(url_for('main.create_team', step=current_step+1))
        elif 'previous' in request.form and current_step > 1:
            # Return to previous step
            return redirect(url_for('main.create_team', step=current_step-1))
    
    # GET request handling (display appropriate step)
    
    # STEP 1: Team naming form
    if current_step == 1:
        return render_template('create_team/create_team.html', 
                            current_step=current_step)
    
    # STEP 2: Game selection (requires team name from step 1)
    # Fix: DO not allow selection of multiple games. Not currently able to go back to team if selection
    # game is not chosen
    elif current_step == 2:
        if 'team_name' not in session['form_data']:
            # Redirect if trying to access step 2 without completing step 1
            return redirect(url_for('main.create_team', step=1))
        
        # Get all games for selection
        games = Game.query.order_by(Game.title).all()
        return render_template('create_team/create_team.html',
                            current_step=current_step,
                            games=games)
    
    # STEP 3: Character selection (requires game selection from step 2)
    elif current_step == 3:
        if 'game_id' not in session['form_data']:
            # Redirect if trying to access step 3 without completing step 2
            return redirect(url_for('main.create_team', step=2))
            
        # Get related data based on selected game
        game_id = session['form_data']['game_id']
        characters = Character.query.filter_by(game_id=game_id).order_by(Character.name).all()
        attributes = Attribute.query.order_by(Attribute.attribute_name).all()
        inventory_items = Inventory_Item.query.order_by(Inventory_Item.item_name).all()
        
        return render_template('create_team/create_team.html',
                            current_step=current_step,
                            characters=characters,
                            attributes=attributes,
                            inventory_items=inventory_items)
    
    # STEP 4: Strategy creation (requires character selection from step 3)
    elif current_step == 4:
        if 'character_ids' not in session['form_data'] or not session['form_data']['character_ids']:
            # Redirect if trying to access step 4 without selecting characters
            return redirect(url_for('create_team', step=3))
        
        return render_template('create_team/create_team.html',
                            current_step=current_step)
    
def process_final_team_submission():
    if 'form_data' not in session:
        flash('Session expired. Please start again.', 'danger')
        return redirect(url_for('main.create_team'))
    
    form_data = session.pop('form_data')
    
    try:
        # Verify required data exists
        required_fields = ['user_id', 'team_name', 'game_id', 'character_ids', 'strategy_description']
        if not all(key in form_data for key in required_fields):
            flash('Missing required data', 'danger')
            return redirect(url_for('main.create_team'))
        
        # Create the team
        team = Team(
            team_name=form_data['team_name'],
            game_id=form_data['game_id'],
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(team)
        db.session.flush()  # Get the team ID
        
        # Create UserTeam association
        user_team = User_Team(
            user_id=form_data['user_id'],
            team_id=team.id,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(user_team)
        
        # Create Strategy
        strategy = Strategy(
            team_id=team.id,
            description=form_data['strategy_description'],
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(strategy)
        
        # Add characters to team and their attributes/inventory
        for char_id in form_data['character_ids']:
            # Create TeamCharacter association
            team_char = Team_Character(
                team_id=team.id,
                character_id=int(char_id),
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(team_char)
            
            # Add character attributes
            char_data = form_data.get('character_data', {}).get(char_id, {})
            for attr_id, attr_value in char_data.get('attributes', {}).items():
                char_attr = Character_Attribute(
                    character_id=int(char_id),
                    attribute_id=int(attr_id),
                    attribute_value=attr_value if attr_value else None,
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(char_attr)
            
            # Add character inventory
            for item_id, quantity in char_data.get('inventory', {}).items():
                char_inv = Character_Inventory(
                    character_id=int(char_id),
                    inventory_item_id=int(item_id),
                    quantity=int(quantity),
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(char_inv)
        
        db.session.commit()
        
        flash(f'Team "{team.team_name}" created successfully with strategy!', 'success')
        # return redirect(url_for('view_team', team_id=team.id))
        return redirect(url_for('main.index'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating team: {str(e)}")
        flash('An error occurred while creating your team. Please try again.', 'danger')
        return redirect(url_for('main.create_team'))

# EDIT TEAM
# THIS SHOULD BE IN EDIT PROFILE

# DELETE TEAM
# THIS SHOULD BE IN EDIT PROFILE