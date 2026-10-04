from faker import Faker
import unicodedata
import csv

fake = Faker(['es_CA'])
anys = {
        "1r ESO": 26,
        "2n ESO": 25,
        "3r ESO": 24,
        "4t ESO": 23,
        "1r Batx": 22,
        "2n Batx": 21
    }

cursos = ["1r ESO", "2n ESO", "3r ESO", "4t ESO", "1r Batx", "2n Batx"]

def clean_string(texto):
    nfkd_form = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in nfkd_form if not unicodedata.combining(c))

n = 45
with open("./examples/csv/alumnes.csv", "w", newline="", encoding="utf-8") as fitxer:
    writer = csv.writer(fitxer)
    writer.writerow(["id", "nom", "identificador", "curs", "email"])
    for e in range(1, n+1):
        nom = fake.first_name()
        cognom = fake.unique.last_name()
        nom_complet = f"{nom} {cognom}"
        print(nom_complet)
        curs = fake.random_element(cursos)
        print(curs)
        email = f"{anys[curs]}{clean_string(nom).lower().replace(" ", "")}{clean_string(cognom).lower().replace(" ", "")}@elfoix.cat"
        print(email)
        identificador = fake.unique.cif()
        print(identificador)
        writer.writerow([e, nom_complet, identificador, curs, email])