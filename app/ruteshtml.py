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

@app.route("/assignar/html/form")
def formulari_assignar():
    return render_template("assignar.html")

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

@app.route('/alumnes/html/restaurar', methods=['POST'])
def restaurar_alumne_html():
    alumne_id = request.form.get('alumne_id')
    alumne = db.session.get(Alumne, alumne_id)
    
    if not alumne:
        return redirect(url_for('veure_alumnes'))

    alumne.estat = "actiu"
    db.session.commit() 
    
    return redirect(url_for('veure_alumnes'))

@app.route('/ordinadors/html/reparar', methods=['POST'])
def reparar_ordinador_html():
    num_serie = request.form.get('num_serie')
    ordinador = Ordinador.query.filter_by(num_serie=num_serie).first()
    
    if not ordinador:
        # manejar error, ordenador no encontrado
        return redirect(url_for('veure_ordinadors'))
    
    ordinador.estat = 'En reparació'
    db.session.commit() 
    
    return redirect(url_for('veure_ordinadors'))

@app.route('/ordinadors/html/baixa', methods=['POST'])
def baixa_ordinador_html():
    num_serie = request.form.get('num_serie')
    ordinador = Ordinador.query.filter_by(num_serie=num_serie).first()
    
    if not ordinador:
        return redirect(url_for('veure_ordinadors'))
    
    ordinador.estat = ' de baixa'
    ordinador.alumne_id = None 
    db.session.commit() 
    
    return redirect(url_for('veure_ordinadors'))

@app.route('/ordinadors/html/emmagatzemar', methods=['POST'])
def emmagatzemar_ordinador_html():
    num_serie = request.form.get('num_serie')
    ordinador = Ordinador.query.filter_by(num_serie=num_serie).first()
    
    if not ordinador:
        return redirect(url_for('veure_ordinadors'))
    
    ordinador.estat = 'emmagatzemat'
    ordinador.alumne_id = None 
    db.session.commit() 
    
    return redirect(url_for('veure_ordinadors'))

@app.route('/assignar/html', methods=['POST'])
def assignar_ordinador_html():
    ordinador_id = request.form.get('ordinador_id')
    alumne_id = request.form.get('alumne_id')

    if not ordinador_id or not alumne_id:
        return {"error": "Falten dades"}, 404

    ordinador = db.session.get(Ordinador, ordinador_id)
    if not ordinador:
        return {"error": "Ordinador no trobat"}, 404

    alumne = db.session.get(Alumne, alumne_id)
    if not alumne:
        return {"error": "Alumne no trobat"}, 404

    if ordinador.alumne_id is not None:
        historial_retirada = Historial(
            alumne_id=ordinador.alumne_id,
            ordinador_id=ordinador.id,
            accio="retirat"
        )
        db.session.add(historial_retirada)

    ordinador.alumne_id = alumne.id
    ordinador.estat = "assignat"

    historial_assignacio = Historial(
        alumne_id=alumne.id,
        ordinador_id=ordinador.id,
        accio="assignat"
    )
    db.session.add(historial_assignacio)

    db.session.commit()
    return redirect(url_for('veure_historial'))

@app.route('/alumnes/html/baixa', methods=['POST'])
def baixa_alumne_html():
    alumne_id = request.form.get('alumne_id')
    alumne = db.session.get(Alumne, alumne_id)
    
    if not alumne:
        return redirect(url_for('veure_alumnes'))

    alumne.estat = "de baixa"

    ordinadors_assignats = db.session.execute(
        db.select(Ordinador).filter_by(alumne_id=alumne.id)
    ).scalars().all()

    for ordinador in ordinadors_assignats:
        historial = Historial(
            alumne_id=alumne.id,
            ordinador_id=ordinador.id,
            accio="retirat (baixa alumne)"
        )
        db.session.add(historial)

        ordinador.alumne_id = None
        ordinador.estat = "emmagatzemat"

    db.session.commit()
    return redirect(url_for('veure_alumnes'))