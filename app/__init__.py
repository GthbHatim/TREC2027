from flask import Flask
from app.extensions import db
from app import models  

#  create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

with app.app_context():
    db.create_all()