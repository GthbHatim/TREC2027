import os
from dotenv import load_dotenv
from flask import Flask
from app.extensions import db
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db.init_app(app)

auth = HTTPBasicAuth()

users = {
    os.environ.get('AUTH_USER'): generate_password_hash(os.environ.get('AUTH_PASSWORD'))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username], password):
        return username

@app.before_request
def require_auth():
    return auth.login_required(lambda: None)()

from app import models
from app import alumnes
from app import ordinadorshistorial
from app import ruteshtml

with app.app_context():
    db.create_all()