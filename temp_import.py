from app import app
from app.extensions import db
from app.models import Alumne, Ordinador, Historial
import pandas as pd

with app.app_context():
    # Importar Alumnes
    print("Important alumnes...")
    df = pd.read_csv('/examples/csv/alumnes.csv')
    for _, row in df.iterrows():
        alumne = Alumne(
            id=int(row['id']),
            nom=row['nom'],
            identificador=row['identificador'],
            curs=row['curs'],
            email=row['email'],
            estat='actiu'
        )
        db.session.add(alumne)
    db.session.commit()
    print("Alumnes importats!")

    # Importar Ordinadors
    print("Important ordinadors...")
    df = pd.read_csv('/examples/csv/ordinadors.csv')
    for _, row in df.iterrows():
        ordinador = Ordinador(
            id=int(row['id']),
            num_serie=row['num_serie'],
            sace=row['sace'],
            model=row['model'],
            estat=row['estat'].strip()
        )
        db.session.add(ordinador)
    db.session.commit()
    print("Ordinadors importats!")

    # Importar Historial
    print("Important historial...")
    df = pd.read_csv('/examples/csv/historial.csv')
    for _, row in df.iterrows():
        historial = Historial(
            id=int(row['id']),
            accio=row['accio'],
            data=row['data'],
            ordinador_id=int(row['ordinador_id']),
            alumne_id=int(row['alumne_id']) if pd.notna(row['alumne_id']) else None
        )
        db.session.add(historial)
    db.session.commit()
    print("Historial importat!")

    # Resetear les sequències
    print("Resetejant sequències...")
    db.session.execute(db.text("SELECT setval('alumne_id_seq', (SELECT MAX(id) FROM alumne))"))
    db.session.execute(db.text("SELECT setval('ordinador_id_seq', (SELECT MAX(id) FROM ordinador))"))
    db.session.execute(db.text("SELECT setval('historial_id_seq', (SELECT MAX(id) FROM historial))"))
    db.session.commit()
    print("Sequències resetejades!")

    print("Tot importat correctament!")