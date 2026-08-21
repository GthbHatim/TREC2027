from app import app
from app.extensions import db
from app.models import Ordinador
from flask import request

@app.route("/ordinadors")
def listar_ordinadors():
    ordinadors = db.session.execute(db.select(Ordinador)).scalars().all()
    return {"ordinadors": [{"id": o.id, "num_serie": o.num_serie, "ref_diputacio": o.ref_diputacio, "model": o.model, "estat": o.estat, "alumne_id": o.alumne_id} for o in ordinadors]}

@app.route("/ordinadors/nou", methods=["POST"])
def crear_ordinador():
    dades = request.get_json()
    nou = Ordinador(num_serie=dades["num_serie"], ref_diputacio=dades["ref_diputacio"], model=dades["model"])
    db.session.add(nou)
    db.session.commit()
    return {"missatge": "Ordinador enregistrat", "id": nou.id, "estat": nou.estat}, 201

@app.route("/ordinadors/<int:id>/editar", methods=["PUT"])
def editar_ordinador(id):
    ordinador = db.session.get(Ordinador, id)
    if not ordinador:
        return {"error": "Ordinador no enregistrat"}, 404
    dades = request.get_json()
    ordinador.num_serie = dades.get("num_serie", ordinador.num_serie)
    ordinador.ref_diputacio = dades.get("ref_diputacio", ordinador.ref_diputacio)
    ordinador.model = dades.get("model", ordinador.model)
    db.session.commit()
    return {"missatge": "Info. del ordinador modificada", "id": ordinador.id}, 200

@app.route("/ordinadors/<int:id>/reparacio", methods=["PUT"])
def reparar_ordinador(id):
    ordinador = db.session.get(Ordinador, id)
    if not ordinador:
        return {"error": "Ordinador no enregistrat"}, 404
    ordinador.estat = "en reparació"
    db.session.commit()
    return {"missatge": "Ordinador marcat com a en reparació", "id": ordinador.id}, 200

@app.route("/ordinadors/<int:id>/emmagatzematge", methods=["PUT"])
def emmagatzemar_ordinador(id):
    ordinador = db.session.get(Ordinador, id)
    if not ordinador:
        return {"error": "Ordinador no enregistrat"}, 404
    ordinador.estat = "emmagatzemat"
    db.session.commit()
    return {"missatge": "Ordinador emmagatzemat", "id": ordinador.id}, 200

@app.route("/ordinadors/<int:id>/baixa", methods=["DELETE"])
def borrar_ordinador(id):
    ordinador = db.session.get(Ordinador, id)
    if not ordinador:
        return {"error": "Ordinador no enregistrat"}, 404
    ordinador.estat = "baixa"
    db.session.commit()
    return {"missatge": "Ordinador donat de baixa", "id": ordinador.id}, 200