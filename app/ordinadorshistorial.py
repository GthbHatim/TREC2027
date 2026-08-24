from app import app
from app.extensions import db
from app.models import Ordinador
from app.models import Alumne
from app.models import Historial
from flask import request

@app.route("/ordinadors")
def listar_ordinadors():
    ordinadors = db.session.execute(db.select(Ordinador)).scalars().all()
    return {"ordinadors": [{"id": o.id, "num_serie": o.num_serie, "ref_diputacio": o.ref_diputacio, "model": o.model, "estat": o.estat, "alumne_id": o.alumne_id, "alumne_nom": o.alumne.nom if o.alumne else None} for o in ordinadors]}

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

@app.route("/ordinadors/<int:id>/assignar", methods=["PATCH"])
def assignar_ordinador(id):
    ordinador = db.session.get(Ordinador, id)
    if not ordinador:
        return {"error": "Ordinador no enregistrat"}, 404
    dades = request.get_json() 
    alumne = db.session.get(Alumne, dades["alumne_id"]) 
    if not alumne:
        return {"error": "Alumne no trobat"}, 404
    if ordinador.alumne_id:
        nou1 = Historial(alumne_id = ordinador.alumne_id, ordinador_id = ordinador.id, accio = "retirat")
        db.session.add(nou1)
    ordinador.alumne_id = alumne.id
    ordinador.estat = "assignat"
    nou2 = Historial(alumne_id = ordinador.alumne_id, ordinador_id = ordinador.id, accio = "assignat")
    db.session.add(nou2)
    db.session.commit()
    return {"missatge": "Ordinador assignat", "id": ordinador.id, "alumne_id": ordinador.alumne_id}, 200

@app.route("/ordinadors/bulk", methods=["POST"])
def crear_ordinador_bulk():
    dades = request.get_json()
    llista = dades["ordinadors"]
    creats = []
    for item in llista:
        nou = Ordinador(num_serie=item["num_serie"], ref_diputacio=item["ref_diputacio"], model=item["model"])
        db.session.add(nou)
        creats.append(nou.num_serie)
    db.session.commit()
    return {"missatge": f"{len(creats)} ordinadors creats", "identificadors": creats}, 201

@app.route("/historial")
def mostrar_historial():
    historial = db.session.execute(db.select(Historial)).scalars().all()
    missatge = []
    for h in historial:
        alumne = db.session.get(Alumne, h.alumne_id)
        nom = alumne.nom if alumne else None
        entrada = {"id": h.id, "accio": h.accio, "data": h.data, "alumne_id": h.alumne_id, "ordinador_id": h.ordinador_id, "alumne_nom": nom}
        missatge.append(entrada)
    return {"historial": missatge}