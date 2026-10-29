# Treball de Recerca | Hatim el Housni Lagrine | Institut el Foix
<img width="1912" height="970" alt="Pàgina d'inici de Gestió El Foix" src="https://github.com/user-attachments/assets/d3183ab0-bc2e-4480-ba3e-4f2386c70fc7" />

# Benvingut al meu Treball de Recerca del curs 2026-2027!
En aquest repositori hi ha tota la part pràctica del meu treball.
Quan l'acabi, també hi faré públic el document final de la recerca.

# En què consisteix el treball?
Aquest treball de recerca consisteix en l'aprenentatge de programació en diversos llenguatges i la seva aplicació en un projecte *full stack*. El producte final és **Gestió El Foix**, un portal web per gestionar els Chromebooks propietat del centre que s'han cedit a l'alumnat.

Amb la web es pot:
- portar l'**inventari** dels ordinadors i el seu estat (assignat, al magatzem, en reparació o de baixa);
- gestionar els **alumnes** (altes, edició, baixes i reactivacions);
- **assignar** i retirar ordinadors, també des de la fila de cada equip o alumne;
- consultar l'**historial** de tots els moviments, amb cerca i filtres;
- veure la **fitxa** de cada ordinador i de cada alumne, amb la seva línia de temps;
- **exportar** les dades a Excel.

Per fer-ho he hagut d'aprendre a programar pàgines web, bases de dades i a connectar-les entre elles.

# Com puc posar en marxa la web per provar-la?
Necessites **Git**, **Python** i **PostgreSQL** instal·lats.

### 1. Instal·lar els programes

Windows (PowerShell):
```
winget install -e --id Python.Python.3.13 --accept-package-agreements --accept-source-agreements
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements
winget install -e --id PostgreSQL.PostgreSQL.17 --accept-package-agreements --accept-source-agreements
```
Després, tanca i torna a obrir PowerShell.

Linux (Fedora):
```
sudo dnf install -y git python3 postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
```
En altres distribucions (Ubuntu, Arch…) els paquets tenen noms semblants.

### 2. Crear la base de dades
Obre la consola de PostgreSQL (a Linux, `sudo -u postgres psql`; a Windows, l'aplicació *SQL Shell (psql)*) i executa:
```sql
CREATE USER gestio WITH PASSWORD 'canvia-aquesta-contrasenya';
CREATE DATABASE gestio_foix OWNER gestio;
\c gestio_foix
CREATE EXTENSION IF NOT EXISTS unaccent;
```
L'extensió `unaccent` és necessària: permet que les cerques trobin «Antònia» encara que escriguis «antonia».

### 3. Descarregar el projecte i preparar l'entorn
```
git clone https://github.com/GthbHatim/TREC2027
cd TREC2027
python -m venv venv
```
Activa l'entorn virtual:
- Windows: `venv\Scripts\activate`
- Linux: `source venv/bin/activate`

I instal·la les dependències:
```
pip install -r requirements.txt
```

### 4. Crear el fitxer `.env`
A la carpeta `TREC2027`, crea un fitxer anomenat `.env` amb aquest contingut (canvia els valors pels teus):
```
DATABASE_URL=postgresql://gestio:canvia-aquesta-contrasenya@localhost/gestio_foix
AUTH_USER=admin
AUTH_PASSWORD=una-contrasenya-per-entrar-a-la-web
SECRET_KEY=enganxa-aqui-una-clau-aleatoria
```
Per generar la `SECRET_KEY`:
```
python -c "import secrets; print(secrets.token_hex(32))"
```
El fitxer `.env` és a `.gitignore`: no el pugis mai a GitHub.

### 5. Carregar dades de prova (opcional)
La carpeta `examples/csv` té alumnes i ordinadors **inventats** (generats amb Faker). Per carregar-los:
```
python temp_import.py
```
Si vols uns altres alumnes inventats, abans pots executar `python generador.py`.

### 6. Arrencar la web
```
python run.py
```
Obre `http://127.0.0.1:5000` al navegador i entra amb l'usuari i la contrasenya que has posat a `AUTH_USER` i `AUTH_PASSWORD`.

`run.py` arrenca el servidor de desenvolupament de Flask, que només serveix per provar-la al teu ordinador. En producció la web s'executa amb `gunicorn` (vegeu el `Procfile`).

# FAQ
## Com està programat?
- **Backend:** Python, amb Flask (rutes), SQLAlchemy (base de dades), Flask-HTTPAuth (accés) i pandas (exportació a Excel).
- **Base de dades:** PostgreSQL.
- **Frontend:** plantilles Jinja2 en HTML, amb Tailwind CSS i DaisyUI, icones de Lucide i Google Fonts. **No fa servir JavaScript propi:** els menús, els diàlegs i el tema clar/fosc funcionen només amb HTML i CSS.

## És reutilitzable?
Sí, per a qualsevol ús **no comercial**, sota la llicència [CC BY-NC-SA 4.0](LICENSE): cal citar-ne l'autor i compartir les modificacions amb la mateixa llicència. Per a qualsevol ús comercial, cal demanar-ne autorització.

## Com el puc personalitzar?
Més endavant hi afegiré una guia per adaptar-lo a les necessitats de cada centre (cursos, domini del correu, models d'ordinador…).

<img width="200" height="100" alt="Logo de l'Institut El Foix" src="https://github.com/user-attachments/assets/d259346c-28ac-4ad4-98a2-4c690e6388d7" />
<img width="237" height="100" alt="image" src="https://github.com/user-attachments/assets/4a66eec1-2b40-4f13-be1c-a880b94a9302" />
