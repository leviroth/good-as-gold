import pickle
from urllib.request import urlopen
from bs4 import BeautifulSoup


class Player:
    def __init__(self, name, cap=None, weight=None, pos=None):
        self.name = name
        self.cap = int(cap)
        self.weight = weight
        self.pos = pos

    def __str__(self):
        return self.name


class Team:
    def __init__(self, name, hyphenated, shortcode):
        self.name = name
        self.hyphenated = hyphenated
        self.shortcode = shortcode

    def __str__(self):
        return self.name


def printResults(teams):
    for team in teams:
        print(team.name)
        print(''.join('=' for _ in team.name))
        for p in team.over:
            print(p.name)
        print("\n")


def dumpMarkdown(teams, f):
    import locale
    locale.setlocale(locale.LC_ALL, '')
    for team in teams:
        f.write("# {}\n\n".format(team.name))
        f.write("| Player | Position | Weight | Cap Number |\n")
        f.write("| --- | --- | --- | --- |\n")
        for p in team.over:
            f.write("| {} | {} | {} | {} |\n"
                    .format(p.name, p.pos, p.weight,
                            locale.currency(p.cap, grouping=True)[:-3]))
        f.write("\n")

if __name__ == '__main__':
    goldprice = 132990

    with open('teams.p', 'rb') as f:
        teams = [Team(*x) for x in pickle.load(f)]

    for team in teams:
        print("Fetching {}".format(team.name))

        capsURL = \
            'http://overthecap.com/salary-cap/{}/'.format(team.hyphenated)
        caps = BeautifulSoup(urlopen(capsURL), "html.parser")

        capstable = caps.find(class_="salary-cap-table")
        capsrows = [list(x) for x in capstable.tbody.children if len(x) != 1]
        ourdict = {x[0].text: Player(x[0].text, x[6].text[1:].replace(',', ''))
                   for x in capsrows}

        weightsURL = \
            'http://www.nfl.com/teams/roster?team={}'.format(team.shortcode)
        weights = BeautifulSoup(urlopen(weightsURL), "html.parser")

        weightstable = weights.find(id='result')
        weightsrows = [list(x) for x in weightstable.tbody.children
                       if len(x) != 1]
        for row in weightsrows:
            try:
                name = ' '.join(row[3].text.lstrip().split(', ')[::-1])
                ourdict[name].weight = int(row[11].text)
                ourdict[name].pos = row[5].text
            except KeyError as e:
                print("Couldn't add player: {}".format(e))

        team.players = {p for p in ourdict.values() if p.weight is not None}
        team.over = {p for p in team.players
                     if p.cap * 100 > p.weight * goldprice * 16}

    with open('results.p', 'wb') as f:
        pickle.dump(teams, f)

    print("\n\n\n")

    printResults(teams)
    with open('results.md', 'w') as f:
        dumpMarkdown(teams, f)
