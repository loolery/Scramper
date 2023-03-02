import sqlite3
import requests
from bs4 import BeautifulSoup

def soupobj(url):
    heads = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
    response = requests.get(url, headers=heads)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    return soup

def getLandId(landname):
    #Braucht als Parameter den Landnamen im String und gibt die in der SQLite gefundene
    #Id des Landes zurück!
    landid = 200 # Id für unbekannte
    sql = sqlite3.connect('database.db3')
    cursor = sql.cursor()
    query = "SELECT ID FROM tbl_land WHERE Name LIKE '%" + landname + "%' LIMIT 1"
    try:
        result = cursor.execute(query)
    except:
        landid = 200
    else:
        for r in result:
            landid= r[0]
    return landid

def getStadtId(stadtname):
    #Braucht als Parameter den Stadtnamen im String und gibt die in der SQLite gefundene
    #Id der Stadt zurück!
    chars = "öäü"
    for char in chars:
        try: stadtname = stadtname.replace(char, '%')
        except: stadtid = 81
        else:
            stadtid = 81 # Id für unbekannte
            sql = sqlite3.connect('database.db3')
            cursor = sql.cursor()
            query = "SELECT ID FROM tbl_stadt WHERE Name LIKE '%" + stadtname + "%' LIMIT 1"
            try: result = cursor.execute(query)
            except: stadtid = 81
            else:
                for r in result:
                    stadtid= r[0]
    return stadtid

def convertPosition(position):
    #Braucht als Parameter den Namen der Position im String, gibt dann
    #die Position als Zahl zurück.
    pos_id = 0
    if '-' in position: pos_id = 0
    elif 'Torwart' in position: pos_id = 1
    elif 'Innenverteidiger' in position: pos_id = 2
    elif 'Linker Verteidiger' in position: pos_id = 3
    elif 'Rechter Verteidiger' in position: pos_id = 4
    elif 'Defensives Mittelfeld' in position: pos_id = 5
    elif 'Zentrales Mittelfeld' in position: pos_id = 6
    elif 'Offensives Mittelfeld' in position: pos_id = 7
    elif 'Hängende Spitze' in position: pos_id = 8
    elif 'Linksaußen' in position: pos_id = 9
    elif 'Rechtsaußen' in position: pos_id = 8
    elif 'Mittelstürmer' in position: pos_id = 9
    return pos_id

def convertFuss(fuss):
    #Braucht als Parameter den Namen des ballführenden Fusses im String,
    # gibt dann den Fuss als Zahl zurück.
    if fuss is None: return 2
    if 'beidfüßig' in fuss: fuss_id = 0
    elif 'links' in fuss: fuss_id = 1
    elif 'rechts' in fuss: fuss_id = 2
    else: fuss_id = 2
    return fuss_id

def search_teamlinks(url):
    # Gibt eine Liste aller gefunden Vereinslinks in der Liga zurück.
    team_link = []
    soup = soupobj(url)
    table = soup.find_all("td", {"class": "hauptlink no-border-links"})
    for t in table:
        a = t.find("a", href=True)
        team_link.append('https://www.transfermarkt.de' + a.get('href', None))
    return team_link