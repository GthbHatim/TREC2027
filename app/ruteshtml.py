from app import app
from app.extensions import db
from flask import request
from flask import render_template
from app.models import Alumne
from app.models import Ordinador
from app.models import Historial

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

@app.route("/historial/html/veure")
def veure_historial():
    historial = db.session.execute(db.select(Historial)).scalars().all()
    dades = []
    for h in historial:
        alumne = db.session.get(Alumne, h.alumne_id)
        nom = alumne.nom if alumne else None
        dades.append({"id": h.id, "accio": h.accio, "data": h.data, "ordinador_id": h.ordinador_id, "alumne_id": h.alumne_id, "alumne_nom": nom})
    return render_template("historial/veure.html", historial=dades)

@app.route("/benvingut")
def benvingut():
    return render_template("benvinguda.html")