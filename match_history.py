import requests
import pandas as pd
from os import path
from functools import partial
from bs4 import BeautifulSoup as bs

SUMMONER_NAME = 'buggga'
REGION = 'euw'

def get_last_games():

    def content_(game, text):
        div = game.find_all('div', text)[0]
        return [ s.strip() for s in div.strings if s.strip() ]

    page = requests.get('https://' + REGION + '.op.gg/summoner/userName=' + SUMMONER_NAME)
    soup = bs(page.content, 'html.parser')
    games_html = list(soup.find_all('div', class_='GameItemWrap'))
    games = []

    for game in games_html:
        content = partial(content_, game)

        game_id     = game.find('div', class_='GameItem')['data-game-id']
        time_stamp  = content('TimeStamp')[0]
        game_type   = content('GameType')[0]
        game_result = content('GameResult')[0]
        game_length = content('GameLength')[0]
        champion    = content('ChampionName')[0]
        level       = content('Level')[0][5:]
        kda         = "".join(content('KDA')[:5])

        games.append([game_id, time_stamp, game_type, game_result, game_length, champion, level, kda])

    return pd.DataFrame(games.reverse, columns = ['ID', 'Time Stamp', 'Type', 'Result', 'Length', 'Champion', 'Level', 'KDA'])

df = get_last_games()

FILE_NAME = 'match_history.txt'
FILE_EXISTS = path.exists(FILE_NAME)

if FILE_EXISTS:
    df.to_csv(FILE_NAME, index=False, mode='a', header=False)
else:
    df.to_csv(FILE_NAME)

