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
# for te in test:
#     if test: print(f'{te[0]} - {te[1][0]} - {te[1][1]}')
# else: print('None!')


laender = func.landerinfo_suche()
test = func.search_fifa()
for te in test:
    for key in te:
        print(key)
        if key in laender: print(f' --> {laender[key][0]} : {laender[key][1]}')
else: print('None!')

# import sqlite3
#
# counter = 0
# sql = sqlite3.connect('database.db3')   #öfnet eine sqlite-db
# cursor = sql.cursor()
# query = "CREATE TABLE IF NOT EXISTS tbl_land " \
#         "(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, " \
#         "Name STRING(32) UNIQUE NOT NULL, " \
#         "Name2 STRING(32) UNIQUE NOT NULL, " \
#         "Einwohner DOUBLE NOT NULL, " \
#         "Punkte INTEGER(5) NOT NULL);"
# try: db_result = cursor.execute(query)
# except: print(f' ERROR... 1')
#
# first = "INSERT INTO tbl_land (ID, Name, Name2, Einwohner, Punkte) VALUES "
# laender = func.search_fifa()
# for land in laender:
#     counter += 1
#     query = first + "(" + counter + ", " + land[0] + ", " + name2 + ", " + einwohner + ", " + land[1][0] + ", " + land[1][1] + ");"


