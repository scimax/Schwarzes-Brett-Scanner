
from lxml import html
import requests
from bs4 import BeautifulSoup
from win10toast import ToastNotifier
import itertools
from urllib.parse import urljoin
import json
from enum import Enum
import time

class Status(Enum):
    INIT = 0
    READY = 1
    RUNNING = 2
    STOP = 3
class SchwarzesBrettScanner:
    def __init__(self, updatefreq, sms_key, telephone_numbers):
        '''
        updatefreq: float
            number of seconds to wait before next request
        sms_key: string
            The key of textbelt for sending custom sms messages
        telephone_numbers: list of numbers 
        '''
        self.root_url= "http://schwarzesbrett.bremen.de"
        self.page_url= "http://schwarzesbrett.bremen.de/verkauf-angebote/rubrik/wohnung-mietangebote-verkauf.html"
        page=requests.get(self.page_url)
        self.soup =BeautifulSoup(page.content, 'html.parser')
        self.current_ads = []
        self.initializeAdList()
        self.toaster = ToastNotifier()
        self.smsrecipients = telephone_numbers
        self.textbelt_key = sms_key
        self.freq = updatefreq
        self.STATUS = Status.INIT
        
    def initializeAdList(self):
        first_two_ad_lists = self.soup.find_all(SchwarzesBrettCrawler.has_class_eintraege_list)[:2]
        map_list= []
        for ad_list in first_two_ad_lists:
            map_list.append(map(lambda t: (' '.join(t.get_text().split()), t.get("href")), ad_list.find_all("a")))
        self.current_ads = set(itertools.chain(*map_list))
        
    def has_class_eintraege_list(tag):
        return tag.has_attr('class') and tag['class']==['content_list', 'eintraege_list']
    
    def run(self):
        self.STATUS = Status.RUNNING
        while self.STATUS == Status.RUNNING:
            self.run_request()
            time.sleep(self.freq)
    
    def run_request(self):
        first_ad_list = self.soup.find_all(SchwarzesBrettCrawler.has_class_eintraege_list)[0]
#         t= first_ad_list.find("a")
        current_ads = set(map(lambda t: (' '.join(t.get_text().split()), t.get("href")), first_ad_list.find_all("a")))
        new_ads = current_ads.difference(self.current_ads)
        
        if new_ads != set():
            for entry in new_ads:
                self.notify(*entry)
                self.notifyViaSMS(*entry)
            self.current_ads.update(new_ads)
        else:
            print("No new entries")
            self.notify("No new entries", "")
#        
    def notify(self, title, urlpath):
        self.toaster.show_toast("Neues vom Schwarzen Brett Bremen!",
                   "'{0}' at {1}".format(title, urljoin(self.root_url, urlpath)),
                   icon_path=None,
                   duration=10)
        
    def notifyViaSMS(self, title, urlpath):
        for number in self.smsrecipients:
            response = requests.post('https://textbelt.com/text', {
              'phone': number,
              'message': "'{0}' at {1}".format(title, urljoin(self.root_url, urlpath)),
              'key': self.textbelt_key,
            })
            j = json.loads(response.content)
            print(j)
            if (not j["success"]) or (j["quotaRemaining"] % 10 == 0):
                mail_sender_url = "https://prod-46.westeurope.logic.azure.com/workflows/919925594201414699126d563fde532c/triggers/manual/paths/invoke/" + \
                "textbelt/" + str(j["success"]) +"/" + str(j["quotaRemaining"])+\
                "?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=XargkUCoOlRNuFSqkWKeuSvakUSE4wMuG68ZWH_BUT0"
                requests.get(mail_sender_url)                
                
            
        