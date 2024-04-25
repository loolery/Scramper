import re
from datetime import datetime
import functions as func

class Verein():
    __tname, __transfermarktid = '', ''
    __turl, __tdatenurl = '', ''
    __teamcolor, __playerlinks = [], []
    __ligarang, __stadionnamen, __stadiongroesse, __gruendung = None, '', 0, ''
    __stadt, __transfermarktid = None, None

    def __init__(self, url):
        self.__turl = url
        self.__tdatenurl = self.__turl.replace('startseite', 'datenfakten')
        match = re.search(r'\d+(?=/\Z)', self.__turl)
        if match: self.__tid = match.group()
        match = re.search(r'markt\.de/(.*?)/startseite', self.__turl)

        # # entfernt - aus den Namen und wandelt den ersten Buchstaben in einen Grossbuchstaben um
        # if match: self.__tname = match.group(1).replace('-', ' ').title()
        # # wandelt abkürzungen wie z.B. FC in Grossbuchstaben um
        # if len(self.__tname.split(' ')[0]) <= 3:
        #     self.__tname = self.__tname.replace(self.__tname.split(' ')[0], self.__tname.split(' ')[0].upper())
        # if len(self.__tname.split(' ')[-1]) <= 3:
        #     self.__tname = self.__tname.replace(self.__tname.split(' ')[-1], self.__tname.split(' ')[-1].upper())
        # if '1 Fc' in self.__tname:
        #     self.__tname = self.__tname.replace('1 Fc', '1.FC')

        soup = func.soupobj(self.__turl)
        self.__search_teamname(soup)
        self.__search_transfermarktid(soup)
        self.__search_ligarang(soup)
        self.__search_stadion(soup)
        self.__search_gruendung(soup)
        self.__search_playerlink(soup)
        self.__search_teamcolor(self.__tdatenurl)
        self.__search_stadt(self.__tdatenurl)

    def get_transfermarktid(self):
        return self.__transfermarktid

    def get_teamname(self):
        return self.__tname

    def get_ligarang(self):
        return self.__ligarang

    def get_stadionname(self):
        return self.__stadionnamen
    def get_stadionsize(self):
        return self.__stadionsize

    def get_gruendung(self):
        return self.__gruendung

    def get_teamcolor(self):
        colors = ""
        for tc in self.__teamcolor:
            tc = str(tc)
            colors += tc.replace("[", "").replace("]", "").replace("'", "")
        return colors

    def get_playerlinks(self):
        return self.__playerlinks

    def get_stadtid(self):
        stadtid = func.getStadtId(self.__stadt)
        return stadtid

    def __search_teamname(self, soup):
        self.__tname = soup.find('div', {'class': 'data-header__headline-container'}).get_text().strip()

    def __search_transfermarktid(self, soup):
        print(self.__turl)
        try:
            self.__transfermarktid = soup.find('div', {'class': 'row hide-on-print', 'id': 'subnavi'})['data-id']
        except:
            self.__transfermarktid = soup.find('tm-subnavigation')['id']

    def __search_ligarang(self, soup):
        try:
            table = soup.find("div", {"class": "data-header__box--big"})
            table1 = table.find_all("span", {"class": "data-header__content"})
        except:
            self.__ligarang = 0
        else:
            if table1[1].text.strip() == '':
                self.__ligarang = 0
            else:
                self.__ligarang = table1[1].text.strip()

    def __search_playerlink(self, soup):
        self.__playerlinks = []
        table = soup.find_all("td", {"class": "hauptlink"})
        for t in table:
            a = t.find("a", href=True)
            if a is not None and '/profil/' in a.get('href', None):
                self.__playerlinks.append('https://www.transfermarkt.de' + a.get('href', None))

    def __search_stadion(self, soup):
        table = soup.find("div", {"class": "data-header__details"})
        table1 = table.find_all("span", {"class": "data-header__content"})
        for t in table1:
            a = t.find_all("a", href=True)
            for b in a:
                if '/stadion/' in b.get('href', None):
                    self.__stadionnamen = b.get_text().replace("'", " ")
        table2 = soup.find_all('span', class_='tabellenplatz')[-1]
        self.__stadionsize = table2.text.split()[0].replace(".", "")

    def __search_gruendung(self, soup):
        table = soup.find("div", {"class": "info-table info-table--equal-space"})
        if table != None:
            table1 = table.find_all("span", {"class": "info-table__content info-table__content--bold"})
            for t in table1:
                if re.search('^[0-3][0-9][/.][0-3][0-9][/.](?:[0-9][0-9])?[0-9][0-9]$', t.get_text()):
                    self.__gruendung = datetime.strptime(t.get_text(), '%d.%m.%Y').date()
        else:
            self.__gruendung = None

    def __search_teamcolor(self, url):
        self.__teamcolor = []
        soup = func.soupobj(url)
        table = soup.find("p", {"class": "vereinsfarbe"})
        if table is None or len(table) == 0:
            self.__teamcolor.append('#FFFFFF')    #keine Vereinsfarben gefunden!
        else:
            table1 = table.find_all("span", style=True)
            for t in table1:
                if len(t) == 0:
                    print("nothing in data!")
                else:
                    if re.findall('#(?:[0-9a-fA-F]{3}){1,2}', t.get('style')):
                        self.__teamcolor.append(re.findall('#(?:[0-9a-fA-F]{3}){1,2}', t.get('style', None)))

    def __search_stadt(self, url):
        soup = func.soupobj(url)
        stadt_element = soup.find("table", {"class": "profilheader"})
        stadt_tr = stadt_element.find_all("tr")
        for st in stadt_tr:
            if st is not None:
                text = st.text.strip()
                regex = r"\(Einwohner:"
                if re.search(r"\(Einwohner:", text):
                    text = text.replace('<span class="tabellenplatz">', '')
                    regex = r"\b(\w+)\s+\("
                    match = re.search(regex, text)
                    if match:
                        self.__stadt = match.group(1).strip()
                        break

def search_teamlink(url):
    # Gibt eine Liste aller gefunden Vereinslinks in der Liga zurück.
    team_link = []
    soup = func.soupobj(url)
    table = soup.find_all("td", {"class": "hauptlink no-border-links"})
    for t in table:
        a = t.find("a", href=True)
        team_link.append('https://www.transfermarkt.de' + a.get('href', None))
    return team_link

#Code um die Klasse allein bei veränderungen zu testen.
teams = search_teamlink('https://www.transfermarkt.de/kyrgyz-premier-league/startseite/wettbewerb/KG1L')
verein = []
for t in teams:
    objVerein = Verein(t)
    verein.append(objVerein)
    print(f"Vereinsdaten von {objVerein.get_teamname()} sind geladen.")
print("\n")
for v in verein:
    print(' ======================================== \n')
    print(f'Team: {v.get_teamname()}')
    print(f'ID: {v.get_transfermarktid()}')
    print(f'Tabellenplatz: {v.get_ligarang()}')
    print(f'Stadion: {v.get_stadionname()}')
    print(f'Stadion größe: {v.get_stadionsize()}')
    print(f'Grundungstag: {v.get_gruendung()}')
    print(f'Vereinsfarben: {v.get_teamcolor()}')
    print(f'Stadt: {str(v.get_stadtid())}')
    playerlinks = v.get_playerlinks()
    for pl in playerlinks:
        print(f'   --> {pl}')
