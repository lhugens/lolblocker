import requests
import pandas as pd
from os import path
from functools import partial
from bs4 import BeautifulSoup as bs

SUMMONER_NAME = 'buggga'
REGION        = 'euw'
FILE_NAME     = 'match_history.txt'

class StringConverter(dict):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return str

    def get(self, default=None):
        return str

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

    games.reverse()
    return pd.DataFrame(games, columns = ['ID', 'Time Stamp', 'Type', 'Result', 'Length', 'Champion', 'Level', 'KDA'])

def update_match_history():
    FILE_EXISTS = path.exists(FILE_NAME)

    last_games_df = get_last_games()

    if not FILE_EXISTS:
        last_games_df.to_csv(FILE_NAME, index=False)
    else:
        saved_games_df = pd.read_csv(FILE_NAME, converters=StringConverter())
        last_saved_id = saved_games_df['ID'].iloc[-1]

        if last_saved_id in last_games_df['ID'].values:
            i = last_games_df.index[last_games_df['ID'] == last_saved_id].tolist()[0]
            last_games_df = last_games_df.iloc[i+1:]

        if saved_games_df['ID'].size > 60:
            saved_games_df = saved_games_df.iloc[20:]
            saved_games_df.to_csv(FILE_NAME, index=False)

        last_games_df.to_csv(FILE_NAME, index=False, mode='a', header=False)

if __name__ == '__main__':
    update_match_history()
