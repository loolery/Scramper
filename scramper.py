import sqlite3
import re
from datetime import date
import team as vereine
import player as Spieler
import functions as func
import time

start = time.time()     #zum messen der Performence
today = date.today()    #damit die Url auf die aktuelle Mannschaft von diesem Jahr zeigt
count = 0               #für die ID der sqlite zeile
t_count = 0

queryhead = "INSERT INTO tbl_vereine (ID, Stadt_ID, Liga_ID, Name, Tabellenplatz, Gruendung, Vereinsfarben, Stadion, Transfermarkt_Id, Geld) \n VALUES "
teamdatensql = open('teamdaten.sql', 'w', encoding="utf-8")  #öffnet die datei in dem die query´s gespeichert werden
teamdatensql.write(queryhead + '\n') # schreibt den sqlheader in die Datei

queryhead = "INSERT INTO tbl_personen (ID,Land_ID,Verein_ID,TrikotNr,Vorname,Nachname,Geburtsdatum,Groesse,Fuss, Position,Position2,Position3,Nationalspieler,VertragVon,VertragBis,Marktwert,Technik,Einsatz,Schnelligkeit,Fitness) \n VALUES "
playerdatensql = open('playerdaten.sql', 'w', encoding="utf-8")  # öffnet die datei in dem die query´s gespeichert werden
playerdatensql.write(queryhead + '\n')  # schreibt den sqlheader in die Datei

sql = sqlite3.connect('database.db3')   #öfnet eine sqlite-db
cursor = sql.cursor()
query = "SELECT ID, Name, Transfermarkt_Id FROM tbl_liga ORDER BY ID"
db_result = cursor.execute(query)

for dbr in db_result:   #Schleife für die einzelnen Links zu den Vereinsprofilen
    listTeams, listVereine = [], []
    listTeams = func.search_teamlinks(f"https://www.transfermarkt.de/{dbr[1].replace(' ', '-').lower()}/startseite/wettbewerb/{dbr[2]}")
    for team in listTeams:     #Schleife zum erstellen der einzelnen Objecte für die Vereine
        listVereine.append(vereine.Verein(team))  # Vereine werden aus der Klasse erstellt und einer Liste hinzugefügt
        print(f"Vereinsdaten von {listVereine[-1].get_teamname()} sind geladen.")   #Kontroll Ausgabe der erstellten Vereinsobjecte.
    for v in listVereine:   #Schleife durch läuft die einzelnen Vereine der Liste'
        t_count += 1
        # SQL-Query wird erstellt und in die Datei geschrieben.
        # Reihenfolge:  ID, Stadt_ID, Liga_ID, Vereinsname, Tabellenplatz, Gründungsdatum, Vereinsfarben,
        #               Stadionname, Transfermarkt_ID, Vereinsbudge,
        t_querystring = "(" + str(t_count) + ", " + str(v.get_stadtid()) + ", " + str(dbr[0]) + ", " + str(v.get_teamname())
        t_querystring += ", " + str(v.get_ligarang()) + ", " + str(v.get_gruendung()) + ", " + str(v.get_teamcolor())
        t_querystring += ", " + str(v.get_stadionname()) + ", " + str(v.get_transfermarktid()) + ", 100),"
        teamdatensql.write(t_querystring + '\n')
        print(f'\n{dbr[2]} - {v.get_teamname()} \n{t_querystring}')  # Kontroll ausgabe

        for pl in v.get_playerlinks():  #Die Schleife durch läuft die einzelnen Spieler welche aus der Vereinsklasse kommen
            count += 1
            print(f"  --> {pl}") #kontroll ausgabe Spielerprofil-Link
            objS = Spieler.Player(pl)   #abruf der Spielerdaten aus dem Transfermarktprofil
            # SQL-Query wird erstellt und in die Datei geschrieben.
            # Reihenfolge:  ID, Land_ID, Verein_ID, TrikotNr, Vorname, Nachname, Geburtsdatum, Groesse, Fuss,
            #               Position, Nebenposition, Nebenposition2, Nationalspieler, VertragVon,
            #               VertragBis, Marktwert, Technik, Einsatz, Schnelligkeit, Fitness
            querystring = "(" + str(count) + ", " + str(func.getLandId(objS.get_land()[0])) + ", " + str(t_count) + ", "
            querystring += str(objS.get_trikotnr()) + ", " + str(objS.get_firstname()) + ", " + str(objS.get_lastname()) + ", " + str(objS.get_geburtstag())
            querystring += ", " + str(objS.get_groesse()) + ", " + str(func.convertFuss(objS.get_fuss())) + ", " + str(func.convertPosition(objS.get_hauptpos())) + ", "
            if not objS.get_nebenpos() is None: querystring += str(func.convertPosition(objS.get_nebenpos())) + ", "
            else: querystring += 'None' + ", "
            if not objS.get_nebenpos2() is None: querystring += str(func.convertPosition(objS.get_nebenpos2()))
            else: querystring += 'None'
            querystring += ", " + str(objS.get_nationalspieler()) + ", " + str(objS.get_imteamseit()) + ", " + str(objS.get_vertragbis()) + ", " + str(objS.get_marktwert())
            querystring += ", " + str(objS.get_technik()) + ", " + str(objS.get_einsatz()) + ", " + str(objS.get_schnelligkeit()) + ", 100),"
            playerdatensql.write(querystring + '\n')
            print(f'  --> {querystring}') #Kontroll ausgabe

teamdatensql.close()
playerdatensql.close()
sql.close()
ende = time.time()  #stoppen und ausgabe der Performence Messung
print('\n           --> Laufzeit: {:5.3f}s'.format(ende-start))