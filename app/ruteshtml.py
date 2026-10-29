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
from sqlalchemy.exc import IntegrityError

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

def assignar(ordinador, alumne):
    antic = alumne.ordinador
    if antic is not None and antic.id != ordinador.id:
        retirar_alumne(antic)
        antic.estat = "emmagatzemat"
    if ordinador.alumne_id is not None and ordinador.alumne_id != alumne.id:
        retirar_alumne(ordinador)
    ordinador.alumne_id = alumne.id
    ordinador.estat = "assignat"
    apuntar("assignat", ordinador.id, alumne.id)

def errors_alumne(form):
    errors = []
    alumne_nom = form.get("nom", "").strip()
    alumne_curs = form.get("curs", "").strip()
    alumne_email = form.get("email", "").strip().lower()
    if alumne_nom.strip() == "":
        errors.append("Falta el nom.")
    if alumne_curs not in CURSOS:
        errors.append("Tria un curs de la llista.")
    if not alumne_email.endswith("@elfoix.cat"):
        errors.append("El correu ha de ser del domini @elfoix.cat.")
    return errors

#Rutes HTML

@app.route('/')
def index():
    return redirect(url_for('benvingut'))

@app.route("/benvingut")
def benvingut():
    recompte = dict(db.session.execute(
    search_ordinadors(db.select(Ordinador.estat, func.count()), "").group_by(Ordinador.estat)).all())
    return render_template("benvinguda.html", recompte=recompte)
    
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
    q = request.args.get("q", "").strip()
    query_h = db.select(Historial).order_by(Historial.data.desc()).order_by(Historial.id.desc())
    accio = request.args.get("accio", "")
    if accio:
        claus = [clau for clau, text in ACCIONS_HISTORIAL.items() if text == accio]
        query_h = query_h.where(Historial.accio.in_(claus))
    if q:
        pattern = f"%{q}%"
        query_h = query_h.outerjoin(Historial.ordinador).outerjoin(Historial.alumne)
        query_h = query_h.where(or_(
            func.unaccent(Alumne.nom).ilike(func.unaccent(pattern)),
            Alumne.identificador.ilike(pattern),
            Alumne.email.ilike(pattern),
            Ordinador.sace.ilike(pattern),
            Ordinador.num_serie.ilike(pattern),
            Ordinador.model.ilike(pattern),
        ))
    historial = db.session.execute(query_h).scalars().all()
    textos = sorted(set(ACCIONS_HISTORIAL.values()))
    return render_template("historial/veure.html", historial=historial, q=q, accio=accio, textos=textos)

@app.route("/assignar/html/form")
def formulari_assignar():
    ordinador_id = request.args.get("ordinador_id", type=int)
    alumne_id = request.args.get("alumne_id", type=int)
    ordinadors = db.session.execute(db.select(Ordinador).where(Ordinador.estat.in_(("emmagatzemat", "assignat"))).order_by(Ordinador.sace)).scalars().all()
    alumnes = db.session.execute(db.select(Alumne).where(Alumne.estat == "actiu").order_by(Alumne.nom)).scalars().all()
    return render_template("assignar.html", ordinadors=ordinadors, alumnes=alumnes, ordinador_id=ordinador_id, alumne_id=alumne_id)

@app.route("/alumnes/html/formulari")
def formulari_alumnes():
    return pagina_afegir_alumne()

@app.route("/ordinadors/html/formulari")
def formulari_ordinadors():
    return pagina_afegir_ordinador()

def pagina_afegir_alumne(valors=None, estat_http=200): 
    ordinadors = db.session.execute(db.select(Ordinador).where(Ordinador.estat.in_(("emmagatzemat", "assignat"))).order_by(Ordinador.sace)).scalars().all()
    recents = db.session.execute(db.select(Alumne).order_by(Alumne.id.desc()).limit(5)).scalars().all()
    cursos = CURSOS
    return render_template("alumnes/afegir.html", valors=valors or {}, ordinadors=ordinadors, recents=recents, cursos=cursos), estat_http

@app.route("/alumnes/nou/form", methods=["POST"])
def post_alumne():
    errors = errors_alumne(request.form)
    if errors:
        for error in errors:
            flash(error, "error")
        return pagina_afegir_alumne(request.form, 422)
    nou = Alumne(nom=request.form["nom"].strip(), curs=request.form["curs"].strip(), email=request.form["email"].strip().lower(), identificador=request.form["identificador"].strip())
    ordinador = None
    if request.form.get("ordinador_id"):
        ordinador = db.session.get(Ordinador, request.form.get("ordinador_id", type=int))
        if not ordinador:
            flash("Ordinador no trobat", "error")
            return pagina_afegir_alumne(request.form, 422)
        elif ordinador.estat not in ("emmagatzemat", "assignat"):
            flash(f"L'ordinador {ordinador.sace} no està disponible", "error")
            return pagina_afegir_alumne(request.form, 422)
    db.session.add(nou)
    antic = ordinador.alumne if ordinador else None
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        flash("Ja existeix un alumne amb aquest nom, email o identificador", "error")
        return pagina_afegir_alumne(request.form, 422)
    if ordinador:
        if antic:
            flash(f"L'ordinador {ordinador.sace} estava assignat a {antic.nom}. S'ha retirat i assignat a {nou.nom}.", "ok")
        assignar(ordinador, nou)
    db.session.commit()
    flash(f"Alumne {nou.nom} afegit correctament", "ok")
    return redirect(url_for("formulari_alumnes"))

def pagina_afegir_ordinador(valors=None, estat_http=200):
    models = db.session.execute(db.select(Ordinador.model).distinct()).scalars().all()
    alumnes = db.session.execute(db.select(Alumne).where(*FILTRES["sense"]).order_by(Alumne.nom)).scalars().all()
    recents = db.session.execute(db.select(Ordinador).order_by(Ordinador.id.desc()).limit(5)).scalars().all()
    return render_template("ordinadors/afegir.html", valors=valors or {},models=models, alumnes=alumnes, recents=recents), estat_http

@app.route("/ordinadors/nou/form", methods=["POST"])
def post_ordinador():
    nou = Ordinador(num_serie=request.form["num_serie"].strip().upper(), sace=request.form["sace"].strip().upper(), model=request.form["model"].strip())
    alumne = None
    if request.form.get("alumne_id"):
        alumne = db.session.get(Alumne, request.form.get("alumne_id", type=int))
        if not alumne:
            flash("Alumne no trobat", "error")
            return pagina_afegir_ordinador(request.form, 422)
        elif alumne.estat != "actiu":
            flash(f"L'alumne {alumne.nom} no està actiu", "error")
            return pagina_afegir_ordinador(request.form, 422)
    db.session.add(nou)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        flash("Ja existeix un ordinador amb aquest SACE o número de sèrie", "error")
        return pagina_afegir_ordinador(request.form, 422)
    if alumne:
        assignar(nou, alumne)
    db.session.commit()
    flash(f"Ordinador {nou.sace} afegit correctament", "ok")
    return redirect(url_for("formulari_ordinadors"))

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
    ordinador = db.session.get(Ordinador, request.form.get("ordinador_id", type=int))
    alumne = db.session.get(Alumne, request.form.get("alumne_id", type=int))
    if ordinador is None or alumne is None:
        flash("Tria un ordinador i un alumne.", "error")
        return redirect(url_for("formulari_assignar"))
    assignar(ordinador, alumne)
    db.session.commit()
    flash(f"{ordinador.sace} assignat a {alumne.nom}.", "ok")
    return redirect(url_for("formulari_assignar"))

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

@app.route('/alumnes/html/<int:alumne_id>/editar', methods=['GET'])
def editar_alumne_html(alumne_id):
    alumne = db.get_or_404(Alumne, alumne_id)
    valors = {
        'nom': alumne.nom,
        'identificador': alumne.identificador,
        'curs': alumne.curs,
        'email': alumne.email,
    }
    return render_template('alumnes/editar.html', alumne=alumne, cursos=CURSOS, valors=valors)


@app.route('/alumnes/html/actualitzar/<int:alumne_id>', methods=['POST'])
def actualitzar_alumne_html(alumne_id):
    alumne = db.get_or_404(Alumne, alumne_id)
    valors = {
        'nom': request.form.get('nom', '').strip(),
        'identificador': request.form.get('identificador', '').strip(),
        'curs': request.form.get('curs', '').strip(),
        'email': request.form.get('email', '').strip().lower(),
    }
    errors = errors_alumne(valors)
    if errors:
        for error in errors:
            flash(error, "error")
        return render_template('alumnes/editar.html', alumne=alumne, cursos=CURSOS, valors=valors), 422
    for camp, valor in valors.items():
        setattr(alumne, camp, valor)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        flash("Ja existeix un alumne amb aquest nom, email o identificador", "error")
        return render_template('alumnes/editar.html', alumne=alumne, cursos=CURSOS, valors=valors), 422
    flash(f"Alumne {alumne.nom} actualitzat correctament", "ok")
    db.session.commit()
    return redirect(url_for('fitxa_alumne', alumne_id=alumne.id))

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



