import requests
import requests_cache
import subprocess
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

def ligen_suche(id):
    # Sucht bei Transfermarkt.de nach den ID´s der einzelnen Ligen eines Landes und gibt diese zurück.
    dictionary = {}
    count, count2 = 0, 0
    img, href = [], []
    soup = soupobj('https://www.transfermarkt.de/wettbewerbe/national/wettbewerbe/' + id)
    try:
        table = soup.find("table", {"class": "items"})
        for link in table.find_all("img", {"class": "continental-league-emblem"}):
            img.append(link.get('src', None))
        for link2 in table.find_all("a"):
            href.append(link2.get('href', None))
    except:
        print('  -> cancel')
    else:
        try:
            for tab in soup.find_all("td", {"class": "extrarow bg_blau_20 hauptlink"}):
                if '.Liga' in tab.text:
                    if count >=1 and tab.text == '1.Liga' or count >= 3: break # schützt vor wiederholungen und reduziert auf max. 3 Ligen.
                    name = tab.text
                    url = href[count2 + 1]
                    picture = img[count]
                    dictionary[name] = [url, picture]
                count+=1
                count2+=2
        except:
            print('break')
    print('\n')
    return dictionary.items()

