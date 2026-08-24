from app import app
from app.extensions import db
from app.models import Alumne
from flask import request

@app.route("/alumnes")
def listar_alumnes():
    alumnes = db.session.execute(db.select(Alumne)).scalars().all()
    return {"alumnes": [{"nom": a.nom, "id": a.id, "identificador": a.identificador, "curs": a.curs, "estat": a.estat, "email": a.email} for a in alumnes]}

@app.route("/alumnes/nou", methods=["POST"])
def crear_alumne():
    dades = request.get_json()
    nou = Alumne(nom=dades["nom"], identificador=dades["identificador"], curs=dades["curs"], email=dades["email"])
    db.session.add(nou)
    db.session.commit()
    return {"missatge": "Alumne creat", "id": nou.id, "estat": nou.estat}, 201

@app.route("/alumnes/<int:id>/editar", methods=["PUT"])
def editar_alumne(id):
    alumne = db.session.get(Alumne, id)
    if not alumne:
        return {"error": "Alumne no trobat"}, 404
    dades = request.get_json()
    alumne.nom = dades.get("nom", alumne.nom)
    alumne.curs = dades.get("curs", alumne.curs)
    alumne.email = dades.get("email", alumne.email)
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

@app.route("/alumnes/bulk", methods=["POST"])
def crear_alumnes_bulk():
    dades = request.get_json()
    llista = dades["alumnes"]
    creats = []
    for item in llista:
        nou = Alumne(nom=item["nom"], identificador=item["identificador"], curs=item["curs"], email=item["email"])
        db.session.add(nou)
        creats.append(nou.identificador)
    db.session.commit()
    return {"missatge": f"{len(creats)} alumnes creats", "identificadors": creats}, 201

