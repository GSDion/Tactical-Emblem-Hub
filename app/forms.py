from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import ListWidget, CheckboxInput

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class TeamInfoForm(FlaskForm):
    team_name = StringField('Team Name', validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])

class GameSelectionForm(FlaskForm):
    game_id = SelectField('Game', coerce=int, validators=[DataRequired()])

class CharacterSelectionForm(FlaskForm):
    characters = MultiCheckboxField('Characters', coerce=int)
    
class StrategyForm(FlaskForm):
    strategy_description = TextAreaField('Strategy Plan', validators=[
        DataRequired(),
        Length(min=50)
    ])