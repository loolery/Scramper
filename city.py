import functions as func

class Stadt():

    def __init__(self):
        self.name, self.bundesland = '', ''
        self.einwohner = 0

def wiki_suche(url):
    soup = func.soupobj(url)
    dictionary = {}
    chars = "0123456789,"
    # Suche die Tabelle im Quelltext
    try: table = soup.find("table", {"class": "wikitable"})
    except: result = None   #Tabelle konnte nicht gefunden werden.
    else:
        #Suche nach den Daten in den Feldern 'Name' & '2021'
        for row in table.find_all("tr"):
            print(row)
            name_col = row.find("a", href=True)
            if name_col is not None:
                name = name_col.text.strip()
                print(name)
                for char in chars:
                    name = name.replace(char, "")
                data_cols = row.find_all("td")
                einw_2021 = data_cols[-2].text.strip().replace('.', '')
                bundesland = data_cols[-1].text.strip().split(u'\xa0')[0]
                dictionary[name] = [bundesland, einw_2021]
                result = dictionary.items()
    return result

results = wiki_suche('https://de.wikipedia.org/wiki/Liste_der_Gro%C3%9F-_und_Mittelst%C3%A4dte_in_Deutschland')
for di in results:
    print(f'{di[0]} --> {di[1][0]} --> {di[1][1]}')