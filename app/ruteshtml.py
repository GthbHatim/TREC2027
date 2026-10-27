#Imports
from csv import writer
from io import BytesIO
import io
from flask import flash, send_file
import pandas
from sqlalchemy import String, ForeignKey, DateTime, func
from pandas import options
from pandas import DataFrame
from pandas import ExcelWriter
from app import alumnes, app
from app.extensions import db
from flask import request, url_for
from flask import render_template
from app.models import ESTATS_ORDINADOR, Alumne, ACCIONS_HISTORIAL, CURSOS
from app.models import Ordinador
from app.models import Historial
from flask import redirect
from pandas import Timestamp
import pandas as pd
from pathlib import Path
from markupsafe import Markup
from datetime import datetime
from sqlalchemy import or_ 

#Diccionaris
modes = ("auto", "clar", "fosc")

FILTRES = {
    "amb": (Alumne.estat == "actiu", Alumne.ordinador.has()),
    "sense": (Alumne.estat == "actiu", ~Alumne.ordinador.has()),
    "baixa": (Alumne.estat == "de baixa",),
}

# Funcions golbals per a les plantilles

@app.context_processor
def inject_tema():
    ara = request.full_path.rstrip("?")
    if request.cookies.get("tema") not in modes:
        return dict(modes=modes, ACCIONS=ACCIONS_HISTORIAL, theme="auto", ara=ara, ESTATS=ESTATS_ORDINADOR)
    return dict(modes=modes, ACCIONS=ACCIONS_HISTORIAL, theme=request.cookies.get("tema", "auto"), ara=ara, ESTATS=ESTATS_ORDINADOR)
def tornar(endpoint):
    seguent = request.form.get("seguent", "")
    if seguent.startswith("/") and not seguent.startswith("//"):
        return redirect(seguent)
    return redirect(url_for(endpoint))

@app.route("/tema", methods=["POST"])
def canviar_tema():
    tema = request.form.get("tema", "auto")
    resposta = tornar("benvingut")
    if tema in modes:
        resposta.set_cookie("tema", tema, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return resposta

@app.template_global()
def get_icon(nom, classe="size-4"):
    folder = Path(app.static_folder)
    file = folder / "icons" / f"{nom}.svg"
    icon = file.read_text()
    icon = icon.replace("<svg", f"<svg class='{classe}'")
    return Markup(icon)

@app.template_filter("data")
def format_data(valor):
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y %H:%M")
    return "Data no disponible"

@app.template_filter("fa")
def fa(valor):
    """{{ h.data|fa }} -> avui, ahir, fa 3 dies, fa 2 setmanes, fa 1 mes..."""
    if isinstance(valor, datetime):
        dies = (datetime.now().date() - valor.date()).days
        if dies <= 0:
            return "avui"
        elif dies == 1:
            return "ahir"
        elif dies < 7:
            return f"fa {dies} dies"
        elif dies < 30:
            setmanes = dies // 7
            if setmanes == 1:
                return "fa 1 setmana"
            return f"fa {setmanes} setmanes"
        else:
            mesos = dies // 30
            if mesos == 1:
                return "fa 1 mes"
            return f"fa {mesos} mesos"

    return ""

def apuntar(accio, ordinador_id, alumne_id=None):
    historial = Historial(accio=accio, ordinador_id=ordinador_id, alumne_id=alumne_id)
    db.session.add(historial)

def retirar_alumne(ordinador, accio="retirat"):
    alumne = db.session.get(Alumne, ordinador.alumne_id)
    if alumne:
        apuntar(accio, ordinador.id, alumne.id)
        ordinador.alumne_id = None
    return alumne


#Rutes HTML

@app.route('/')
def index():
    return redirect(url_for('benvingut'))

@app.route("/benvingut")
def benvingut():
    return render_template("benvinguda.html")
    
def search_alumnes(query_a, q, curs):
    if curs in CURSOS:
        query_a = query_a.where(Alumne.curs == curs)
    if q:
        pattern = f"%{q}%"
        query_a = query_a.outerjoin(Alumne.ordinador)
        query_a = query_a.where(or_(
            func.unaccent(Alumne.nom).ilike(func.unaccent(pattern)),
            Alumne.identificador.ilike(pattern),
            Alumne.email.ilike(pattern),
            Ordinador.sace.ilike(pattern),
            Ordinador.num_serie.ilike(pattern),
            Ordinador.model.ilike(pattern),
        ))
    return query_a

@app.route("/alumnes/html/veure")
def veure_alumnes():
    q = request.args.get("q", "").strip()
    estat = request.args.get("estat", "")
    curs = request.args.get("curs", "")
    query_a = search_alumnes(db.select(Alumne), q, curs)
    if estat in FILTRES:
        query_a = query_a.where(*FILTRES[estat])
    alumnes = db.session.execute(query_a.order_by(Alumne.nom)).scalars().all()
    recompte = {}
    for clau, condicions in FILTRES.items():
        consulta = search_alumnes(db.select(func.count(Alumne.id)), q, curs).where(*condicions)
        recompte[clau] = db.session.scalar(consulta)
    return render_template("alumnes/veure.html", alumnes=alumnes, recompte=recompte,q=q, estat=estat, curs=curs, cursos=CURSOS)

def search_ordinadors(query_o, q):
    if q:
        pattern = f"%{q}%"
        query_o = query_o.outerjoin(Ordinador.alumne)
        query_o = query_o.where(or_(
            Ordinador.num_serie.ilike(pattern),
            Ordinador.sace.ilike(pattern),
            Ordinador.model.ilike(pattern),
            func.unaccent(Alumne.nom).ilike(func.unaccent(pattern)),
        ))
    return query_o

@app.route("/ordinadors/html/veure")
def veure_ordinadors():
    q = request.args.get("q", "").strip()
    estat = request.args.get("estat", "")
    query_o = db.select(Ordinador)
    if estat and estat in ESTATS_ORDINADOR:
        query_o = query_o.where(Ordinador.estat == estat)
    query_o = search_ordinadors(query_o, q)
    ordinadors = db.session.execute(query_o.order_by(Ordinador.sace)).scalars().all()
    recompte = dict(db.session.execute(
    search_ordinadors(db.select(Ordinador.estat, func.count()), q).group_by(Ordinador.estat)).all())
    return render_template("ordinadors/veure.html", ordinadors=ordinadors, q=q, estat=estat, recompte=recompte)

@app.route("/historial/html/veure")
def veure_historial():
    historial = db.session.execute(db.select(Historial).order_by(Historial.id)).scalars().all()
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
    return render_template("assignarhstrlr.html", historial=dades)

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
        apuntar("assignat", nou.id, alumne.id)
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

@app.route('/ordinadors/html/<int:ordinador_id>/reparar', methods=['POST'])
def reparar_ordinador_html(ordinador_id):
    ordinador = db.session.get(Ordinador, ordinador_id)
    if not ordinador:
        flash ("404: Ordinador no trobat.", "error")
        return tornar("veure_ordinadors")
    if ordinador.estat == "de baixa" or ordinador.estat == "reparacio":
        flash ("No es pot reparar un ordinador que està de baixa o ja sent reparat.", "avis")
        return tornar("veure_ordinadors")
    alumne = retirar_alumne(ordinador, accio="retirat (reparació)")
    ordinador.estat = "reparacio"
    apuntar("reparacio", ordinador.id, alumne.id if alumne else None)
    db.session.commit()
    flash (f"Ordinador {ordinador.sace} enviat a reparació.", "ok")
    return tornar("veure_ordinadors")

@app.route('/ordinadors/html/<int:ordinador_id>/baixa', methods=['POST'])
def baixa_ordinador_html(ordinador_id):
    ordinador = db.session.get(Ordinador, ordinador_id)
    if not ordinador:
        flash ("404: Ordinador no trobat.", "error")
        return tornar("veure_ordinadors")
    if ordinador.estat == "de baixa":
        flash ("No es pot donar de baixa un ordinador que ja ho està.", "avis")
        return tornar("veure_ordinadors")
    alumne = retirar_alumne(ordinador, accio="retirat (baixa)")
    ordinador.estat = "de baixa"
    apuntar("de baixa", ordinador.id, alumne.id if alumne else None)
    db.session.commit()
    flash (f"Ordinador {ordinador.sace} donat de baixa.", "ok")
    return tornar("veure_ordinadors")

@app.route('/ordinadors/html/<int:ordinador_id>/restaurar', methods=['POST'])
def restaurar_ordinador_html(ordinador_id):
    ordinador = db.session.get(Ordinador, ordinador_id)
    if not ordinador:
        flash ("404: Ordinador no trobat.", "error")
        return tornar("veure_ordinadors")
    if ordinador.estat != "de baixa":
        flash ("Només es poden restaurar ordinadors que estiguin de baixa.", "avis")
        return tornar("veure_ordinadors")
    ordinador.estat = "emmagatzemat"
    apuntar("restaurat", ordinador.id)
    db.session.commit()
    flash (f"Ordinador {ordinador.sace} restaurat i emmagatzemat.", "ok")
    return tornar("veure_ordinadors")

@app.route('/ordinadors/html/<int:ordinador_id>/emmagatzemar', methods=['POST'])
def emmagatzemar_ordinador_html(ordinador_id):
    ordinador = db.session.get(Ordinador, ordinador_id)
    if not ordinador:
        flash ("404: Ordinador no trobat.", "error")
        return tornar("veure_ordinadors")
    if ordinador.estat == "reparacio":
        flash (f"Ordinador {ordinador.sace} marcat com a reparat i emmagatzemat.", "ok")
        ordinador.estat = "emmagatzemat"
        apuntar("emmagatzemat (reparació)", ordinador.id)
        db.session.commit()
        return tornar("veure_ordinadors")
    elif ordinador.estat == "assignat":
        alumne = retirar_alumne(ordinador, accio="retirat (emmagatzemat)")
    else:
        flash(f"El {ordinador.sace} no es pot guardar al magatzem: està {ESTATS_ORDINADOR[ordinador.estat].lower()}.", "avis")
        return tornar("veure_ordinadors")
    ordinador.estat = "emmagatzemat"
    apuntar("emmagatzemat", ordinador.id, alumne.id if alumne else None)
    db.session.commit()
    flash (f"Ordinador {ordinador.sace} emmagatzemat.", "ok")
    return tornar("veure_ordinadors")

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

    if ordinador.alumne_id is not None and ordinador.alumne_id != alumne.id:
        historial_retirada = Historial(
            alumne_id=ordinador.alumne_id,
            ordinador_id=ordinador.id,
            accio="retirat"
        )
        db.session.add(historial_retirada)
    if alumne.ordinador is not None and alumne.ordinador.id != ordinador.id:
        antic = alumne.ordinador
        historial_retirada = Historial(
            alumne_id=alumne.id,
            ordinador_id=antic.id,
            accio="retirat"
        )
        antic.estat = "emmagatzemat"
        antic.alumne_id = None
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
    return redirect(url_for("formulari_assignar_after"))

@app.route('/alumnes/html/<int:alumne_id>/baixa', methods=['POST'])
def baixa_alumne_html(alumne_id):
    alumne = db.session.get(Alumne, alumne_id)
    if not alumne:
        flash ("404: Alumne no trobat.", "error")
        return tornar("veure_alumnes")
    if alumne.estat == "de baixa":
        flash ("No es pot donar de baixa un alumne que ja ho està.", "avis")
        return tornar("veure_alumnes")
    if alumne.ordinador:
        ordinador = alumne.ordinador
        retirar_alumne(ordinador, "retirat (baixa alumne)")
        ordinador.estat = "emmagatzemat"
    alumne.estat = "de baixa"
    db.session.commit()
    flash (f"{alumne.nom} amb l'identificador {alumne.identificador} ha estat donat de baixa.", "ok")
    return tornar("veure_alumnes")

@app.route('/alumnes/html/<int:alumne_id>/restaurar', methods=['POST'])
def restaurar_alumne_html(alumne_id):
    alumne = db.session.get(Alumne, alumne_id)
    if not alumne:
        flash ("404: Alumne no trobat.", "error")
        return tornar("veure_alumnes")
    if alumne.estat != "de baixa":
        flash ("Només es poden restaurar alumnes que estiguin de baixa.", "avis")
        return tornar("veure_alumnes")
    alumne.estat = "actiu"
    db.session.commit()
    flash (f"{alumne.nom} amb l'identificador {alumne.identificador} ha estat restaurat.", "ok")
    return tornar("veure_alumnes")


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
                historial = db.session.execute(db.select(Historial).order_by(Historial.id)).scalars().all()
                data = [{'id': h.id, 'accio': h.accio, 'data': h.data, 'ordinador_id': h.ordinador_id, 'alumne_id': h.alumne_id} for h in historial]
                df = pd.DataFrame(data)
                dataframes['historial'] = df
            elif key == 'alumnes':
                alumnes = db.session.execute(db.select(Alumne).order_by(Alumne.id)).scalars().all()
                data = [{'id': a.id, 'nom': a.nom, 'identificador': a.identificador, 'curs': a.curs, 'email': a.email, 'estat': a.estat, 'id_ordinador': a.ordinador.id if a.ordinador else None} for a in alumnes]
                df = pd.DataFrame(data)
                dataframes['alumnes'] = df
            elif key == 'ordinadors':
                ordinadors = db.session.execute(db.select(Ordinador).order_by(Ordinador.id)).scalars().all()
                data = [{'id': o.id, 'num_serie': o.num_serie, 'sace': o.sace, 'model': o.model, 'estat': o.estat} for o in ordinadors]
                df = pd.DataFrame(data)
                dataframes['ordinadors'] = df
    if not dataframes:
        return render_template('export.html', error="Has de marcar almenys una taula.")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"backup_{fecha_actual}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route("/ordinadors/html/<int:ordinador_id>")
def fitxa_ordinador(ordinador_id):
    ordinador = db.get_or_404(Ordinador, ordinador_id)
    historial = db.session.execute(
        db.select(Historial).where(Historial.ordinador_id == ordinador_id).order_by(Historial.data.desc())).scalars().all()
    return render_template("ordinadors/fitxa.html", ordinador=ordinador, historial=historial)

@app.route("/alumnes/html/<int:alumne_id>")
def fitxa_alumne(alumne_id):
    alumne = db.get_or_404(Alumne, alumne_id)
    historial = db.session.execute(
        db.select(Historial).where(Historial.alumne_id == alumne_id).order_by(Historial.data.desc())).scalars().all()
    return render_template("alumnes/fitxa.html", alumne=alumne, historial=historial)

@app.route('/html/exemples')
def exemples_html():
    return render_template('exemples_document/basexemple.html')

@app.route('/html/exemples/1')
def exemples_1_html():
    return render_template('exemples_document/fillexemple.html')



