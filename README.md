# Treball de Recerca | Hatim el Housni Lagrine | Institut el Foix

<img width="6445" height="2410" alt="Logo_Gestio" src="https://github.com/user-attachments/assets/a95e9b57-b6ae-4a33-8d36-d02f3368aecd" />

# Benvingut al meu Treball de Recerca pel curs 2026-2027!
En aquest repositori és guardat tota la part practica del meu treball.
En finalitzar el treball també fare public el full de recerca final.

# En que consisteix el treball?
Aquest treball de recerca consisteix en l’aprenentatge de programació en diversos llenguatges de programació i la seva implantació full stack. El producte final és un portal web per l'administració i gestió els equips Chromebook propietat del centre educatiu que han estat cedits a l'alumnat, on es poden gestionar coses com incidències, inventari, dades dels alumnes usuaris, etc. Per assolir això he hagut d'aprendre a programar pàgines web, bases de dades i a enllaçar aquests dos. 

# Com puc iniciar la web per provar-la?
Per fer-ho has de tenir tant Git com Python al teu sistema.
Windows:
```
winget install -e --id python --accept-package-agreements --accept-source-agreements
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements
```
A posteriori, reinicia la teva finestra de powershell.

Linux (Fedora):
```
sudo dnf install -y git python
```
Altres distribucions de linux, com Ubuntu, Arch, etc son similars.

Un cop fet aixo, els pasos son els següents:

En Windows
```
git clone https://github.com/GthbHatim/TREC2027
cd ./TREC2027
pip install -r requirements.txt
python run.py
```
A Linux:
```
git clone https://github.com/GthbHatim/TREC2027
cd ./TREC2027
pip install -r requirements.txt
python3 run.py
```
El terminal retornara:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://XXX.X.X.X:XXXX
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 708-197-034
```
Al teu navegador, substitueix `http://XXX.X.X.X:XXXX` amb el valor que la terminal retorni, per exemple:
```
http://192.0.0.1:4444/
```

# FAQ
## Com esta programat?
El programari esta escrit majoritariament en Python (Pandas, SQLAlchemy, Flask) i les webs en HTML (TailwindCSS, Google Fonts)

## Es reutilitzable?
En cas de ser una institució escolar publica, si. Qualsevol altre tipus de ús comercial queda totalment prohibit sense autorització.

## Com ho puc personalitzar?
En un futur posare una guia de com modificar les entrades per encaixar en les necesitats de cada centre.

<img width="200" height="100" alt="Logo El Foix Nou (TXT) (1)" src="https://github.com/user-attachments/assets/d259346c-28ac-4ad4-98a2-4c690e6388d7" />
<img width="237" height="100" alt="image" src="https://github.com/user-attachments/assets/4a66eec1-2b40-4f13-be1c-a880b94a9302" />

