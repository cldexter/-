# coding=utf-8

from bs4 import BeautifulSoup
from bookkeeper import Bookkeeper
import requests
import json, time
import browserbot
import logging
import sys

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}



class Robot:

    engine = ''
    config_general = {}
    config_engine = {}  
    __s = requests.Session()
    __next_version = ''
    is_zero_query = True
    is_first_query = True

    def __init__(self, engine_select):
        ## Init logger
        if len(sys.argv) > 1:
            level_name = sys.argv[1]
            level = LEVELS.get(level_name, logging.NOTSET)
            logging.basicConfig(level=level)
        # create logger
        self.logger = logging.getLogger("robot")
        self.logger.setLevel(logging.DEBUG)
        
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # add formatter to ch
        ch.setFormatter(formatter)
        
        # add ch to logger
        self.logger.addHandler(ch)

        self.logger.info('logger init complete.')


        ## Read general config file
        config_general_file = open('config/config.json', 'r')
        self.config_general = json.loads(config_general_file.read())

        ## Read engine config file
        has_engine = False
        for engine in self.config_general['engines']:
            if engine_select == engine:
                self.engine = engine_select
                has_engine = True
            
        if has_engine == False:
            raise Exception("No such engine!")
        
        config_engine_file = open('config/config_' + engine_select + '.json', 'r')
        self.config_engine = json.loads(config_engine_file.read())

        config_general_file.close()
        config_engine_file.close()

        ## Fake request headers
        ### User-agent
        self.__s.headers.update({'User-Agent': self.config_general['user_agent']})

        ## Init Bookkeeper
        self.container = Bookkeeper()
        self.container.start()  ### Start listening

        ## Init browser-bot
        self.browserbot = browserbot.browserbot(self.logger, self.config_general, self.config_engine)
        self.browserbot.start() ### Start listening

    def query(self):

        ## Assemble payload
        payload = {}
        if self.is_first_query:
            # if self.is_zero_query:
            #     self.is_zero_query = False
            #     payload = self.config_engine['url_params']['query_0']
            # else:
            #     self.is_first_query = False
            #     payload = self.config_engine['url_params']['query_1']

            
            payload = self.config_engine['url_params']['query_1']
            
        else:
            payload  = self.config_engine['url_params']['query']
            payload['versions'] = self.__next_version

        time_str = str(int(time.time() * 1000))
        payload['_'] = time_str

        ## Actually triggers the request
        result = self.__s.get(self.config_engine['url_list']['query'], params = payload)
        print result.url + ', ' + str(result.status_code)

        ## Extract next version, for later queries
        response_obj = json.loads(result.text)
        ### There are two f**king kinds of data file, which appears randomly, so must determine file type
        if response_obj.has_key('i-ots'):   ### Normal/full df
            self.__next_version = response_obj['i-ots'][0]['v']
            self.container.set('set', result.text)
        elif response_obj.has_key('us'):    ### Append style df
            self.__next_version = response_obj['us'][0]['v']
            self.container.set('append', result.text)
        else:
            pass
        print self.__next_version

        ## Switch status
        self.is_first_query = False


    def transaction(self, action_id, quantity):
        self.browserbot.add(action_id, quantity)



