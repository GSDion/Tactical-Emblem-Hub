# instead of using "import datetime"
from datetime import datetime, timezone
from app.__init__ import db
from extensions import db
from flask_login import UserMixin

'''
TO DO:
- [ ] DOCUMENT HOW RELATIONSHIPS ARE DEFINED IN CODE (Tactical_Emblem_Hub_Notes.md) (Ongoing...)
- [x] use either back_populates OR backrefs. Not both. (decided on back_populates)
- [ ] Delete a character --> inventory_items deleted? (Dont do if making pre-made inventory_items)
- [ ] Delete a character --> attributes deleted (Dont do if making pre-made attributes)
- [ ] Delete a game --> characters deleted
- [ ] Automated tests for database
'''
# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    # `user_id` (Primary Key)
    # - `username`
    # - `email`
    # - `password_hash`
    # - `role` (e.g., "Admin" or "User")
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), unique=False, nullable=False)
    role = db.Column(db.String(20), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # `Users` ⟶ 1:M ⟶ `UserTeams`
    user_teams = db.relationship('User_Team', back_populates='user', lazy=True)
    # `Images` ⟶ 1:1 ⟶ (`Users`, `Games`, `Teams`, `Characters`, `InventoryItems`)
    # Deleting a user will delete the image associated with the user
    image = db.relationship('Image', 
                       back_populates='user', 
                       uselist=False,
                       cascade='all, delete-orphan',
                       foreign_keys='Image.user_id')


# Game Model
class Game(db.Model):
    __tablename__ = 'game'
    # `game_id` (Primary Key)
    # - `title`
    # - `release_year`
    # - `description`
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=False, nullable=False)
    release_year = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.String(200), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # `Games` ⟶ 1:M ⟶ `Teams`
    teams = db.relationship('Team',back_populates='game',lazy=True)
    #  `Games` ⟶ 1:M ⟶ `Characters` 
    characters = db.relationship('Character',back_populates='game',lazy=True)
    # `Images` ⟶ 1:1 ⟶ (`Users`, `Games`, `Teams`, `Characters`, `InventoryItems`)
    # Deleting a game will delete the image associated with the game
    image = db.relationship('Image',
                      back_populates='game',
                      uselist=False,
                      cascade='all, delete-orphan',
                      foreign_keys='Image.game_id')

# Team Model
# ADD OPTIONAL MAP NAME ATTRIBUTES?
class Team(db.Model):
    __tablename__ = 'team'
    # - `team_id` (Primary Key)
    # - `team_name`
    # - `game_id` (Foreign Key referencing `Games`)
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(50), unique=False, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # `Games` ⟶ 1:M ⟶ `Teams`
    game = db.relationship('Game',back_populates='teams',lazy=True)
    # `Teams` ⟶ 1:M ⟶ `Strategies`
    strategies = db.relationship('Strategy',back_populates='team',lazy=True)
    # Relationship to the intermediate Team_Character model
    # `Teams` ⟶ M:N ⟶ `Characters` (via `TeamCharacters`)
    characters = db.relationship('Team_Character',back_populates='team')
    # `Images` ⟶ 1:1 ⟶ (`Users`, `Games`, `Teams`, `Characters`, `InventoryItems`)
    # Deleting a team will delete the image associated with the team
    #`Teams` ⟶ 1:M ⟶ `UserTeams`  
    user_teams = db.relationship('User_Team', back_populates='team', lazy=True)
     # Deleting a team will delete the image associated with the team
    image = db.relationship('Image',
                      back_populates='team',
                      uselist=False,
                      cascade='all, delete-orphan',
                      foreign_keys='Image.team_id')


# Character Model
class Character(db.Model):
    __tablename__ = 'character'
    # - `character_id` (Primary Key)
    # - `name`
    # - `game_id` (Foreign Key referencing `Games`)
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # Relationship to the intermediate Character_Attribute model
    attributes = db.relationship('Character_Attribute', back_populates='character',lazy=True)
    # Relationship to the intermediate Character_Inventory model
    # # - `Characters` ⟶ M:N ⟶ `InventoryItems` (via `CharacterInventory`)
    inventory_items = db.relationship('Character_Inventory', back_populates='character',lazy=True)
    # Relationship to the intermediate Team_Character model
    # `Teams` ⟶ M:N ⟶ `Characters` (via `TeamCharacters`)
    teams = db.relationship('Team_Character',back_populates='character',lazy=True)
#  `Games` ⟶ 1:M ⟶ `Characters` 
    game = db.relationship('Game', back_populates='characters', lazy=True)
    # `Images` ⟶ 1:1 ⟶ (`Users`, `Games`, `Teams`, `Characters`, `InventoryItems`)
    # Deleting a character will delete the image associated with the character
    image = db.relationship('Image',
                      back_populates='character',
                      uselist=False,
                      cascade='all, delete-orphan',
                      foreign_keys='Image.character_id')
    
    


# Attributes Model
class Attribute(db.Model):
    __tablename__ = 'attribute'
    #  `attribute_id` (Primary Key)
    # - `attribute_name` (e.g., "Strength", "Weakness", "Ability")
    # - `description` (Optional; e.g., explanation of the ability)
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    attribute_name = db.Column(db.String(50), unique=False, nullable=False)
    description = db.Column(db.String(200), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # Relationship to the intermediate Character_Attribute model
    characters = db.relationship('Character_Attribute', back_populates='attribute')
    

# Character Attributes Model
class Character_Attribute(db.Model):
    __tablename__ = 'characterattribute'
    # - `character_attribute_id` (Primary Key)
    # - `character_id` (Foreign Key referencing `Characters`)
    # - `attribute_id` (Foreign Key referencing `Attributes`)
    # - `attribute_value` (Optional; e.g., "Sword", "Axe", etc.)
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    # Composite Keys
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'),primary_key=True)
    attribute_id = db.Column(db.Integer, db.ForeignKey('attribute.id'),primary_key=True)
    attribute_value = db.Column(db.String(50), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # `Characters` ⟶ M:N ⟶ `Attributes` (via `CharacterAttributes`)
    character = db.relationship('Character', back_populates='attributes')
    attribute = db.relationship('Attribute', back_populates='characters')





# Inventory Items Model
class Inventory_Item(db.Model):
    __tablename__ = 'inventoryitem'
    # - `item_id` (Primary Key)
    # - `item_name`
    # - `description` (Optional; e.g., "A legendary sword with magical properties")
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    item_name =  db.Column(db.String(50), unique=False, nullable=False)
    description = db.Column(db.String(200), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # Relationship to the intermediate Character_Inventory model
    characters = db.relationship('Character_Inventory',back_populates='inventory_item')
    # `Images` ⟶ 1:1 ⟶ (`Users`, `Games`, `Teams`, `Characters`, `InventoryItems`)
    # Deleting an inventory_item will delete the image associated with the inventory_item
    image = db.relationship('Image',
                       back_populates='inventory_item',
                       uselist=False,
                       cascade='all, delete-orphan',
                       foreign_keys='Image.inventory_item_id')
    


# Character Inventory Model
class Character_Inventory(db.Model):
    __tablename__ = 'characterinventory'
    # - `character_inventory_id` (Primary Key)
    # - `character_id` (Foreign Key referencing `Characters`)
    # - `item_id` (Foreign Key referencing `InventoryItems`)
    # - `quantity` (Optional; e.g., "2 swords")
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    # Composite Keys
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'),primary_key=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventoryitem.id'),primary_key=True)
    quantity = db.Column(db.Integer, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # - `Characters` ⟶ M:N ⟶ `InventoryItems` (via `CharacterInventory`)
    character = db.relationship('Character', back_populates='inventory_items')
    inventory_item = db.relationship('Inventory_Item', back_populates='characters')



# User Teams Model
class User_Team(db.Model):
    __tablename__ = 'userteam'
    # - `user_team_id` (Primary Key)
    # - `user_id` (Foreign Key referencing `Users`)
    # - `team_id` (Foreign Key referencing `Teams`)
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # `Users` ⟶ 1:M ⟶ `UserTeams`
    user = db.relationship('User', back_populates='user_teams')
    # `Teams` ⟶ 1:M ⟶ `UserTeams`  
    team = db.relationship('Team', back_populates='user_teams')


# Team Characters Model
class Team_Character(db.Model):
    __tablename__ = 'team_character'
    # - `team_character_id` (Primary Key)
    # - `team_id` (Foreign Key referencing `Teams`)
    # - `character_id` (Foreign Key referencing `Characters`)
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    # Composite Keys
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'),primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'),primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    # `Teams` ⟶ M:N ⟶ `Characters` (via `TeamCharacters`)
    team = db.relationship('Team', back_populates='characters')
    character = db.relationship('Character', back_populates='teams')



# Strategy Model
class Strategy(db.Model):
    __tablename__ = 'strategy'
    # - `strategy_id` (Primary Key)
    # - `team_id` (Foreign Key referencing `Teams`)
    # - `description`
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id')) 
    description = db.Column(db.String(200), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
     # `Teams` ⟶ 1:M ⟶ `Strategies`
     # Deleting a team will delete a strategy
    team = db.relationship('Team',back_populates='strategies',lazy=True)


# Image Model
class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    
    # Specific foreign keys (only one will be non-NULL per record)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventoryitem.id'), nullable=True)
    
    # Common image fields
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships (now properly linked to specific FKs)
    user = db.relationship('User', back_populates='image', foreign_keys=[user_id])
    game = db.relationship('Game', back_populates='image', foreign_keys=[game_id])
    team = db.relationship('Team', back_populates='image', foreign_keys=[team_id])
    character = db.relationship('Character', back_populates='image', foreign_keys=[character_id])
    inventory_item = db.relationship('Inventory_Item', back_populates='image', foreign_keys=[inventory_item_id])

  
