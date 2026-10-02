from faker import Faker
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

for _ in range(10):
    nom = fake.first_name()
    cognom = fake.last_name()
    print(f"{nom} {cognom}")
    curs = fake.random_element(cursos)
    print(curs)
    email = f"{anys[curs]}{nom.lower()}{cognom.lower()}@elfoix.cat"
    print(email)
    identificador = fake.cif()
    print(identificador)
