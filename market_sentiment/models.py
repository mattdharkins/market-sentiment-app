# Standard
from distutils.log import Log
import uuid
from datetime import datetime
import secrets

# 3rd party imports
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from flask_marshmallow import Marshmallow

# Adding Flask Security for Passwords
from werkzeug.security import generate_password_hash, check_password_hash



db = SQLAlchemy()
login_manager = LoginManager()
ma = Marshmallow()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key = True)
    first_name = db.Column(db.String(50), nullable = True, default='')
    last_name = db.Column(db.String(50), nullable = True, default = '')
    email = db.Column(db.String(150), nullable = False)
    password = db.Column(db.String, nullable = True, default = '')
    g_auth_verify = db.Column(db.Boolean, default = False)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __init__(self,email,first_name = '', last_name = '', id = '', password = '', g_auth_verify = False):
        self.id = self.set_id()
        self.first_name = first_name
        self.last_name = last_name
        self.password = self.set_password(password)
        self.email = email
        self.g_auth_verify = g_auth_verify

    def set_id(self):
        return str(uuid.uuid4())

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash


    def __repr__(self):
        return f'User {self.email} has been added to the database'



class OptionsInfo(db.Model):
    __tablename__ = 'optionsInfo'
    symbol = db.Column(db.String(256), primary_key=True)
    quoteDate = db.Column(db.String(10), primary_key=True)
    frontDelta = db.Column(db.Numeric)
    frontStrike = db.Column(db.Numeric)
    backStrike = db.Column(db.Numeric)
    spreadPrice = db.Column(db.Numeric)
    spreadWidth = db.Column(db.Numeric)
    sentiment = db.Column(db.String(30))

    def __init__(self) -> None:
        super().__init__()

# Creation of API Schema via the Marshmallow Object
class OptionsInfoSchema(ma.Schema):
    class Meta:
        fields = ['symbol', 'date', 'frontDelta', 'frontStrike', 'backStrike', 'spreadPrice', 'spreadWidth', 'sentiment']

options_info_schema = OptionsInfoSchema()
options_infos_schema = OptionsInfoSchema(many = True)
