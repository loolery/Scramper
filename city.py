import functions as func

class Stadt():

    def __init__(self):
        self.name, self.bundesland = '', ''
        self.einwohner = 0

# results = func.staedte_suche('https://de.wikipedia.org/wiki/Liste_der_St%C3%A4dte_in_Frankreich')
# for di in results:
#     print(f'{di[0]} --> {di[1][0]} --> {di[1][1]}')
#
# test = func.search_fifa()
# # for te in test:
# #     if test: print(f'{te[0]} - {te[1][0]}')
# # else: print('None!')

import sqlite3

db_name = 'new_database.db3'

counter = 0
sql = sqlite3.connect(db_name)   #erstellt eine sqlite-db
cursor = sql.cursor()
query = "CREATE TABLE IF NOT EXISTS 'tbl_land' " \
        "(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, " \
        "Name STRING(32) UNIQUE NOT NULL, " \
        "Name2 STRING(32) UNIQUE NOT NULL, " \
        "Einwohner DOUBLE NOT NULL, "\
        "Hauptstadt STRING(32) UNIQUE NOT NULL, " \
        "Fahne STRING(128) UNIQUE NOT NULL, " \
        "Punkte INTEGER(6) NOT NULL);"
try:
    db_result = cursor.execute(query)
    print('Datenbank mit Tabelle tbl_land wurde erstellt!')
except: print(f' ERROR... {db_result}')

first = "INSERT INTO 'tbl_land' (ID, Name, Name2, Einwohner, Hauptstadt, Fahne, Punkte) VALUES "
laender = func.landerinfo_suche()
test = func.search_fifa()
for te in test:
    for key in te:
        for land in laender:
            if key in land:
                counter += 1
                query = first + "(" + str(counter) + ", '" + land[0] + "', '" + land[1][0] + "', " + land[1][3] + ", '" + land[1][1] + "', '" + land[1][2] + "',  0);"
                print(query)
                try:
                    db_result = cursor.execute(query)
                except: print(f' ERROR... {db_result}')
sql.commit()
sql.close()
print(f'{counter} Länder in Datenbank eingetragen!')

sql = sqlite3.connect(db_name)   #erstellt eine sqlite-db
cursor = sql.cursor()
counter = 0
query = ""
first = "UPDATE 'tbl_land' SET Punkte = "
next = " WHERE Name = '"
for te in test:
    counter += 1
    query = first + te[1][0] + next + te[0] + "';"
    try:
        db_result = cursor.execute(query)
        if db_result: print(query)
    except: print(f' ERROR... {db_result.err()}')
sql.commit()
print(f'{counter}x FIFA-Punktestände in Datenbank hinzugefügt!')
sql.close()
