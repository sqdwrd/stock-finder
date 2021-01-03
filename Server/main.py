# -*- encoding: utf-8 -*-
import configparser
import re
import sys
import time
import json
import os
import send
from selenium import webdriver

cycle = True
if os.path.dirname(__file__):
    configDir = os.path.dirname(__file__) + '/config.ini'
    jsonDir = os.path.dirname(__file__) + '/stock.json'
    logDir = os.path.dirname(__file__) + '/stock.log'
else:
    configDir = 'config.ini'
    jsonDir = 'stock.json'
    logDir = 'stock.log'


class NoConfigFile(Exception):
    def __init__(self):
        super().__init__('Can\'t read config file. Try with --config parameter!')


def get_argv(num):
    try:
        return sys.argv[num]
    except IndexError:
        return None


def int_sieve(raw_value):
    raw_value = list(raw_value)
    value = []
    for j in raw_value:
        try:
            j = int(j)
            value.append(str(j))
        except ValueError or TypeError:
            pass
    return ''.join(value)


def repeat_cycle():
    minute = int(time.strftime('%M'))
    if debugMode:
        return True
    elif minute == 00:
        return True


def configure():
    config = configparser.ConfigParser()
    try:
        open('config.ini')
        print('Overwriting config.ini...')
    except FileNotFoundError:
        pass
    shops = ['1']  # 1 : 네이버쇼핑
    shop = input('choose shop [1 = Naver Shopping]\n>>')
    while shop not in shops:
        shop = input('\033[31m' + 'Shop incorrect!' + '\033[0m' + '\nchoose shop [1 = Naver Shopping]\n>>')
    if shop == '1':
        regex = re.compile('^https?://search.shopping.naver.com/catalog/')
        url = input("input URL\n>>")
        while regex.match(url) is None:
            url = input('\033[31m' + 'URL incorrect!' + '\033[0m' + '\ninput URL\n>>')
        url = url.replace('%', '%%')
        config['NShopping'] = {}
        config['NShopping']['URL'] = url
    # NETWORK
    port = None
    port_regex = re.compile(r'^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])|(^$)$')
    port = input('input port [Default = 51208]\n>>')
    while not port_regex.match(port):
        port = input('\033[31m' + 'PORT incorrect!' + '\033[0m' + '\ninput port\n>>')
    if port == '':
        port = '51208'
        print('port set to tcp:51208')
    else:
        print('port set to tcp:' + port)
    config['Network'] = {}
    config['Network']['port'] = port

    with open(configDir, 'w') as configFile:
        config.write(configFile)
    with open(jsonDir, 'w', encoding='utf-8') as json_File:
        json_data = dict()
        json_data['NaverShopping'] = list()
        json_data['NaverShopping'].append({'url': url})
        json_data['NaverShopping'].append({'data': list()})
        json_File.write(json.dumps(json_data))


class Shop:
    url = None
    time = None
    title = None
    Price = None
    priceSelector = None
    includeShipChkBoxSelector = None
    shipPriceSelector = None
    shipPrice = None
    browser = None
    browser_options = None

    def config_browser(self):
        self.browser_options = webdriver.firefox.options.Options()
        if not debugMode:
            self.browser_options.headless = True
        self.browser = webdriver.Firefox(options=self.browser_options)

    def get_title(self):
        return self.browser.find_element_by_css_selector('head > title').text


if '--debug' in sys.argv:
    debugMode = True
else:
    debugMode = False
if '--config' in sys.argv:
    configMode = True
else:
    configMode = False
if '--send' in sys.argv:
    sendMode = True
else:
    sendMode = False

if configMode:
    configure()

with open(logDir, 'a', -1, 'utf-8') as f:
    if debugMode:
        print(time.strftime('[%y/%m/%d,%X] ') + '-------------디버깅 시작------------')
        f.write(time.strftime('[%y/%m/%d,%X] ') + '-------------디버깅 시작------------\n')
    else:
        print(time.strftime('[%y/%m/%d,%X] ') + '----------------시작----------------')
        f.write(time.strftime('[%y/%m/%d,%X] ') + '----------------시작----------------\n')

NShopping = Shop()
try:
    config = configparser.ConfigParser()
    config.read(configDir)
    NShopping.url = config['NShopping']['URL'].replace('%%', '%')
    port = int(config['Network']['port'])
except KeyError:
    raise NoConfigFile


while not sendMode:
    if repeat_cycle():
        f = open(logDir, 'a', -1, "utf-8")
        NShopping.config_browser()
        NShopping.browser.get(NShopping.url)
        NShopping.priceSelector = r'.lowestPrice_num__3AlQ-'
        NShopping.includeShipChkBoxSelector = r'.filter_chk_box__23BvI'
        NShopping.shipPriceSelector = r'.lowestPrice_delivery_price__3f-2l'
        NShopping.browser.find_element_by_css_selector(NShopping.includeShipChkBoxSelector).click()
        NShopping.title = NShopping.browser.find_element_by_css_selector('head > title').text
        NShopping.time = int(time.time())
        # 가격
        NShopping.rawPrice = NShopping.browser.find_element_by_css_selector(NShopping.priceSelector).text
        NShopping.price = int_sieve(NShopping.rawPrice)
        # 배송료
        try:
            NShopping.rawShipPrice = NShopping.browser.find_element_by_css_selector(NShopping.shipPriceSelector + ' > em').text
            NShopping.shipPrice = int_sieve(NShopping.rawShipPrice)
        except:
            if '무료' in NShopping.browser.find_element_by_css_selector(NShopping.shipPriceSelector).text:
                NShopping.shipPrice = 0

        NShopping.finalPrice = int(NShopping.price) + int(NShopping.shipPrice)
        print(time.strftime('[%y/%m/%d,%X] ', time.localtime(NShopping.time)) + NShopping.title + '의 내용: '
              + '₩ ' + str(NShopping.finalPrice))
        f.write(time.strftime('[%y/%m/%d,%X] ', time.localtime(NShopping.time)) + NShopping.title + '의 내용: '
                + '₩ ' + str(NShopping.finalPrice) + '\n')

        f.close()
        NShopping.browser.close()

        with open(jsonDir, encoding='utf-8') as jsonFile:
            jsonData = json.load(jsonFile)
            jsonData['NaverShopping'][1]['data'].append({NShopping.time: NShopping.finalPrice})
        with open(jsonDir, 'w', encoding='utf-8') as jsonFile:
            jsonFile.write(json.dumps(jsonData))

        print('대기 중')  # json을 클라이언트에 보내기
        send.connect_and_send('BoF', port)
        with open(jsonDir, encoding='utf-8') as jsonFile:
            print(jsonFile.read())
            print(type(jsonFile.read()))
            send.connect_and_send(jsonFile.read(), port)
        send.connect_and_send('EoF', port)
        print('보내짐')
        time.sleep(60)

if sendMode:
    send.connect_and_send('BoF', port)
    with open(jsonDir, encoding='utf-8') as jsonFile:
        print(jsonFile.read())
        print(type(jsonFile.read()))
        send.connect_and_send(jsonFile.read(), port)
    send.connect_and_send('EoF', port)
