import re
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
def search_teamlinks(url):
    # searching for the teamlinks on transfermarkt.de, needs the url of a country
    team_link = []
    soup = soupobj(url)
    table = soup.find_all("td", {"class": "hauptlink no-border-links"})
    for t in table:
        a = t.find("a", href=True)
        team_link.append('https://www.transfermarkt.de' + a.get('href', None))
    #if no teams found, try a different way
    if(len(team_link) == 0):
        table =soup.find_all("span", {"class": "vereinsname"})
        for t in table:
            a = t.find("a", href=True)
            if(a.get('href', None).find('spielplan')):
                link = 'https://www.transfermarkt.de' + a.get('href', None).replace('spielplan', 'kader')
            team_link.append(link)
    return team_link


url = "https://www.transfermarkt.de/campeonato-brasileiro-serie-c/startseite/pokalwettbewerb/BRA3"
print(f'{search_teamlinks(url)}')

