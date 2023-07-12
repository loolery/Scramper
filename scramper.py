import sqlite3
from datetime import date
import team as vereine
import player as Spieler
import functions as func
import time
import os

func.conCheck('8.8.8.8')
#============= Variablen definieren  =============================================================

start = time.time()     #zum messen der Performence
today = date.today()    #damit die Url auf die aktuelle Mannschaft von diesem Jahr zeigt
count = 0               #für die ID der sqlite zeile
t_count = 0

# Städtelisten D, GB, ES, I, FR
staedte_urls = ('https://de.wikipedia.org/wiki/Liste_der_Gro%C3%9F-_und_Mittelst%C3%A4dte_in_Deutschland', 'https://de.wikipedia.org/wiki/Liste_der_St%C3%A4dte_im_Vereinigten_K%C3%B6nigreich', 'https://de.wikipedia.org/wiki/Liste_der_St%C3%A4dte_in_Spanien', 'https://de.wikipedia.org/wiki/Liste_der_St%C3%A4dte_in_Italien', 'https://de.wikipedia.org/wiki/Liste_der_St%C3%A4dte_in_Frankreich', )

#============= Erstellt DB mit tbl_land  =============================================================

db_name = 'new_database.db3'
counter = 0
if os.path.isfile(db_name):
    os.remove(db_name)
    print(' --> Alte Datenbank wurde gelöscht!')
sql = sqlite3.connect(db_name)   #erstellt eine sqlite-db
cursor = sql.cursor()
query = "CREATE TABLE IF NOT EXISTS 'tbl_land' " \
        "(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, " \
        "Name STRING(32) UNIQUE NOT NULL, " \
        "Name2 STRING(32) UNIQUE NOT NULL, " \
        "Einwohner DOUBLE NOT NULL, "\
        "Hauptstadt STRING(32) UNIQUE NOT NULL, " \
        "Fahne STRING(128) UNIQUE, " \
        "Punkte INTEGER(6) NOT NULL);"
try:
    db_result = cursor.execute(query)
    print(' --> Neue Datenbank mit Tabelle tbl_land wurde erstellt!')
except sqlite3.Error as er:
    print('SQLite error: %s' % (' '.join(er.args)))
    print("Exception class is: ", er.__class__)

first = "INSERT INTO 'tbl_land' (Name, Name2, Einwohner, Hauptstadt, Fahne, Punkte) VALUES "
laender = func.landerinfo_suche()
test = func.search_fifa()
for te in test:
    for key in te:
        for land in laender:
            if key in land:
                counter += 1
                query = first + "('" + land[0] + "', '" + land[1][0] + "', " + land[1][3] + ", '" + land[1][1] + "', '" + land[1][2] + "', 0);"
                try:
                    db_result = cursor.execute(query)
                except sqlite3.Error as er:
                    print('SQLite error: %s' % (' '.join(er.args)))
                    print("Exception class is: ", er.__class__)
sql.commit()
print(f' --> {counter} Länder in Datenbank eingetragen!')

counter = 0
query = ""
first = "UPDATE 'tbl_land' SET Punkte = "
next = " WHERE Name LIKE '%"
for te in test:
    query = first + te[1][0] + next + te[0] + "%';"
    try:
        db_result = cursor.execute(query)
        if db_result: counter += 1
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
sql.commit()
print(f' --> {counter}x FIFA-Punktestände in Datenbank hinzugefügt!\n')

#============= Erstellt tbl_stadt in DB ==========================================

query = "CREATE TABLE IF NOT EXISTS 'tbl_stadt' " \
        "(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, " \
        "Land_ID INTEGER REFERENCES tbl_land (ID) NOT NULL, " \
        "Name STRING(32) UNIQUE NOT NULL, " \
        "Bundesland STRING (32) NOT NULL, " \
        "Einwohner DOUBLE NOT NULL);"
try:
    db_result = cursor.execute(query)
    print(' --> Datenbank mit Tabelle tbl_stadt wurde erstellt!')
except sqlite3.Error as er:
    print('SQLite error: %s' % (' '.join(er.args)))
    print("Exception class is: ", er.__class__)
counter = 0
query = ""
first = "INSERT INTO 'tbl_stadt' (ID, Land_ID, Name, Bundesland, Einwohner) VALUES "
for url in staedte_urls:
    results = func.staedte_suche(url)
    if 'Deutschland' in url:
        print('Städte aus Deutschland geladen ...')
        landId =  1
    elif 'Vereinigten' in url:
        print('Städte aus Großbritanien geladen ...')
        landId = 2
    elif 'Spanien' in url:
        print('Städte aus Spanien geladen ...')
        landId = 3
    elif 'Frankreich' in url:
        print('Städte aus Frankreich geladen ...')
        landId = 4
    elif 'Italien' in url:
        print('Städte aus Italien geladen ...')
        landId = 5
    for di in results:
        counter += 1
        c_query = "(" + str(counter) + ", " + str(landId) + ", '" + str(func.germanConvert(di[0])) + "', '" + str(func.germanConvert(di[1][0])) + "', " + str(di[1][1]) + ");"
        #print(f'  {first}{c_query}')   #kontrollausgabe bei problemen mit dem erstellten SQL-Query
        query = first + c_query
        try:
            db_result = cursor.execute(query)
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
print('\n')
sql.commit()

#============= Erstellt tbl_ligen in DB ==========================================

query = "CREATE TABLE IF NOT EXISTS 'tbl_ligen' " \
        "(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, " \
        "Land_ID INTEGER REFERENCES tbl_land (ID) NOT NULL, " \
        "Name STRING(32) UNIQUE NOT NULL, " \
        "Groesse INTEGER NOT NULL);"
try:
    db_result = cursor.execute(query)
    print(' --> Datenbank mit Tabelle tbl_ligen wurde erstellt!')
except sqlite3.Error as er:
    print('SQLite error: %s' % (' '.join(er.args)))
    print("Exception class is: ", er.__class__)
sql.commit()

#später für die automatische suche in der Europamap von Transfermarkt.de

l_queryhead = "INSERT INTO tbl_vereine (ID, Land_ID, Name, Groesse) \n VALUES "
result = func.laender_suche()
print('--> Läd Ligen...')
for res in result:
    print(f' {res[0]} --> {res[1][0]}')

#============= Erstellt tbl_vereine & tbl_personen in DB =======================================

query = "CREATE TABLE IF NOT EXISTS 'tbl_vereine' " \
        "(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, " \
        "Stadt_ID INTEGER REFERENCES tbl_stadt (ID) NOT NULL, " \
        "liga_ID INTEGER REFERENCES tbl_liga (ID) NOT NULL, " \
        "Name STRING(32) UNIQUE NOT NULL, " \
        "Tabellenplatz INTEGER NOT NULL, " \
        "Gruendung STRING(10) NOT NULL, " \
        "Vereinsfarben STRING (32) NOT NULL, " \
        "Stadion STRING NOT NULL, " \
        "Transfermarkt_Id INTEGER NOT NULL, " \
        "Geld INTEGER NOT NULL);"
try:
    db_result = cursor.execute(query)
    print(' --> Datenbank mit Tabelle tbl_vereine wurde erstellt!')
except sqlite3.Error as er:
    print('SQLite error: %s' % (' '.join(er.args)))
    print("Exception class is: ", er.__class__)
sql.commit()
query = "CREATE TABLE IF NOT EXISTS 'tbl_personen' " \
        "(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, " \
        "Land_ID INTEGER REFERENCES tbl_land (ID) NOT NULL, " \
        "Verein_ID INTEGER REFERENCES tbl_vereine (ID) NOT NULL, " \
        "TrikotNr INTEGER NOT NULL, " \
        "Vorname STRING(32) NOT NULL, " \
        "Nachname STRING(32) NOT NULL, " \
        "Geburtsdatum STRING(10) NOT NULL, " \
        "Groesse INTEGER NOT NULL, " \
        "Fuss INTEGER NOT NULL, " \
        "Position INTEGER NOT NULL, " \
        "Position2 INTEGER NOT NULL, " \
        "Position3 INTEGER NOT NULL, " \
        "Nationalspieler BOOLEAN NOT NULL, " \
        "VertragVon STRING(10) NOT NULL, " \
        "VertragBis STRING(10) NOT NULL, " \
        "Marktwert INTEGER NOT NULL, " \
        "Ausfall BOOLEAN NOT NULL, " \
        "AusfallBis STRING(10) NOT NULL, " \
        "Technik INTEGER NOT NULL, " \
        "Einsatz INTEGER NOT NULL, " \
        "Schnelligkeit INTEGER NOT NULL, " \
        "Fitness INTEGER NOT NULL);"
try:
    db_result = cursor.execute(query)
    print(' --> Datenbank mit Tabelle tbl_personen wurde erstellt!')
except sqlite3.Error as er:
    print('SQLite error: %s' % (' '.join(er.args)))
    print("Exception class is: ", er.__class__)
sql.commit()

#============= tbl_vereine wird mit Daten gefüllt =======================================

t_queryhead = "INSERT INTO tbl_vereine (ID, Stadt_ID, Liga_ID, Name, Tabellenplatz, Gruendung, Vereinsfarben, Stadion, Transfermarkt_Id, Geld) \n VALUES "
p_queryhead = "INSERT INTO tbl_personen (ID,Land_ID,Verein_ID,TrikotNr,Vorname,Nachname,Geburtsdatum,Groesse,Fuss,Position,Position2,Position3,Nationalspieler,VertragVon,VertragBis,Marktwert,Ausfall,AusfallBis,Technik,Einsatz,Schnelligkeit,Fitness) \n VALUES "
playerdatensql = open('playerdaten.sql', 'w', encoding="utf-8")  # öffnet die datei in dem die query´s gespeichert werden
playerdatensql.write(p_queryhead + '\n')  # schreibt den sqlheader in die Datei

sql2 = sqlite3.connect('database.db3')   #öffnet eine sqlite-db zum auslesen
cursor2 = sql2.cursor()
query = "SELECT ID, Name, Transfermarkt_Id FROM tbl_liga ORDER BY ID"
db_result = cursor2.execute(query)
for dbr in db_result:   #Schleife für die einzelnen Links zu den Vereinsprofilen
    listTeams, listVereine = [], []
    listTeams = func.search_teamlinks(f"https://www.transfermarkt.de/{dbr[1].replace(' ', '-').replace('.', '').lower()}/startseite/wettbewerb/{dbr[2]}")
    print(f"\n{dbr[2]} - https://www.transfermarkt.de/{dbr[1].replace(' ', '-').lower()}/startseite/wettbewerb/{dbr[2]}")
    for team in listTeams:     #Schleife zum erstellen der einzelnen Objecte für die Vereine
        listVereine.append(vereine.Verein(team))  # Vereine werden aus der Klasse erstellt und einer Liste hinzugefügt
        print(f" Vereinsdaten von {listVereine[-1].get_teamname()} werden geladen...")   #Kontroll Ausgabe der erstellten Vereinsobjecte.
    for v in listVereine:   #Schleife durch läuft die einzelnen Vereine der Liste'
        t_count += 1
        # SQL-Query wird erstellt und in die Datei geschrieben.
        # Reihenfolge:  ID, Stadt_ID, Liga_ID, Vereinsname, Tabellenplatz, Gründungsdatum, Vereinsfarben,
        #               Stadionname, Transfermarkt_ID, Vereinsbudge,
        t_querystring = "(" + str(t_count) + ", " + str(v.get_stadtid()) + ", " + str(dbr[0]) + ", '" + str(func.germanConvert(v.get_teamname()))
        t_querystring += "', " + str(v.get_ligarang()) + ", '" + str(v.get_gruendung()) + "', '" + str(v.get_teamcolor())
        t_querystring += "', '" + str(v.get_stadionname()) + "', " + str(v.get_transfermarktid()) + ", 100);"
        try:
            tquery = t_queryhead + t_querystring
            db_result = cursor.execute(tquery)
        except sqlite3.Error as er:
            print(f"* SQLite error: {tquery}")
            print('* messsage: %s' % (' '.join(er.args)))
            print("* Exception class is: ", er.__class__)
        else:
            sql.commit()
            print('\n')
            print(f'\n{dbr[2]} - {v.get_teamname()} \n{t_querystring}')

# ============= tbl_personen wird mit Daten gefüllt =======================================

        for pl in v.get_playerlinks():  #Die Schleife durch läuft die einzelnen Spieler welche aus der Vereinsklasse kommen
            count += 1
            print(f"  --> {pl}") #kontroll ausgabe Spielerprofil-Link
            objS = Spieler.Player(pl)   #abruf der Spielerdaten aus dem Transfermarktprofil
            # SQL-Query wird erstellt und in die Datei geschrieben.
            # Reihenfolge:  ID, Land_ID, Verein_ID, TrikotNr, Vorname, Nachname, Geburtsdatum, Groesse, Fuss,
            #               Position, Nebenposition, Nebenposition2, Nationalspieler, VertragVon,
            #               VertragBis, Marktwert, Ausfall, AusfallBis Technik, Einsatz, Schnelligkeit, Fitness
            p_querystring = "(" + str(count) + ", " + str(func.getLandId(objS.get_land()[0])) + ", " + str(t_count) + ", "
            p_querystring += str(objS.get_trikotnr()) + ", '" + str(objS.get_firstname()) + "', '" + str(objS.get_lastname()) + "', '" + str(objS.get_geburtstag())
            p_querystring += "', " + str(objS.get_groesse()) + ", " + str(func.convertFuss(objS.get_fuss())) + ", " + str(func.convertPosition(objS.get_hauptpos()))
            p_querystring += ", " + str(func.convertPosition(objS.get_nebenpos())) + ", " + str(func.convertPosition(objS.get_nebenpos2()))
            p_querystring += ", " + str(objS.get_nationalspieler()) + ", '" + str(objS.get_imteamseit()) + "', '" + str(objS.get_vertragbis()) + "', " + str(objS.get_marktwert())
            p_querystring += ", " + str(objS.get_ausfall()) + ", '" + str(objS.get_ausfallbis())    #Dopingsperre
            p_querystring += "', " + str(objS.get_technik()) + ", " + str(objS.get_einsatz()) + ", " + str(objS.get_schnelligkeit()) + ", 100);"
            playerdatensql.write(p_querystring + '\n')    #Ausgabe in .sql file
            try:
                pquery = p_queryhead + p_querystring
                db_result = cursor.execute(pquery)
            except sqlite3.Error as er:
                print(f"* SQLite error: {pquery}")
                print('* messsage: %s' % (' '.join(er.args)))
                print("* Exception class is: ", er.__class__)
            else:
                sql.commit()
                print(f'  --> {p_querystring}')

playerdatensql.close()
sql.close()
sql2.close()
ende = time.time()  #stoppen und ausgabe der Performence Messung
print('\n           --> Laufzeit: {:5.3f}s'.format(ende-start))
