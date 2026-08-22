from flask import Flask
from app.extensions import db

#  create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

from app import models 
from app import alumnes
from app import ordinadorshistorial

with app.app_context():
    db.create_all()

