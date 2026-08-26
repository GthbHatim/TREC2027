from app import app
from app.extensions import db
from flask import request, url_for
from flask import render_template
from app.models import Alumne
from app.models import Ordinador
from app.models import Historial
from flask import redirect

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

@app.route("/alumnes/html/formulari")
def formulari_alumnes():
    return render_template("alumnes/afegir.html")

@app.route("/ordinadors/html/formulari")
def formulari_ordinadors():
    return render_template("ordinadors/afegir.html")

@app.route("/ordinadors/nou/form", methods=["POST"])
def post_ordinador():
    nou = Ordinador(num_serie=request.form["num_serie"], ref_diputacio=request.form["ref_diputacio"], model=request.form["model"])

    db.session.add(nou)
    db.session.commit()

    alumne_id = request.form.get("alumne_id")
    if alumne_id:
        alumne = db.session.get(Alumne, alumne_id)
        if not alumne:
            return {"error": "Alumne no trobat"}, 404
        nou.alumne_id = alumne.id
        nou.estat = "assignat"
        nou2 = Historial(alumne_id = nou.alumne_id, ordinador_id = nou.id, accio = "assignat")
        db.session.add(nou2)
        db.session.commit()
    return redirect(url_for('veure_ordinadors'))

@app.route("/alumnes/nou/form", methods=["POST"])
def post_alumne():
    nou = Alumne(nom=request.form["nom"], identificador=request.form["identificador"], curs=request.form["curs"], email=request.form["email"])

    db.session.add(nou)
    db.session.commit()

    ordinador_id = request.form.get("ordinador_id")
    if ordinador_id:
        ordinador = db.session.get(Ordinador, ordinador_id)
        if not ordinador:
            return {"error": "Ordinador no trobat"}, 404

        ordinador.alumne_id = nou.id
        ordinador.estat = "assignat"

        historial = Historial(alumne_id=nou.id, ordinador_id=ordinador.id, accio="assignat")
        db.session.add(historial)
        db.session.commit()

    return redirect(url_for("veure_alumnes"))
