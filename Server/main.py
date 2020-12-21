# -*- encoding: utf-8 -*-
import configparser
import re
import sys
import time
import json
from selenium import webdriver

log = 'stock.log'
cycle = True


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
    shops = ['1']
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
        with open('config.ini', 'w') as configFile:
            config.write(configFile)
        with open('stock.json', 'w', encoding='utf-8') as json_File:
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

if configMode:
    configure()

with open(log, 'a', -1, 'utf-8') as f:
    if debugMode:
        print(time.strftime('[%y/%m/%d,%X] ') + '-------------디버깅 시작------------')
        f.write(time.strftime('[%y/%m/%d,%X] ') + '-------------디버깅 시작------------\n')
    else:
        print(time.strftime('[%y/%m/%d,%X] ') + '----------------시작----------------')
        f.write(time.strftime('[%y/%m/%d,%X] ') + '----------------시작----------------\n')

NShopping = Shop()
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    NShopping.url = config['NShopping']['URL'].replace('%%', '%')
except KeyError:
    raise NoConfigFile


while True:
    if repeat_cycle():
        f = open(log, 'a', -1, "utf-8")
        NShopping.config_browser()
        NShopping.browser.get(NShopping.url)
        NShopping.priceSelector = r'.lowestPrice_num__3AlQ-'
        NShopping.includeShipChkBoxSelector = r'.filter_chk_box__23BvI'
        NShopping.shipPriceSelector = r'.lowestPrice_delivery_price__3f-2l > em'
        NShopping.browser.find_element_by_css_selector(NShopping.includeShipChkBoxSelector).click()
        NShopping.title = NShopping.browser.find_element_by_css_selector('head > title').text
        NShopping.time = int(time.time())
        # 가격
        NShopping.rawPrice = NShopping.browser.find_element_by_css_selector(NShopping.priceSelector).text
        NShopping.price = int_sieve(NShopping.rawPrice)
        # 배송료
        NShopping.rawShipPrice = NShopping.browser.find_element_by_css_selector(NShopping.shipPriceSelector).text
        NShopping.shipPrice = int_sieve(NShopping.rawShipPrice)

        NShopping.finalPrice = int(NShopping.price) + int(NShopping.shipPrice)
        print(time.strftime('[%y/%m/%d,%X] ', time.localtime(NShopping.time)) + NShopping.title + '의 내용: '
              + '₩ ' + str(NShopping.finalPrice))
        f.write(time.strftime('[%y/%m/%d,%X] ', time.localtime(NShopping.time)) + NShopping.title + '의 내용: '
                + '₩ ' + str(NShopping.finalPrice) + '\n')

        f.close()
        NShopping.browser.close()

        with open('stock.json', encoding='utf-8') as jsonFile:
            jsonData = json.load(jsonFile)
            jsonData['NaverShopping'][1]['data'].append({NShopping.time: NShopping.finalPrice})
        with open('stock.json', 'w', encoding='utf-8') as jsonFile:
            jsonFile.write(json.dumps(jsonData))
        time.sleep(60)
