import re
import sqlite3
import os
import requests
import requests_cache
import subprocess
import time
from bs4 import BeautifulSoup

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
    requests_cache.install_cache('my_cache', expire_after=86400)
    while True:
        try:
            response = requests.get(url, headers=heads)
            html = response.text
            soup = BeautifulSoup(html, "lxml")
            break
        except:
            print(f" Connection failed! Next try in 10 seconds... {url}")
            time.sleep(10)
    return soup
def germanConvert(word):
    word = word.replace("ä", "ae")
    word = word.replace("ö", "oe")
    word = word.replace("ü", "ue")
    word = word.replace("ß", "ss")
    return word
def search_playerskills(url):
    count = 0
    while count < 4:
        soup = soupobj(url + str(count))
        player_name = "Kylian Mbappé"

        try:
            tr = soup.find_all("tr", {"class": "Table_row__4INyY"})
        except:
            print("exception\n")
        else:
            for t in tr:
                names = t.find_all("a", {"class": "Table_profileCellAnchor__L23hq"})
                allnames = [name.text for name in names]
                print(allnames)
                # Verwende find_all(), um alle passenden Werte des Spielers zu finden
                values = t.find_all("span", {"class": "Table_statCellValue__0G9QI"})

                # Extrahiere den ersten Text jedes gefundenen span-Elements
                allvalues = []
                for value in values:
                    text = value.text.strip()  # Entferne Leerzeichen am Anfang und Ende
                    # Extrahiere nur die ersten beiden Ziffern
                    if text.isdigit():  # Überprüfe, ob der Text eine Zahl ist
                        if len(text) >= 3:  # Überprüfe, ob die Zahl mindestens 3 Stellen hat
                            text = text[:-1]  # Entferne die letzte Ziffer
                        allvalues.append(text[:2])  # Extrahiere die ersten beiden Ziffern
                print(allvalues)
        count += 1

db_name = 'test.db3'    #SQLite DB zum schreiben
url = "https://drop-api.ea.com/rating/fc-24?locale=de&limit=100&gender=0&offset="
offset = 0
while offset < 18000:
    source = requests.get(url+str(offset)).json()

    for sour in source['items']:
        print(sour['firstName'])
        sql = sqlite3.connect(db_name)
        cursor = sql.cursor()
        query = f"UPDATE 'tbl_personen' SET Fitness=99 WHERE Vorname='{sour['firstName'].replace("'", "")}' AND Nachname='{sour['lastName'].replace("'", "")}'"
        try:
            db_result = cursor.execute(query)
            print(' --> Neuer Wert wurd eingetragen!')
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
        sql.commit()
    offset += 100