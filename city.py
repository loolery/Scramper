import functions as func

class Stadt():

    def __init__(self):
        self.name, self.bundesland = '', ''
        self.einwohner = 0

results = func.wiki_suche('https://de.wikipedia.org/wiki/Liste_der_Gro%C3%9Fst%C3%A4dte_in_Deutschland')
for di in results:
    print(f'{di[0]} --> {di[1][0]} --> {di[1][1]}')