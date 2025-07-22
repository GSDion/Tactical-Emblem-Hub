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
from .forms import TeamInfoForm, GameSelectionForm, CharacterSelectionForm, StrategyForm
from sqlalchemy import exc

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

@bp.route('/create-team/<int:step>', methods=['GET', 'POST'])
@login_required
def create_team(step):
    # Initialize session data with all pf the required keys
    if 'form_data' not in session:
        session['form_data'] = {
            'user_id': current_user.id,
            'step1': {},  # Team Name/info
            'step2': {},  # Game selection
            'step3': {},  # Character selection
            'step4': {}   # Strategy
        }
    else:
        # Ensure all keys exist even if session exists
        session['form_data'].setdefault('step1', {})
        session['form_data'].setdefault('step2', {})
        session['form_data'].setdefault('step3', {})
        session['form_data'].setdefault('step4', {})
    
    # Initialize template variables
    template_vars = {
        'current_step': step,
        'total_steps': 4,
        'games': None,
        'selected_game': None,
        'characters': None,
        'attributes': None,
        'inventory_items': None,
        'team_name': session['form_data']['step1'].get('team_name', '')
    }

    # Step 1: Team Info
    if step == 1:
        form = TeamInfoForm(data=session['form_data']['step1'])
        # DEBUG
        print("Form data received:", form.data)
        if form.validate_on_submit():
            session['form_data']['step1'] = {
                'team_name': form.team_name.data
            }
            session.modified = True
            return redirect(url_for('main.create_team', step=2))
    
    # Step 2: Game Selection
    elif step == 2:
        form = GameSelectionForm()
        games = Game.query.order_by(Game.title).all()
        form.game_id.choices = [(g.id, g.title) for g in games]
        
        # Pre-populate form if returning to this step
        if 'game_id' in session['form_data']['step2']:
            form.game_id.data = session['form_data']['step2']['game_id']
        # DEBUG
        print("Form data received:", form.data)
        if form.validate_on_submit():
            session['form_data']['step2'] = {
                'game_id': form.game_id.data
            }
            session.modified = True
            return redirect(url_for('main.create_team', step=3))
        
        template_vars['games'] = games
    
    # Step 3: Character Selection
    elif step == 3:
        if 'step2' not in session['form_data']:
            return redirect(url_for('main.create_team', step=2))
            
        game_id = session['form_data']['step2']['game_id']
        selected_game = Game.query.get(game_id)
        characters = Character.query.filter_by(game_id=game_id).order_by(Character.name).all()
        attributes = Attribute.query.order_by(Attribute.attribute_name).all()
        inventory_items = Inventory_Item.query.order_by(Inventory_Item.item_name).all()
        
        # Initialize character_dict
        character_dict = {str(c.id): c for c in characters}
        
        form = CharacterSelectionForm()
        form.characters.choices = [(c.id, c.name) for c in characters]
        
        # Initialize step3 data if not exists
        if 'step3' not in session['form_data']:
            session['form_data']['step3'] = {
                'character_ids': [],
                'character_data': {}
            }
        
        # Safely get character_ids with default empty list
        character_ids = session['form_data']['step3'].get('character_ids', [])
        form.characters.data = character_ids
        # DEBUG
        print("Form data received:", form.data)
        if form.validate_on_submit():
            # Get selected characters from form
            selected_characters = form.characters.data
            
            # Preserve existing character_data for selected characters
            existing_data = session['form_data']['step3'].get('character_data', {})
            new_character_data = {}
            
            # Only keep data for currently selected characters
            for char_id in selected_characters:
                char_id_str = str(char_id)
                new_character_data[char_id_str] = existing_data.get(char_id_str, {})
            
            # Update session
            session['form_data']['step3'] = {
                'character_ids': selected_characters,
                'character_data': new_character_data
            }
            session.modified = True
            
            return redirect(url_for('main.create_team', step=4))
        
        template_vars.update({
            'selected_game': selected_game,
            'characters': characters,
            'character_dict': character_dict,
            'attributes': attributes,
            'inventory_items': inventory_items
        })
    
    
    # Step 4: Strategy
    elif step == 4:
        if 'step3' not in session['form_data']:
            return redirect(url_for('main.create_team', step=3))
            
        form = StrategyForm(data=session['form_data'].get('step4', {}))
        # DEBUG
        print("Form data received:", form.data)
        if form.validate_on_submit():
            session['form_data']['step4'] = {
                'strategy_description': form.strategy_description.data
            }
            session.modified = True
            
            # Verify all required data is present
            required_data = {
                'team_name': session['form_data']['step1'].get('team_name'),
                'game_id': session['form_data']['step2'].get('game_id'),
                'character_ids': session['form_data']['step3'].get('character_ids', []),
                'strategy_description': form.strategy_description.data
            }
            
            if not all(required_data.values()):
                flash('Missing required team information', 'danger')
                return redirect(url_for('main.create_team', step=1))
                
            if len(required_data['character_ids']) == 0:
                flash('Please select at least one character', 'danger')
                return redirect(url_for('main.create_team', step=3))
                
            return process_final_team_submission()
        
    if step > 1:
        template_vars['team_name'] = session['form_data']['step1'].get('team_name', 'Unknown Team')\
    # DEBUG
    print("Session data:", session['form_data'])  
    return render_template('create_team/create_team.html', form=form, **template_vars)
    
    # return render_template('create_team/create_team.html',
    #                     form=form,
    #                     current_step=step,
    #                     total_steps=4,
    #                     games=games,
    #                     selected_game=selected_game,
    #                     characters=characters,
    #                     attributes=attributes,
    #                     inventory_items=inventory_items)

def process_final_team_submission():
    
    # DEBUG: Print the data being saved
    print("Final team data being saved:", {
        'team_name': session['form_data']['step1']['team_name'],
        'game_id': session['form_data']['step2']['game_id'],
        'character_ids': session['form_data']['step3']['character_ids'],
        'strategy': session['form_data']['step4']['strategy_description']
    })
    # Check session exists before moving forward
    if 'form_data' not in session:
        flash('Session expired. Please start again.', 'danger')
        return redirect(url_for('main.create_team'))
    
    try:
        # Get and validate form data
        form_data = session.pop('form_data')
        required_fields = ['user_id', 'team_name', 'game_id', 'character_ids', 'strategy_description']
        
        if not all(key in form_data for key in required_fields):
            flash('Missing required team information', 'danger')
            return redirect(url_for('main.create_team'))
        
        # Validate character_ids is a non-empty list
        if not isinstance(form_data['character_ids'], list) or len(form_data['character_ids']) == 0:
            flash('No characters selected for the team', 'danger')
            return redirect(url_for('main.create_team', step=3))
        
        # Begin transaction
        with db.session.begin_nested():
            # Create the team
            team = Team(
                team_name=form_data['team_name'],
                game_id=form_data['game_id'],
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(team)
            db.session.flush()  # Get team ID without committing
            
            # Create UserTeam association
            db.session.add(User_Team(
                user_id=form_data['user_id'],
                team_id=team.id,
                created_at=datetime.now(timezone.utc)
            ))
            
            # Create Strategy
            db.session.add(Strategy(
                team_id=team.id,
                description=form_data['strategy_description'],
                created_at=datetime.now(timezone.utc)
            ))
            
            # Process characters and their attributes/inventory
            for char_id in form_data['character_ids']:
                # Validate character exists
                if not Character.query.get(char_id):
                    raise ValueError(f"Invalid character ID: {char_id}")
                
                # Add team-character relationship
                db.session.add(Team_Character(
                    team_id=team.id,
                    character_id=int(char_id),
                    created_at=datetime.now(timezone.utc)
                ))
                
                # Process attributes if they exist
                char_data = form_data.get('character_data', {}).get(str(char_id), {})
                
                for attr_id, attr_value in char_data.get('attributes', {}).items():
                    if not Attribute.query.get(attr_id):
                        continue  # Skip invalid attributes
                    db.session.add(Character_Attribute(
                        character_id=int(char_id),
                        attribute_id=int(attr_id),
                        attribute_value=attr_value if attr_value else None,
                        created_at=datetime.now(timezone.utc)
                    ))
                
                # Process inventory if it exists
                for item_id, quantity in char_data.get('inventory', {}).items():
                    if not Inventory_Item.query.get(item_id):
                        continue  # Skip invalid items
                    db.session.add(Character_Inventory(
                        character_id=int(char_id),
                        inventory_item_id=int(item_id),
                        quantity=max(1, int(quantity)),  # Min. quantity of 1
                        created_at=datetime.now(timezone.utc)
                    ))
        
        
        db.session.commit()
        
        flash(f'Team "{team.team_name}" created successfully!', 'success')
        return redirect(url_for('main.team_detail', team_id=team.id))
    
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Validation error: {str(e)}")
        flash('Invalid team data. Please check your selections.', 'danger')
        return redirect(url_for('main.create_team', step=3))
    
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error creating team: {str(e)}")
        flash('A database error occurred. Please try again.', 'danger')
        return redirect(url_for('main.create_team'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error creating team: {str(e)}", exc_info=True)
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('main.create_team'))
    

# EDIT TEAM
# THIS SHOULD BE IN EDIT PROFILE
"""
Make new form/card in edit profile that, 
after pressing a team card, redirects user to edit form for team 
(use team creation form)

Each team card will have an edit/delete button.
"""


# DELETE TEAM
# THIS SHOULD BE IN EDIT PROFILE