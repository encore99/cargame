import json                             #Import der JSON Lib

# Pfad zur Konfigurationsdatei
config_file = ".\credentials\config.json"

# Funktion zum Lesen der Konfigurationsdatei
def read_config():
    with open(config_file) as f:
        config = json.load(f)
    return config

# Verwendung der Funktion zum Lesen der Konfigurationsdatei
config = read_config()

# Extrahieren der Logindaten
benutzername = config["benutzername"]
passwort = config["passwort"]
host = config["host"]
datenbank = config["datenbank"]
