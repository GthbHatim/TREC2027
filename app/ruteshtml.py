from app import app
from app.extensions import db
from flask import request
from flask import render_template
from app.models import Alumne
from app.models import Ordinador

@app.route("/alumnes/html")
def llistar_alumnes():
    return render_template("base.html")
    
@app.route("/alumnes/html/veure")
def veure_alumnes():
    alumnes = db.session.execute(db.select(Alumne)).scalars().all()
    return render_template("alumnes/veure.html", alumnes=alumnes)

@app.route("/ordinadors/html/veure")
def veure_ordinadors():
    ordinadors = db.session.execute(db.select(Ordinador)).scalars().all()
    return render_template("ordinadors/veure.html", ordinadors=ordinadors)

