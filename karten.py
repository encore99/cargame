import mysql.connector
import json

# Funktion zum Lesen der Konfigurationsdatei
def read_config():
    with open("credentials\config.json") as f:
        config = json.load(f)
    return config

# Verbindung zur Datenbank herstellen
def connect_to_database():
    config = read_config()
    mydb = mysql.connector.connect(
        host=config["host"],
        user=config["benutzername"],
        password=config["passwort"],
        database=config["datenbank"]
    )
    return mydb

# Tabelle erstellen und Datensatz einfügen
def create_table_and_insert_data():
    mydb = connect_to_database()
    cursor = mydb.cursor()

    # Tabelle erstellen, wenn sie noch nicht existiert
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id INT PRIMARY KEY)")

    # Datensatz mit Wert 1 einfügen
    cursor.execute("INSERT INTO test (id) VALUES (1)")

    # Änderungen bestätigen und Verbindung schließen
    mydb.commit()
    mydb.close()

    print("Tabelle erstellt und Datensatz eingefügt.")

# Hauptfunktion aufrufen
if __name__ == "__main__":
    create_table_and_insert_data()
