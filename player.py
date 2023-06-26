import requests
import re
import random
from datetime import datetime
from datetime import date
from bs4 import BeautifulSoup
import functions as func

class Player():

    def __init__(self, url):
        self.firstname, self.lastname = None, None
        self.nation, self.imteamseit, self.vertragbis = None, None, None
        self.hauptpos, self.nebenpos, self.nebenpos2 = None, None, None
        self.fuss, self.nationalteam, self.gebdatum = None, None, None
        self.trikotnr, self.groesse, self.marktwert = None, None, None
        self.technik, self.einsatz, self.schnelligkeit = 0, 0, 0

        soup = func.soupobj(url)
        self.__search_TrikotNr(soup)
        self.__search_name(soup)
        self.__search_marktwert(soup)
        self.__search_nationalspieler(soup)
        self.__search_positionen(soup)
        self.__search_allinbox(soup)
        self.__player_values(int(self.marktwert))

    def get_firstname(self):
        return self.firstname
    def get_lastname(self):
        return self.lastname
    def get_geburtstag(self):
        return self.gebdatum
    def get_land(self):
        return self.nation
    def get_nationalspieler(self):
        return self.nationalteam
    def get_fuss(self):
        return self.fuss
    def get_trikotnr(self):
        return self.trikotnr
    def get_groesse(self):
        return self.groesse
    def get_marktwert(self):
        return self.marktwert
    def get_imteamseit(self):
        return self.imteamseit
    def get_vertragbis(self):
        return self.vertragbis
    def get_hauptpos(self):
        return self.hauptpos
    def get_nebenpos(self):
        return self.nebenpos
    def get_nebenpos2(self):
        return self.nebenpos2
    def get_technik(self):
        return self.technik
    def get_einsatz(self):
        return self.einsatz
    def get_schnelligkeit(self):
        return self.schnelligkeit

    def __search_name(self, soup):
        # Suche Vor und Nachname
        header = soup.h1
        if header.contents[2].strip(): self.firstname = header.contents[2].strip()
        self.lastname = header.strong.text
        if "'" in self.lastname:
            self.lastname = self.lastname.replace("'", " ")
        if not self.firstname is None:
            if "'" in self.firstname:
                self.firstname = self.firstname.replace("'", " ")

    def __search_TrikotNr(self, soup):
        # Suche Rückennummer
        table = soup.find("h1", {"data-header__headline-wrapper"})
        table1 = table.find_all("span", {"class": "data-header__shirt-number"})
        trikotnummer = [tbl.text.replace("#", " ").strip() for tbl in table1]
        if not trikotnummer:
            self.trikotnr = None
        else:
            self.trikotnr = trikotnummer.pop(0)

    def __search_marktwert(self, soup):
        # Suche Marktwert
        self.marktwert = '10000'
        div = soup.find_all("div", {"class": "tm-player-market-value-development__current-value"})
        if div:
            self.marktwert = div[0].text.strip()
        suffixes = {' Mio. €': '0000', ',00 Mio. €': '000000', 'Tsd. €': '000'}
        for suffix, multiplier in suffixes.items():
            if suffix in self.marktwert:
                self.marktwert = self.marktwert.translate(str.maketrans('', '', suffix)) + multiplier
        self.marktwert = self.marktwert.replace(' ', '').replace(',', '')
        if '-' in self.marktwert:
            print('! Spieler ist Suspendiert !')
            self.marktwert = '10001'

    def __search_nationalspieler(self, soup):
        # Nationalspieler?
        self.nationalteam = None
        infoheader = soup.find_all("ul", {"class": "data-header__items"})
        if len(infoheader) != 0:
            test = infoheader[2].find("li", {"class": "data-header__label"})
            if test != None:
                if 'Akt. Nationalspieler:' in test.text.strip():
                    land = infoheader[2].find("span", {"class": "data-header__content"})
                    if len(land.text.strip()) > 2:
                        self.nationalteam = 1  # 1 = ja, ist nationalspieler seines Landes

    def __search_positionen(self, soup):
        # mittlere-rechte Box für Positionen
        pos_all = soup.find_all("dd", {"class": "detail-position__position"})
        if len(pos_all) == 0:   #wenn Box nicht vorhanden ist!
            self.hauptpos = "Mittelfeld"
        else:
            position = []
            for pos in pos_all:
                if pos.text.strip() == "Hauptposition:":
                    continue
                elif pos.text.strip() == "Nebenposition:":
                    continue
                else:
                    position.append(pos.text.strip())
            self.hauptpos = position.pop(0)
            if len(position) > 1: self.nebenpos = position.pop(1)
            if len(position) > 2: self.nebenpos = position.pop(2)

    def __search_allinbox(self, soup):
        # einlesen der kompletten Box auf der linken Seite und ausfiltern der benötigten Werte
        today = date.today()
        box = soup.find("div", {"class": re.compile('info-table info-table--right-space.*')})
        box_left = [left.text.strip() for left in
                    box.find_all("span", {"class": "info-table__content info-table__content--regular"})
                    if left.text.strip() not in ('Aktueller Verein:', 'Social Media:', 'Spielerberater:')]
        box_right = [right.text.strip() for right in
                     box.find_all("span", {"class": "info-table__content info-table__content--bold"})]

        # Fügt beide Boxen zusammen, um sie dann einzeln auf die Klassenvariablen zu verteilen
        box_elements = list(zip(box_left, box_right))
        for ele in box_elements:
            if "Geburtsdatum:" in ele[0]:
                datum = ele[1].replace('Happy Birthday', '').strip()
                self.gebdatum = datetime.strptime(datum, '%d.%m.%Y').date() if 'Happy Birthday' in ele[
                    1] else datetime.strptime(ele[1], '%d.%m.%Y').date()
            elif 'Nationalität:' in ele[0]:
                self.nation = re.split(r'\s+', ele[1]) if ele[1] is not None else None
            elif 'Größe:' in ele[0]:
                gross = re.findall(r'-?\d+\.?\d*', ele[1]) if ele[1] is not None else None
                self.groesse = gross[0] + gross[1] if gross is not None else None
            elif "Fuß:" in ele[0]:
                self.fuss = ele[1] if ele[1] is not None else None
            elif "Im Team seit:" in ele[0]:
                datum = '01.01.' + str(today.year) if '-' in ele[1] else ele[1]
                datum = '01.' + ele[1] if len(ele[1]) == 7 else datum
                self.imteamseit = datetime.strptime(datum, '%d.%m.%Y').date() if ele[1] is not None else None
            elif "Vertrag bis:" in ele[0]:
                datum2 = '30.06.' + str(today.year) if '-' in ele[1] else ele[1]
                datum2 = '01.' + ele[1] if len(ele[1]) == 7 else datum2
                self.vertragbis = datetime.strptime(datum2, '%d.%m.%Y').date() if ele[1] is not None else None

    def __randrange_float(self, start, stop, step):
        # Hilfsfunktion für player_values
        return random.randint(0, int((stop - start) / step)) * step + start

    def __player_values(self, price):
        _VALUES = {
            0: {'Technik': 1, 'Einsatz': 1, 'Schnelligkeit': 1},
            50000: {'Technik': 5, 'Einsatz': 5, 'Schnelligkeit': 4},
            100000: {'Technik': 8, 'Einsatz': 8, 'Schnelligkeit': 7},
            250000: {'Technik': 15, 'Einsatz': 15, 'Schnelligkeit': 13},
            500000: {'Technik': 25, 'Einsatz': 25, 'Schnelligkeit': 20},
            1000000: {'Technik': 50, 'Einsatz': 50, 'Schnelligkeit': 30},
            1800000: {'Technik': 70, 'Einsatz': 70, 'Schnelligkeit': 50},
            3000000: {'Technik': 75, 'Einsatz': 75, 'Schnelligkeit': 60},
            10000000: {'Technik': 80, 'Einsatz': 80, 'Schnelligkeit': 70},
            50000000: {'Technik': 90, 'Einsatz': 90, 'Schnelligkeit': 80},
            100000000: {'Technik': 95, 'Einsatz': 95, 'Schnelligkeit': 90},
            200000000: {'Technik': 99, 'Einsatz': 99, 'Schnelligkeit': 99}
        }
        prices = list(_VALUES.keys())
        left_price = max([p for p in prices if p <= price])
        right_price = min([p for p in prices if p > price])

        weight_left = (right_price - price) / (right_price - left_price)
        weight_right = 1 - weight_left

        attributes = {}
        for attribute in ['Technik', 'Einsatz', 'Schnelligkeit']:
            value_left = _VALUES[left_price][attribute]
            value_right = _VALUES[right_price][attribute]
            attributes[attribute] = round(weight_left * value_left + weight_right * value_right)
        if price > 55000 and price < 70000000:
            if price > 10000 and price < 500001:
                m = attributes['Technik'] // 5
            else:
                if random.randint(0, 6) == 5:
                    m = attributes['Technik'] // 5
                else:
                    m = attributes['Technik'] // 10
            r = self.__randrange_float(1, m, 0.1)
            wurf = random.randint(0, 5)
            if wurf == 0:
                attributes['Technik'] = round(attributes['Technik'] + r)
                attributes['Einsatz'] = round(attributes['Einsatz'] - r)
            elif wurf == 1:
                attributes['Einsatz'] = round(attributes['Einsatz'] + r)
                attributes['Technik'] = round(attributes['Technik'] - r)
            elif wurf == 2:
                attributes['Einsatz'] = round(attributes['Einsatz'] + r)
                attributes['Schnelligkeit'] = round(attributes['Schnelligkeit'] - r)
            elif wurf == 3:
                attributes['Einsatz'] = round(attributes['Einsatz'] - r)
                attributes['Schnelligkeit'] = round(attributes['Schnelligkeit'] + r)
            elif wurf == 4:
                attributes['Technik'] = round(attributes['Technik'] + r)
                attributes['Schnelligkeit'] = round(attributes['Schnelligkeit'] - r)
            elif wurf == 5:
                attributes['Technik'] = round(attributes['Technik'] - r)
                attributes['Schnelligkeit'] = round(attributes['Schnelligkeit'] + r)

            for attribute in ['Technik', 'Einsatz', 'Schnelligkeit']:
                if attributes[attribute] > 99: attributes[attribute] = 99
        self.technik = attributes['Technik']
        self.einsatz = attributes['Einsatz']
        self.schnelligkeit = attributes['Schnelligkeit']


##############################################################
# Für kuze tests bei umbauten an der Klasse!

# s = Player('https://www.transfermarkt.de/curtis-durose/profil/spieler/951159')
# print(s.get_firstname())
# print(s.get_lastname())
# print(s.get_trikotnr())
# print(s.get_geburtstag())
# print(s.get_fuss())
# print(s.get_groesse())
# print(s.get_land())
# print(s.get_nationalspieler())
# print(s.get_marktwert())
# print(s.get_imteamseit())
# print(s.get_vertragbis())
# print(s.get_hauptpos())
# print(s.get_nebenpos())
# print(s.get_nebenpos2())
# print(s.get_technik())
# print(s.get_einsatz())
# print(s.get_schnelligkeit())
