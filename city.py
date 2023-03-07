import functions as func

class Stadt():

    def __init__(self):
        self.name, self.bundesland = '', ''
        self.einwohner = 0

results = func.staedte_suche('https://de.wikipedia.org/wiki/Liste_der_St%C3%A4dte_in_Frankreich')
for di in results:
    print(f'{di[0]} --> {di[1][0]} --> {di[1][1]}')