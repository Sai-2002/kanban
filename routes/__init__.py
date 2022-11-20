from flask import Flask
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testsecretkey'
version = "/api/v1"

redis_cli = redis.Redis(host="localhost", port=6379, password="", decode_responses=True)


from routes import user_action
from routes import home
from routes import list_actions
from routes import card_actions