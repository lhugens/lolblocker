import os
from contextlib                                     import contextmanager
from selenium.webdriver.support.ui                  import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.chrome.options              import Options
from selenium                                       import webdriver
from selenium.webdriver.common.by                   import By
from selenium.webdriver.support                     import expected_conditions as EC

class BOT():
    def __init__(self):
        DRIVER_PATH = os.path.realpath('./')+'/chromedriver'
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("start-maximized")
        self.d = webdriver.Chrome(executable_path=DRIVER_PATH, options=chrome_options)

        with open('password_history.txt') as f:
            for line in f:
                pass
            last_line = line.rstrip("\n")

        self.username = "buggabugga1337"
        self.password = last_line

    def element_present(self, text):
        try:
            element = WebDriverWait(self.d, 30).until(EC.presence_of_element_located((By.CLASS_NAME, text)))
        except:
            return False
        return True

    def my_find_element_by_class_name(self, text):
        if self.element_present(text):
            return self.d.find_element_by_class_name(text)
        return None

    def my_find_elements_by_class_name(self, text):
        if self.element_present(text):
            return self.d.find_elements_by_class_name(text)
        return None


    def sign_in(self):
        try:
            self.my_find_element_by_class_name('riotbar-anonymous-link').click()
        except:
            try:
                self.my_find_element_by_class_name('riotbar-explore').click()
                self.my_find_element_by_class_name('riotbar-navmenu-link').click()
            except:
                pass

        self.my_find_elements_by_class_name('field__form-input')[0].send_keys(self.username)
        self.my_find_elements_by_class_name('field__form-input')[1].send_keys(self.password)
        self.my_find_element_by_class_name('mobile-button').click()

    def go_to_settings(self):
        try:
            self.my_find_element_by_class_name('riotbar-summoner-name').click()
            self.my_find_elements_by_class_name('riotbar-account-link')[1].click()
        except:
            try:
                self.my_find_element_by_class_name('riotbar-explore').click()
                self.my_find_element_by_class_name('riotbar-navmenu-link').click()
                self.my_find_elements_by_class_name('riotbar-navmenu-link')[11].click()
            except:
                pass

        self.my_find_element_by_class_name('field__form-input').send_keys(self.password)
        self.my_find_element_by_class_name('mobile-button').click()


    def change_password(self, new_password):
        self.my_find_elements_by_class_name('ds-field__form-input')[5].send_keys(self.password)
        self.password = new_password
        self.my_find_elements_by_class_name('ds-field__form-input')[6].send_keys(self.password)
        self.my_find_elements_by_class_name('ds-field__form-input')[7].send_keys(self.password)
        self.my_find_elements_by_class_name('ds-button')[3].click()



bot = BOT()
print(bot.password)
#bot.d.get("https://na.leagueoflegends.com/en-us/")
#bot.sign_in()
#bot.go_to_settings()

