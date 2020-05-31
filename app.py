from flask import Flask
from flask_login import LoginManager

from model import db_session

app = Flask(__name__, template_folder='templates')
app.secret_key = 'super secret key'

session = db_session()
login = LoginManager(app)
