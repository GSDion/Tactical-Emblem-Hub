# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_mail import Mail

# db and csrf need to be defined outside any function or class,
# so they are accessible globally throughout the application.
db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()