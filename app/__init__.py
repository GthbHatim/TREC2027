import os
from dotenv import load_dotenv
from flask import Flask
from app.extensions import db

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db.init_app(app)

from app import models
from app import alumnes
from app import ordinadorshistorial
from app import ruteshtml

with app.app_context():
    db.create_all()

