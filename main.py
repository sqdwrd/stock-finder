# -*- encoding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import sys
import configparser
import re

log = 'stock.log'
cycle = True


def get_argv(num):
    try:
        return sys.argv[num]
    except IndexError:
        return None


def new_tab():
    driver.execute_script('window.open(\"about:blank\", \"_blank\")')
    driver.switch_to.window(driver.window_handles[0])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def repeat_cycle():
    minute = int(time.strftime('%M'))
    if debugMode:
        return True
    elif minute == 00:
        return True


if get_argv(1) == '--debug':
    debugMode = True
    configMode = False
elif get_argv(1) == '--config':
    debugMode = False
    configMode = True
else:
    debugMode = False
    configMode = False


class Shop:
    url = None
    time = None
    title = None
    bs = None
    html = None
    price = None
    deliver_price = None
    priceSelector = None

    def get_title(self):
        title = self.bs.select('head > title')
        title_str = str(title[0]).split('<title>')
        title_str = str(title_str[1]).split('</title>')
        title_str = str(title_str[0])
        return title_str


if configMode:
    config = configparser.ConfigParser()
    shops = ['1', '2']
    shop = input('choose shop [1 = Naver Shopping]\n>>')
    while shop not in shops:
        shop = input('\033[31m' + 'Shop incorrect!' + '\033[0m' + '\nchoose shop [1 = Naver Shopping]\n>>')
    if shop == '1':
        regex = re.compile('^https?://search.shopping.naver.com/catalog/')
        tempUrl = input("input URL\n>>")
        while regex.match(tempUrl) is None:
            tempUrl = input('\033[31m' + 'URL incorrect!' + '\033[0m' + '\ninput URL\n>>')
        config['NShopping'] = {}
        config['NShopping']['URL'] = tempUrl.replace('%', '%%')
        with open('config.ini', 'w') as configFile:
            config.write(configFile)

with open(log, 'a', -1, 'utf-8') as f:
    if debugMode:
        print(time.strftime('[%x,%X] ') + '-------------디버깅 시작------------')
        f.write(time.strftime('[%x,%X] ') + '-------------디버깅 시작------------\n')
    else:
        print(time.strftime('[%x,%X] ') + '----------------시작----------------')
        f.write(time.strftime('[%x,%X] ') + '----------------시작----------------\n')

NShopping = Shop()
config = configparser.ConfigParser()
config.read('config.ini')
NShopping.url = config['NShopping']['URL'].replace('%%', '%')

while True:
    if repeat_cycle():
        firefox_options = webdriver.firefox.options.Options()
        if not debugMode:
            firefox_options.headless = True
        driver = webdriver.Firefox(options=firefox_options)
        f = open(log, 'a', -1, "utf-8")

        driver.get(NShopping.url)
        NShopping.html = driver.page_source
        NShopping.bs = BeautifulSoup(NShopping.html, 'html.parser')
        NShopping.title = NShopping.get_title()
        NShopping.time = time.gmtime(int(time.time()))
        NShopping.priceSelector = r'.lowestPrice_num__3AlQ-'
#        nvr_info = nvr_LocalTime + ' 「' + nvr_title_str + '」'

        # 가격 선택
        NShopping.price = NShopping.bs.select(NShopping.priceSelector)[0].text

        print(time.strftime('[%x,%X] ', NShopping.time) + '₩ ' + NShopping.price)
        f.write(time.strftime('[%x,%X] ', NShopping.time)+ '₩ ' + NShopping.price + '\n')

        f.close()
        driver.close()
        time.sleep(60)
