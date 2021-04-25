import requests
import datetime
import pandas as pd
from os import path
from functools import partial
from bs4 import BeautifulSoup as bs

SUMMONER_NAME = 'buggga'
REGION        = 'euw'
FILE_NAME     = 'match_history.txt'

SCHEDULE = {'Monday'   : (20, 23),
            'Tuesday'  : (20, 23),
            'Wednesday': (20, 23),
            'Thursday' : (20, 23),
            'Friday'   : (20, 23),
            'Saturday' : (20, 23),
            'Sunday'   : (20, 23)}

class StringConverter(dict):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return str

    def get(self, default=None):
        return str



class shame():
    def __init__(self):
        self.last_games_df  = pd.DataFrame({'A' : []})
        self.games_df = pd.DataFrame({'A' : []})
        self.schedule       = SCHEDULE

    def get_last_games(self):
    
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
    
            games.append([game_id, 
                          time_stamp, 
                          'False', 
                          'True', 
                          'False', 
                          game_type, 
                          game_result, 
                          game_length, 
                          champion, 
                          level, 
                          kda])
    
        games.reverse()
        self.last_games_df = pd.DataFrame(games, columns = ['ID', 
                                                            'Time Stamp', 
                                                            'Checked', 
                                                            'Allowed', 
                                                            'Sentenced', 
                                                            'Type', 
                                                            'Result', 
                                                            'Length', 
                                                            'Champion', 
                                                            'Level', 
                                                            'KDA'])

    def update_match_history(self):
        FILE_EXISTS = path.exists(FILE_NAME)
    
        self.get_last_games()
    
        if not FILE_EXISTS:
            self.last_games_df.to_csv(FILE_NAME, index=False)
            return self.last_games_df
        else:
            self.games_df = pd.read_csv(FILE_NAME, converters=StringConverter())
            last_saved_id = self.games_df['ID'].iloc[-1]
    
            if last_saved_id in self.last_games_df['ID'].values:
                i = self.last_games_df.index[self.last_games_df['ID'] == last_saved_id].tolist()[0]
                self.last_games_df = self.last_games_df.iloc[i+1:]
    
            self.games_df = self.games_df.append(self.last_games_df, ignore_index=True)
    
            if self.games_df['ID'].size > 20:
                self.games_df = self.games_df.iloc[-20:]
    
            self.games_df.to_csv(FILE_NAME, index=False)

    def check_and_allow(self):
        for index, game in self.games_df.loc[self.games_df['Checked'] == 'False'].iterrows():
            timestamp = game['Time Stamp']
            date, time = timestamp.split()
            year, month, day = (int(x) for x in date.split('-'))   
            hour, minute, second = (int(x) for x in time.split(':'))   
            proper_time = datetime.date(year, month, day)
            weekday = proper_time.strftime('%A')
            hour1, hour2 = self.schedule[weekday]
            print(hour1, hour, hour2)
            if hour1 <= hour <= hour2:
                self.games_df['Allowed'][index] = 'True'
            else:
                self.games_df['Allowed'][index] = 'False'

            self.games_df['Checked'][index] = 'True'




if __name__ == '__main__':
    bot = shame()
    bot.update_match_history()
    print(bot.games_df)
    bot.check_and_allow()
    print(bot.games_df)
