import threading
import Queue

from selenium import webdriver
from time import sleep


login_scripts = open('js/login.js', 'r').read()
place_scripts = open('js/buy.js', 'r').read()
#print login_scripts

class browserbot(threading.Thread):

    debug = True
    is_logged_in = False

    def __init__(self, logger, config, config_engine):

        # Init
        self.logger = logger
        self.logger.debug('Starting Browserbot...')
        threading.Thread.__init__(self)
        self.login_scripts = open('js/login.js', 'r').read()
        self.place_scripts = open('js/buy.js', 'r').read()
        executable_path = config['webdriver_path']
        self.browser = webdriver.Chrome(executable_path = executable_path)
        self.queue = Queue.Queue()

        # First, login
        url_list = config_engine['url_list']
        self.browser.get(url_list['index'])
        self.browser.execute_script(self.login_scripts)
        sleep(5)
        self.browser.get(url_list['sportsbook'])
        self.browser.get(url_list['sports_index'])
        self.is_logged_in = True

        self.logger.debug('Browserbot started, listening now...')


    def run(self):
        # Once login is done, start listening for commands
        while(True):
            item = self.queue.get(True)
            action_id = item['action_id']
            quantity = item['quantity']
            if quantity > 0:
                self.debug = False
            elif quantity < 0:
                raise ValueError

            self.browser.execute_script(self.place_scripts % (action_id, quantity))
            sleep(3)
            if not self.debug:
                self.browser.switch_to_alert().accept()
            else:
                self.browser.switch_to_alert().dismiss()

    def add(self, action_id, quantity):
        item = {
            'quantity' : quantity,
            'action_id' : action_id
        }
        self.queue.put_nowait(item)



