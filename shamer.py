import os
import smtplib
import logging
import requests
import datetime
import pandas as pd
from os                                             import path
from functools                                      import partial
from time                                           import sleep
from bs4                                            import BeautifulSoup as bs
from contextlib                                     import contextmanager
from selenium.webdriver.support.ui                  import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.chrome.options              import Options
from selenium                                       import webdriver
from selenium.webdriver.common.by                   import By
from selenium.webdriver.support                     import expected_conditions as EC

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logging.info('Admin logged in')

from user_settings import *

URL = 'https://' + REGION + '.op.gg/summoner/userName=' + SUMMONER_NAME

class time_handler:
    # timestamp should be in the format '2021-05-01 14:34:46'
    def __init__(self, timestamp):
        date, time = timestamp.split()
        self.timestamp = timestamp
        year, month, day    = (int(x) for x in date.split('-'))   
        hour, minute,second = (int(x) for x in time.split(':'))   
        self.dt = datetime.datetime(year, month, day, hour, minute, second)
        self.weekday = self.dt.strftime('%A')

    def update_timestamp(self):
        int_to_2str = lambda i: str(i).zfill(2)
        int_to_4str = lambda i: str(i).zfill(4)
        year    = int_to_4str(self.dt.year)
        month   = int_to_2str(self.dt.month)
        day     = int_to_2str(self.dt.day)
        hour    = int_to_2str(self.dt.hour)
        minute  = int_to_2str(self.dt.minute)
        second  = int_to_2str(self.dt.second)
        self.timestamp = f'{year}-{month}-{day} {hour}:{minute}:{second}'
    
    def fix_time(self, offset):
        self.dt = self.dt + datetime.timedelta(hours = offset)
        self.weekday = self.dt.strftime('%A')
        self.update_timestamp()

# EXAMPLE
"""
timestamp = '2021-05-01 02:51:49'
clock = time_handler(timestamp)
print(clock.timestamp)
clock.fix_time(-8)
print(clock.timestamp)
"""

class selenium_bot:
    def __init__(self, headless = False):
        driver_path = os.path.realpath('./')+'/chromedriver'
        chrome_options = Options()
        if headless == True:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("start-maximized")
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        self.d = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    def get(self, url):
        self.d.get(url)

    def element_present(self, text, wait_time):
        try:
            element = WebDriverWait(self.d, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, text)))
        except:
            return False
        return True

    def click_class_name(self, text, wait_time):
        if self.element_present(text, wait_time):
            try:
                self.d.find_element_by_class_name(text).click()
                return True
            except:
                return False

"""
# EXAMPLE
bot = selenium_bot()
bot.get(URL)
bot.click_class_name('css-1tbbj19', 10)
bot.click_class_name('Button', 10)
sleep(5)
bot.d.quit()
"""

class email_handler:
    def __init__(self, email_user, email_pass):
        self.email_user = email_user
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email_user, email_pass)
        self.server = server

    def send_mail(self, receiver, message):
        self.server.sendmail(self.email_user, receiver, message)

"""
# EXAMPLE
m = email_handler(EMAIL, EMAIL_PASSWORD)
m.send_mail(RECEIVERS[0], MESSAGE)
"""

class StringConverter(dict):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return str

    def get(self, default=None):
        return str

class shamer:
    def __init__(self):
        self.games_df = pd.DataFrame({'A' : []})
        self.last_games_df = pd.DataFrame({'A' : []})
        self.soup = []
        self.updated = False

    @staticmethod
    def update_op_gg():
        logging.info(f'Clicking "Update" in op.gg')
        bot = selenium_bot(True)
        bot.get(URL)
        bot.click_class_name('css-1tbbj19', 10)
        bot.click_class_name('Button', 10)
        sleep(5)
        bot.d.quit()

    def update_page(self):
        page = requests.get(URL, timeout=(3.05, 5))
        self.soup = bs(page.content, 'html.parser')
        update_status = shamer.content_(self.soup, 'Buttons')[0]
        if update_status == 'Updated':
            self.updated = True
        else:
            self.updated = False
            shamer.update_op_gg()

    @staticmethod
    def content_(game, text):
        div = game.find_all('div', text)[0]
        return [ s.strip() for s in div.strings if s.strip() ]

    def get_last_games(self):
        logging.info(f'Reading op.gg page content')
        self.update_page()
        logging.info(f'Getting games from op.gg')
        games_html = list(self.soup.find_all('div', class_='GameItemWrap'))
        games = []
    
        for game in games_html:
            content = partial(shamer.content_, game)
    
            game_id     = game.find('div', class_='GameItem')['data-game-id']
            time_stamp  = content('TimeStamp')[0]
            game_type   = content('GameType')[0]
            game_result = content('GameResult')[0]
            game_length = content('GameLength')[0]
            champion    = content('ChampionName')[0]
            level       = content('Level')[0][5:]
            kda         = "".join(content('KDA')[:5])

            clock = time_handler(time_stamp)
            clock.fix_time(OFFSET)
            time_stamp = clock.timestamp
    
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

    def save_to_txt(self):
        logging.info(f'Saving games to {FILE_NAME}')
        self.games_df.to_csv(FILE_NAME, index=False)

    def update_match_history(self):
        FILE_EXISTS = path.exists(FILE_NAME)
    
        self.get_last_games()
    
        if not FILE_EXISTS:
            logging.info(f'{FILE_NAME} does not exist. Creating one and saving games.')
            self.last_games_df.to_csv(FILE_NAME, index=False)
            self.games_df = self.last_games_df
        else:
            self.games_df = pd.read_csv(FILE_NAME, converters=StringConverter())
            last_saved_id = self.games_df['ID'].iloc[-1]
    
            if last_saved_id in self.last_games_df['ID'].values:
                i = self.last_games_df.index[self.last_games_df['ID'] == last_saved_id].tolist()[0]
                self.last_games_df = self.last_games_df.iloc[i+1:]
    
            self.games_df = self.games_df.append(self.last_games_df, ignore_index=True)
    
            if self.games_df['ID'].size > 20:
                self.games_df = self.games_df.iloc[-20:]
    
            self.save_to_txt()

    def check_and_allow(self):
        logging.info(f'Checking legimitacy of games')
        for index, game in self.games_df.loc[self.games_df['Checked'] == 'False'].iterrows():
            timestamp = game['Time Stamp']
            clock = time_handler(timestamp)

            hour1, hour2 = SCHEDULE[clock.weekday]
            if hour1 <= clock.dt.hour <= hour2:
                self.games_df['Allowed'][index] = 'True'
            else:
                self.games_df['Allowed'][index] = 'False'

            self.games_df['Checked'][index] = 'True'

    def sentence(self):
        if not self.games_df.loc[self.games_df['Sentenced'] == 'False'].empty:
            logging.info(f'Illegimate games detected. Sending emails.')
            m = email_handler(EMAIL, EMAIL_PASSWORD)
            m.send_mail(RECEIVERS[0], MESSAGE)
            self.games_df['Sentenced'] = 'True' 
            self.save_to_txt()

    def print_status(self):
        print(self.games_df)
    
if __name__ == '__main__':
    s = shamer()
    
    while True:
        s.update_match_history()
        s.check_and_allow()
        s.sentence()
        s.print_status()
        sleep(1200)
