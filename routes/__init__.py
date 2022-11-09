from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testsecretkey'
version = "/api/v1"

from routes import user_action
from routes import home
from routes import list_actions
from routes import card_actions