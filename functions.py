import sqlite3
import re
import requests
import requests_cache
from bs4 import BeautifulSoup
import subprocess
import time

def conCheck(url):
    #prüft ob die übergeben Internet URL erreichbar ist, wenn nicht
    #wird alle 10 sekunden wiederholt geprüft.
    if url.split("/", 1)[0] == 'https:':    #IPs können direkt gepinged werden, urls müssen erst bereinigt werden
        url = url.split("/", 1)[1].split("/")[1]
    while True:
        print(f"*ping - {url}")
        try:
            subprocess.check_call('ping ' + url + ' -n 1', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            break
        except subprocess.CalledProcessError:
            print(f" Connection failed! Next try in 10 seconds... {url}")
            time.sleep(10)
def soupobj(url):
    heads = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
    requests_cache.install_cache('my_cache', expire_after=259200)
    while True:
        try:
            response = requests.get(url, headers=heads)
            html = response.text
            soup = BeautifulSoup(html, "lxml")
            break
        except:
            print(f" Connection failed! New try...(y/n)? {url}")
            choice = input()
            if choice == 'n': return False
            time.sleep(1)
    return soup

def germanConvert(word):
    word = word.replace("ä", "ae")
    word = word.replace("ö", "oe")
    word = word.replace("ü", "ue")
    word = word.replace("ß", "ss")
    return word
def getLandId(cursor, landname):
    #Braucht als Parameter den SQL-Cursor & Landnamen als String und gibt die in der SQLite gefundene
    #Id des Landes zurück!
    landid = 200 # Id für unbekannte
    if landname is None:
        landname = 'unbekanntesLand'
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

def staedte_suche(url):
    #sucht nach den Städten eines Landes, deren Einwohnerzahl und dem dazu gehörigen
    #Bundeslandes, der Parameter muss die URL zur wikipediaseite mit den Daten sein.
    # Rückgabe ist ein tuple mit einer Liste drin: tuple[1][1]
    # im Falle UKs wird das Land noch mit angehängt also: tuple[1][2]
    soup = soupobj(url)
    dictionary = {}
    chars = "0123456789,"
    # Suche die Tabelle im Quelltext
    try:
        if 'Frankreich' in url: table = soup.find_all("table", {"class": "wikitable"})[2]
        else: table = soup.find_all("table", {"class": "wikitable"})[1]
    except: result = None   #Tabelle konnte nicht gefunden werden.
    else:
        #Suche nach den Daten in den Feldern 'Name', 'Bundesland' 'aktuellste Einwohnerzahl'
        for row in table.tbody.find_all("tr"):
            name_col = row.find("a", title=True)
            if name_col is not None:
                name = name_col.text.strip()
                for char in chars:
                    name = name.replace(char, "")
                data_cols = row.find_all("td")
                if 'Vereinigten' in url:
                    einw_2021 = data_cols[-3].text.strip().replace('.', '')
                    bundesland = data_cols[-2].text.strip().split(u'\xa0')[0]
                    staat = data_cols[-1].text.strip().split(u'\xa0')[0].replace('*', '')
                    dictionary[name] = [bundesland, einw_2021, staat]
                elif 'Deutschland' in url or 'Italien' in url:
                    einw_2021 = data_cols[-2].text.strip().replace('.', '')
                    bundesland = data_cols[-1].text.strip().split(u'\xa0')[0].replace('*', '')
                    dictionary[name] = [bundesland, einw_2021]
                elif 'Spanien' in url or 'Frankreich' in url:
                    einw_2021 = data_cols[-3].text.strip().replace('.', '')
                    bundesland = data_cols[-2].text.strip().split(u'\xa0')[0].replace('*', '')
                    dictionary[name] = [bundesland, einw_2021]
    return dictionary.items()

def search_fifa():
    # Liest auf Transfermarkt.de die FiFA-Weltrangliste ein und
    # gibt den Ländernamen und die Punkte als tuple zurück. tuple[1][1]
    url = 'https://www.transfermarkt.de/statistik/weltrangliste?page='
    chars = "123456789"
    dictionary = {}
    counter = 0
    for page in chars:
        soup = soupobj(url + page)
        # Suche die Tabelle im Quelltext
        try: table = soup.find("table", {"class": "items"})
        except: return None  # Tabelle konnte nicht gefunden werden.
        else:
            for tr in table.tbody.find_all("tr"):
                td = tr.find("td", {"class": "hauptlink"})
                try:
                    title = td.find("a", href=True)
                    img = td.find("img", src=True)
                    picture = img.get('src', None).split("?lm=")[0]
                except: counter += 1  # jeder 2ter Durchlauf muss abgefangen werden.
                else:
                    name = title.get('title', None)
                    punkte = tr.find("td", {"class": "zentriert hauptlink"}).text.strip()
                    dictionary[name] = [punkte, picture]
    return dictionary.items()

def landerinfo_suche():
    # läd ein tuple von Wikipedia mit allen Staaten, deren englischen Namen,
    # die Hauptstadt, die Adresse der Fahne.jpg, und die Einwohnerzahl: tuple[1][3]
    soup = soupobj('https://de.wikipedia.org/wiki/Liste_der_Staaten_der_Erde')
    dictionary = {}
    chars = "0123456789,#%&$"
    count = 0
    try: table = soup.find("table", {"class": "wikitable"})
    except: result = None   #Tabelle konnte nicht gefunden werden.
    else:
        #Searching for data in fields like 'Name', 'Bundesland' 'aktuellste Einwohnerzahl'
        for row in table.tbody.find_all("tr"):
            count += 1
            if count >= 5:
                try: name_col = row.find("a", title=True)
                except Exception as error: print(f' ERROR...: {error}')
                else:
                    if name_col is not None:
                        name = name_col.text.strip()

                        if 'Vereinigtes Königreich' in name:
                            soup2 = soupobj(f'https://de.wikipedia.org{name_col.get("href", None)}')
                            try:
                                tableuk = soup2.find("table", {"class": "wikitable sortable mw-collapsible zebra"})
                            except:
                                print('error! -> Vereinigtes Königreich')
                            else:
                                for row2 in tableuk.tbody.find_all("tr"):
                                    if row2.find("a", title=True):
                                        cell = row2.find_all("td")
                                        #print(f"  {cell[0].text}")
                                #     if not row.get('src', None) == None and not 'United_Kingdom' in row.get('src', None):
                                #         print(row.get('src', None).split("//")[1])
                                # print('\n')
                                # for result2 in soup2.tbody.find_all("tr"):
                                #     if not result2.text == None and not 'Vereinigtes' in result2.text.strip():
                                #         print(result2.text.strip())
                        #dictionary[name] = [name_englisch, hauptstadt, fahne, einwohner]
                        #break

                    data_cols = row.find_all("td")
                    try: name_englisch = data_cols[-2].text.strip().replace('.', '')
                    except: continue
                    else:
                        hstadt = data_cols[-10].text.strip().split(u'\xa0')[0].replace('*', '')
                        einwohner = data_cols[-9].text.strip().split(u'\xa0')[0].replace('.', '').replace('*', '').split('K')[0]
                        fahne = "https:" + data_cols[-6].find("img", src=True).get('src', None)
                        for char in chars:
                            name = name.replace(char, "").split('(')[0]
                            hauptstadt = hstadt.replace(char, "").split('[')[0].split('(')[0]
                        dictionary[name] = [name_englisch, hauptstadt, fahne, einwohner]
    return dictionary.items()
result = landerinfo_suche()

# def laender_suche():
#     # läd von Transfermarkt.de alle Länder mit Ligen in Europa
#     # zurückgegeben wird der Name des Landes und deren Transfermarkt-ID
#     soup = soupobj('https://www.transfermarkt.de/wettbewerbe/europa/wettbewerbe')
#     dictionary = {}
#     chars = "0123456789,#%&$"
#     count = 0
#     # Suche die Tabelle im Quelltext
#     try:
#         table = soup.find("map", {"id": "europa_Map"})
#     except:
#         result = None
#         print(' ## Error - Map mit Ländern auf Transfermarkt wurde nicht gefunden!')
#     else:
#         for row in table.find_all("area"):
#             if row.get('href', None).split('/')[4].strip().isnumeric():
#                 count += 1
#                 name = row.get('title', None).strip()
#                 id = row.get('href', None).split('/')[4].strip()
#                 dictionary[name] = [id]
#     return dictionary.items()
def laender_suche():
    # searching countrys at Transfermarkt.de.
    # returns the Name and the Transfermarkt-ID
    dictionary = {}
    chars = "0123456789,#%&$"
    count = 0
    soup = soupobj('https://www.transfermarkt.de/wettbewerbe/europa/wettbewerbe')
    try:
        table = soup.find("map", {"id": "europa_Map"})
    except:
        result = None
        print(' ## Error - Europa Map mit Ländern auf Transfermarkt wurde nicht gefunden!')
    else:
        for row in table.find_all("area"):
            if row.get('href', None).split('/')[4].strip().isnumeric():
                count += 1
                name = row.get('title', None).strip()
                id = row.get('href', None).split('/')[4].strip()
                dictionary[name] = [id]
    # Suche die Tabelle im Quelltext
    count = 0
    soup1 = soupobj('https://www.transfermarkt.de/wettbewerbe/amerika/wettbewerbe')
    try:
        table1 = soup1.find("map", {"name": "amerika_Map"})
    except:
        result = None
        print(' ## Error - Amerika Map mit Ländern auf Transfermarkt wurde nicht gefunden!')
    else:
        for row in table1.find_all("area"):
            if row.get('href', None).split('/')[4].strip().isnumeric():
                count += 1
                name = row.get('title', None).strip()
                id = row.get('href', None).split('/')[4].strip()
                dictionary[name] = [id]
    count = 0
    soup2 = soupobj('https://www.transfermarkt.de/wettbewerbe/asien/wettbewerbe')
    try:
        table2 = soup2.find("map", {"name": "asien_Map"})
    except:
        result = None
        print(' ## Error - Asien Map mit Ländern auf Transfermarkt wurde nicht gefunden!')
    else:
        for row in table2.find_all("area"):
            if row.get('href', None).split('/')[4].strip().isnumeric():
                count += 1
                name = row.get('title', None).strip()
                id = row.get('href', None).split('/')[4].strip()
                dictionary[name] = [id]
    count = 0
    soup3 = soupobj('https://www.transfermarkt.de/wettbewerbe/afrika/wettbewerbe')
    try:
        table3 = soup3.find("map", {"name": "afrika_Map"})
    except:
        result = None
        print(' ## Error - Afrika Map mit Ländern auf Transfermarkt wurde nicht gefunden!')
    else:
        for row in table3.find_all("area"):
            if row.get('href', None).split('/')[4].strip().isnumeric():
                count += 1
                name = row.get('title', None).strip()
                id = row.get('href', None).split('/')[4].strip()
                dictionary[name] = [id]
    return dictionary.items()


def ligen_suche(id):
    # Sucht bei Transfermarkt.de nach den ID´s(String) der einzelnen Ligen eines Landes und gibt diese zurück.
    # Rückgabe erfolg im tuple:
    # Rang der Liga --> Landname, Name der Liga, Transfermarkt.de Url zur Liga, Url des Wappens der Liga
    dictionary = {}
    count, count2 = 0, 0
    img, href, title, groesse, land = [], [], [], [], ''
    soup = soupobj('https://www.transfermarkt.de/wettbewerbe/national/wettbewerbe/' + id)
    try:
        #Sucht nach Ligadaten
        #Sucht nach Ligadaten
        table = soup.find("table", {"class": "items"})
        for link in table.find_all("img", {"class": "continental-league-emblem"}):
            img.append(link.get('src', None))
        for link2 in table.find_all("a"):
            if not '/forum/' in link2.get('href', None):
                href.append(link2.get('href', None))
                title.append(link2.get('title', None))
    except Exception as error:
        print('break: ', error)
    else:
        try:
            for tab in soup.find_all("td", {"class": "extrarow bg_blau_20 hauptlink"}):
                if '.Liga' in tab.text:
                    # schützt vor wiederholungen und reduziert auf max. 3 Ligen.
                    if count >=1 and tab.text == '1.Liga' or count >= 3: break
                    rang = tab.text
                    name = title[count2 + 1]
                    url = href[count2 + 1]
                    picture = img[count]
                    soup2 = soupobj('https://www.transfermarkt.de' + url)
                    for infobox in soup2.find_all("div", {"class": "data-header__info-box"}):
                        groesse = [int(num) for num in re.findall(r'\d+', infobox.find("li", {"class": "data-header__label"}).text)]
                    for clubinfo in soup2.find_all("div", {"class": "data-header__club-info"}):
                        land = clubinfo.find("span", {"class": "data-header__club"}).text.strip()
                    dictionary[rang] = [germanConvert(land), name, groesse, url, picture]
                count+=1
                count2+=2
        except Exception as error:
            print('break2: ', error)
    print('\n')
    return dictionary.items()
def marktwerte_korrigieren(marktwert):
    value_str = marktwert.replace(',', '.')  # Ersetze das Komma durch einen Punkt für die Dezimaldarstellung
    if 'Mio.' in value_str:  # Wenn "Mio." in der Zeichenkette vorhanden ist
        value = float(value_str.replace(' Mio.', '')) * 1000000  # Entferne "Mio." und multipliziere mit 1.000.000
    elif 'Tsd.' in value_str:  # Wenn "Tsd." in der Zeichenkette vorhanden ist
        value = float(value_str.replace(' Tsd.', '')) * 1000  # Entferne "Tsd." und multipliziere mit 1.000
    else:
        value = float(value_str)  # Wenn keine Einheit angegeben ist, konvertiere einfach die Zahl in float
    return int(value)  # Rückgabe des Werts als Integer
