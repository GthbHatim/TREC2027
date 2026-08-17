from app import app
from app.extensions import db
from app.models import Alumne
from flask import request

@app.route("/alumnes")
def listar_alumnes():
    alumnes = db.session.execute(db.select(Alumne)).scalars().all()
    return {"alumnes": [{"id": a.id, "identificador": a.identificador, "curs": a.curs, "estat": a.estat} for a in alumnes]}

@app.route("/alumnes/nou", methods=["POST"])
def crear_alumne():
    dades = request.get_json()
    nou = Alumne(identificador=dades["identificador"], curs=dades["curs"])
    db.session.add(nou)
    db.session.commit()
    return {"missatge": "Alumne creat", "id": nou.id, "estat": nou.estat}, 201

@app.route("/alumnes/<int:id>/editar", methods=["PUT"])
def editar_alumne(id):
    alumne = db.session.get(Alumne, id)
    if not alumne:
        return {"error": "Alumne no trobat"}, 404
    dades = request.get_json()
    alumne.curs = dades.get("curs", alumne.curs)
    db.session.commit()
    return {"missatge": "Alumne actualitzat", "id": alumne.id}, 200

@app.route("/alumnes/<int:id>/baixa", methods=["DELETE"])
def borrar_alumne(id):
    alumne = db.session.get(Alumne, id)
    if not alumne:
        return {"error": "Alumne no trobat"}, 404
    alumne.estat = "baixa"
    db.session.commit()
    return {"missatge": "Alumne eliminat", "id": alumne.id}, 200


