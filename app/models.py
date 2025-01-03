import datetime
from flask_sqlalchemy import SQLAlchemy
from __init__ import db

'''
TO DO:
- DOCUMENT HOW RELATIONSHIPS ARE DEFINED IN CODE (Tactical_Emblem_Hub_Notes.md)
- use either back_populates OR backrefs. Not both.
'''
# User Model
class User(db.Model):
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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
    # `Users` ⟶ 1:M ⟶ `UserTeams`
    user_teams = db.relationship('User_Team', backref='user', lazy=True)


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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
    # `Games` ⟶ 1:M ⟶ `Teams`
    teams = db.relationship('Team', backref='game', lazy=True)
    #  `Games` ⟶ 1:M ⟶ `Characters` 
    characters = db.relationship('Character', backref='game', lazy=True)


# Team Model
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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
    # `Teams` ⟶ 1:M ⟶ `Strategies`
    strategies = db.relationship('Strategy', backref='team', lazy=True)
    # Relationship to the intermediate Team_Character model
    # `Teams` ⟶ M:N ⟶ `Characters` (via `TeamCharacters`)
    characters = db.relationship('Team_Character',back_populates='team')


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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
     # Relationship to the intermediate Character_Attribute model
    attributes = db.relationship('Character_Attribute', back_populates='character')
    # Relationship to the intermediate Character_Inventory model
    # # - `Characters` ⟶ M:N ⟶ `InventoryItems` (via `CharacterInventory`)
    inventory_items = db.relationship('Character_Inventory', back_populates='character')
    # Relationship to the intermediate Team_Character model
    # `Teams` ⟶ M:N ⟶ `Characters` (via `TeamCharacters`)
    teams = db.relationship('Team_Character',back_populates='character')
    
    


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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
    # `Characters` ⟶ M:N ⟶ `Attributes` (via `CharacterAttributes`)
    character = db.relationship('Character', back_populates='attributes')
    attribute = db.relationship('Attribute', back_populates='characters')

    __table_args__ = (
    db.PrimaryKeyConstraint('character_id', 'attribute_id'),
    )




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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
    # Relationship to the intermediate Character_Inventory model
    characters = db.relationship('Character_Inventory',back_populates='inventory_item')
    


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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
    # - `Characters` ⟶ M:N ⟶ `InventoryItems` (via `CharacterInventory`)
    character = db.relationship('Character', back_populates='inventory_items')
    inventory_item = db.relationship('Inventory_Item', back_populates='characters')
    __table_args__ = (
    db.PrimaryKeyConstraint('character_id', 'item_id'),
    )


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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification


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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
    # `Teams` ⟶ M:N ⟶ `Characters` (via `TeamCharacters`)
    team = db.relationship('Team', back_populates='characters')
    character = db.relationship('Character', back_populates='teams')
    __table_args__ = (
    db.PrimaryKeyConstraint('team_id', 'character_id'),
    )


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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification


# Image Model
class Image(db.Model):
    __tablename__ = 'image'
    # - `image_id` (Primary Key)
    # - `entity_type` (e.g., "Character", "Team", "InventoryItem", etc.)
    # - `entity_id` (Foreign Key referencing the associated entity)
    # - `image_url` or `image_path` (Path to the image file)
    # - `created_at` (Timestamp)
    # - `updated_at` (Timestamp)
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), unique=False, nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)  # The ID of the referenced entity
    image_url = db.Column(db.String(200), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC))  # Automatically set on creation
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.UTC), onupdate=datetime.now(datetime.UTC))  # Update on modification
    # `Images` ⟶ 1:1 ⟶ (`Users`, `Games`, `Teams`, `Characters`, `InventoryItems`)
    users = db.relationship('User', backref='image', uselist=False)
    games = db.relationship('Game', backref='image', uselist=False)
    teams = db.relationship('Team', backref='image', uselist=False)
    characters = db.relationship('Character', backref='image', uselist=False)
    inventory_items = db.relationship('Inventory_Item', backref='image', uselist=False)

    # Polymorphic relationship for ORM queries
    #When querying:
        # image = Image.query.filter_by(entity_type='Character', entity_id=1).first()
    __mapper_args__ = {
        "polymorphic_on": entity_type,
    }

