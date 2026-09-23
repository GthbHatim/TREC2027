from csv import writer
from io import BytesIO
import io
from flask import send_file
import pandas
from sqlalchemy import String, ForeignKey, DateTime
from pandas import options
from pandas import DataFrame
from pandas import ExcelWriter
from app import alumnes, app
from app.extensions import db
from flask import request, url_for
from flask import render_template
from app.models import Alumne
from app.models import Ordinador
from app.models import Historial
from flask import redirect
from pandas import Timestamp
import pandas as pd

@app.route('/')
def index():
    return redirect(url_for('benvingut'))

@app.route("/benvingut")
def benvingut():
    return render_template("benvinguda.html")

@app.route("/alumnes/html")
def llistar_alumnes():
    return render_template("base.html")
    
@app.route("/alumnes/html/veure")
def veure_alumnes():
    alumnes = db.session.execute(db.select(Alumne)).scalars().all()
    return render_template("alumnes/veure.html", alumnes=alumnes)

@app.route("/alumnes/html/dark/veure")
def veure_alumnes_dark():
    alumnes = db.session.execute(db.select(Alumne)).scalars().all()
    return render_template("darkmode_test/alumnes/veure.html", alumnes=alumnes)

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
    dades.reverse()
    return render_template("historial/veure.html", historial=dades)

@app.route("/assignar/html/form")
def formulari_assignar():
    return render_template("assignar.html")

@app.route("/assignar/html/form/after")
def formulari_assignar_after():
    historial = db.session.execute(db.select(Historial).order_by(Historial.data.desc()).limit(7)).scalars()
    dades = []
    for h in historial:
        alumne = db.session.get(Alumne, h.alumne_id)
        nom = alumne.nom if alumne else None
        dades.append({"id": h.id, "accio": h.accio, "data": h.data, "ordinador_id": h.ordinador_id, "alumne_id": h.alumne_id, "alumne_nom": nom})
    dades.reverse()
    return render_template("assignarhstrl.html", historial=dades)

@app.route("/alumnes/html/formulari")
def formulari_alumnes():
    return render_template("alumnes/afegir.html")

@app.route("/alumnes/html/formulari/after")
def formulari_alumnes_after():
    alumnes = db.session.execute(db.select(Alumne).order_by(Alumne.id.desc()).limit(7)).scalars()
    return render_template("alumnes/afegir_after.html", alumnes=alumnes)

@app.route("/ordinadors/html/formulari")
def formulari_ordinadors():
    return render_template("ordinadors/afegir.html")

@app.route("/ordinadors/html/formulari/after")
def formulari_ordinadors_after():
    ordinadors = db.session.execute(db.select(Ordinador).order_by(Ordinador.id.desc()).limit(7)).scalars()
    return render_template("ordinadors/afegir_after.html", ordinadors=ordinadors)

@app.route("/ordinadors/nou/form", methods=["POST"])
def post_ordinador():
    nou = Ordinador(num_serie=request.form["num_serie"], sace=request.form["sace"], model=request.form["model"])

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
    return redirect(url_for('formulari_ordinadors_after'))

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

    return redirect(url_for("formulari_alumnes_after"))

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
    
    alumnes_assignats = db.session.execute(db.select(Alumne).filter_by(id=ordinador.alumne_id)).scalars().all()

    for alumne in alumnes_assignats:
        historial = Historial(
            alumne_id=alumne.id,
            ordinador_id=ordinador.id,
            accio="retirat (emmagatzemat)"
        )
        db.session.add(historial)

    ordinador.alumne_id = None
    ordinador.estat = "emmagatzemat"

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
    historial = db.session.execute(db.select(Historial).order_by(Historial.data.desc()).limit(7)).scalars()
    dades = []
    for h in historial:
        alumne = db.session.get(Alumne, h.alumne_id)
        nom = alumne.nom if alumne else None
        dades.append({"id": h.id, "accio": h.accio, "data": h.data, "ordinador_id": h.ordinador_id, "alumne_id": h.alumne_id, "alumne_nom": nom})
    dades.reverse()
    return render_template("/assignarhstrl.html", historial=dades)

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

@app.route('/alumnes/html/editar', methods=['GET'])
def editar_alumne_html():
    alumne_id = request.args.get('alumne_id')
    alumne = db.session.get(Alumne, alumne_id)

    if not alumne:
        return redirect(url_for('veure_alumnes'))

    return render_template('alumnes/editar.html', alumne=alumne)

@app.route('/alumnes/html/actualitzar/<int:alumne_id>', methods=['POST'])
def actualitzar_alumne_html(alumne_id):
    alumne = db.session.get(Alumne, alumne_id)

    if not alumne:
        return redirect(url_for('veure_alumnes'))

    alumne.nom = request.form.get('nom')
    alumne.identificador = request.form.get('identificador')
    alumne.curs = request.form.get('curs')
    alumne.email = request.form.get('email')

    db.session.commit()
    return redirect(url_for('veure_alumnes'))

@app.route('/html/export')
def exportar ():
    return render_template('export.html')

# --- Mode fosc ---------------------------------------------------------
# Cada ruta clara te la seva bessona fosca, que fa servir la mateixa
# consulta pero renderitza la plantilla de darkmode_test/.

PARELLES_FOSQUES = {
    'benvingut': 'benvingut_dark',
    'veure_alumnes': 'veure_alumnes_dark',
    'formulari_alumnes': 'formulari_alumnes_dark',
    'formulari_alumnes_after': 'formulari_alumnes_after_dark',
    'editar_alumne_html': 'editar_alumne_html_dark',
    'veure_ordinadors': 'veure_ordinadors_dark',
    'formulari_ordinadors': 'formulari_ordinadors_dark',
    'formulari_ordinadors_after': 'formulari_ordinadors_after_dark',
    'veure_historial': 'veure_historial_dark',
    'formulari_assignar': 'formulari_assignar_dark',
    'formulari_assignar_after': 'formulari_assignar_after_dark',
    'exportar': 'exportar_dark',
}

PARELLES_CLARES = {fosca: clara for clara, fosca in PARELLES_FOSQUES.items()}


@app.context_processor
def injectar_toggle():
    """Dona a les plantilles l'URL de la mateixa pagina en l'altre mode."""
    def toggle_url():
        bessona = PARELLES_FOSQUES.get(request.endpoint) or PARELLES_CLARES.get(request.endpoint)
        if not bessona:
            return None
        parametres = dict(request.view_args or {})
        parametres.update(request.args.to_dict())
        return url_for(bessona, **parametres)
    return {'toggle_url': toggle_url}


def dades_historial(historial):
    dades = []
    for h in historial:
        alumne = db.session.get(Alumne, h.alumne_id)
        nom = alumne.nom if alumne else None
        dades.append({"id": h.id, "accio": h.accio, "data": h.data, "ordinador_id": h.ordinador_id, "alumne_id": h.alumne_id, "alumne_nom": nom})
    dades.reverse()
    return dades


@app.route("/benvingut/dark")
def benvingut_dark():
    return render_template("darkmode_test/benvinguda_dark.html")

@app.route("/alumnes/html/dark/formulari")
def formulari_alumnes_dark():
    return render_template("darkmode_test/alumnes/afegir.html")

@app.route("/alumnes/html/dark/formulari/after")
def formulari_alumnes_after_dark():
    alumnes = db.session.execute(db.select(Alumne).order_by(Alumne.id.desc()).limit(7)).scalars()
    return render_template("darkmode_test/alumnes/afegir_after.html", alumnes=alumnes)

@app.route("/alumnes/html/dark/editar", methods=['GET'])
def editar_alumne_html_dark():
    alumne_id = request.args.get('alumne_id')
    alumne = db.session.get(Alumne, alumne_id)

    if not alumne:
        return redirect(url_for('veure_alumnes_dark'))

    return render_template("darkmode_test/alumnes/editar.html", alumne=alumne)

@app.route("/ordinadors/html/dark/veure")
def veure_ordinadors_dark():
    ordinadors = db.session.execute(db.select(Ordinador)).scalars().all()
    return render_template("darkmode_test/ordinadors/veure.html", ordinadors=ordinadors)

@app.route("/ordinadors/html/dark/formulari")
def formulari_ordinadors_dark():
    return render_template("darkmode_test/ordinadors/afegir.html")

@app.route("/ordinadors/html/dark/formulari/after")
def formulari_ordinadors_after_dark():
    ordinadors = db.session.execute(db.select(Ordinador).order_by(Ordinador.id.desc()).limit(7)).scalars()
    return render_template("darkmode_test/ordinadors/afegir_after.html", ordinadors=ordinadors)

@app.route("/historial/html/dark/veure")
def veure_historial_dark():
    historial = db.session.execute(db.select(Historial)).scalars().all()
    return render_template("darkmode_test/historial/veure.html", historial=dades_historial(historial))

@app.route("/assignar/html/dark/form")
def formulari_assignar_dark():
    return render_template("darkmode_test/assignar_dark.html")

@app.route("/assignar/html/dark/form/after")
def formulari_assignar_after_dark():
    historial = db.session.execute(db.select(Historial).order_by(Historial.data.desc()).limit(7)).scalars()
    return render_template("darkmode_test/assignarhstrl_dark.html", historial=dades_historial(historial))

@app.route("/html/dark/export")
def exportar_dark():
    return render_template("darkmode_test/export_dark.html")

# --- Fi mode fosc ------------------------------------------------------

@app.route('/html/export/action', methods=['POST'])
def exportar_post():
    options = {
        'historial': bool(request.form.get('historial')),
        'alumnes': bool(request.form.get('alumnes')),
        'ordinadors': bool(request.form.get('ordinadors'))
    }

    dataframes = {}
    fecha_actual = pandas.Timestamp.now().strftime("%d-%m-%Y_%H-%M-%S")

    for key, value in options.items():
        if value:
            if key == 'historial':
                historial = db.session.execute(db.select(Historial)).scalars().all()
                data = [{'id': h.id, 'accio': h.accio, 'data': h.data, 'ordinador_id': h.ordinador_id, 'alumne_id': h.alumne_id} for h in historial]
                df = pd.DataFrame(data)
                dataframes['historial'] = df
            elif key == 'alumnes':
                alumnes = db.session.execute(db.select(Alumne)).scalars().all()
                data = [{'id': a.id, 'nom': a.nom, 'identificador': a.identificador, 'curs': a.curs, 'email': a.email} for a in alumnes]
                df = pd.DataFrame(data)
                dataframes['alumnes'] = df
            elif key == 'ordinadors':
                ordinadors = db.session.execute(db.select(Ordinador)).scalars().all()
                data = [{'id': o.id, 'num_serie': o.num_serie, 'sace': o.sace, 'model': o.model, 'estat': o.estat} for o in ordinadors]
                df = pd.DataFrame(data)
                dataframes['ordinadors'] = df

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"backup_{fecha_actual}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/html/test')
def test_html():
    return render_template('tests/test.html')