# -*- encoding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import sys
import subprocess

hi_url = 'http://www.e-himart.co.kr/app/goods/goodsDetail?goodsNo=0003948195'
nvr_url = 'https://search.shopping.naver.com/detail/detail.nhn?nvMid=20985197108&query=%25EB%25A7%2581%25ED%2594%25BC%25ED%258A%25B8&NaPm=ct%3Dkbofpcqw%7Cci%3D15eb519cd6f277cf5994fb88bb92649e3bc9d4cb%7Ctr%3Dslsl%7Csn%3D95694%7Chk%3D3c9d80bd94fd8219167c801ab7cb962c46741e44'
txt = 'stock.log'
cycle = True


def getargv(num):
    try:
        return sys.argv[num]
    except IndexError:
        return None

def newtab():
    driver.execute_script('window.open(\"about:blank\", \"_blank\")')
    driver.switch_to.window(driver.window_handles[0])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def title(bs, url):
    title = bs.select('head > title')
    try:
        title_str = str(title[0]).split('<title>')
        title_str = str(title_str[1]).split('</title>')
        title_str = str(title_str[0])
        return title_str
    except:
        f.write(Localtime + ' 「' + url + '」' + '의 결과: 오류: <title> 헤더를 찾을 수 없음\n')
        sys.exit(Localtime + ' 「' + url + '」' + '의 결과: 오류: <title> 헤더를 찾을 수 없음')

def timenow():
    return time.strftime('[%y-%m-%d %H:%M:%S]', time.localtime(time.time()))

def cycle15():
    min = int(time.strftime('%M', time.localtime(time.time())))
    if isdebug == True:
        return True
    elif min == 00 or min == 15 or min == 30 or min == 45:
        return True

if getargv(1) == '--debug':
    isdebug = True
else:
    isdebug = False

f = open(txt, 'a')
if isdebug == True:
    print(timenow() + ' -------------디버깅 시작------------')
    f.write(timenow() + ' -------------디버깅 시작------------\n')
else:
    print(timenow() + ' ----------------시작----------------')
    f.write(timenow() + ' ----------------시작----------------\n')

f.close()
while True:
    if cycle15():
        firefox_options = webdriver.firefox.options.Options()
        if isdebug == False:
            firefox_options.headless = True
        driver = webdriver.Firefox(options=firefox_options)
        f = open(txt, 'a')

        #하이마트
        driver.get(hi_url)
        hi_LocalTime = timenow()
        hi_LocalTime2 = time.strftime('%y-%m-%d_%H:%M:%S', time.localtime(time.time()))
        hi_html = driver.page_source
        hi_bs = BeautifulSoup(hi_html, 'html.parser')
        hi_title_str = title(hi_bs, hi_url)
        hi_info = hi_LocalTime + ' 「' + hi_title_str + '」'

        #재고값 선택
        hi_stock = hi_bs.select("#content > div.detailArea > div.prdSec > div.rightSec > div")
        try:
                hi_stock_str = str(hi_stock[0])
        except:
                f.write(hi_info + '오류: 재고값 개체를 찾을 수 없음\n')
                sys.exit(hi_info + '오류: 재고값 개체를 찾을 수 없음')  #오류 종료


        #결과 분류
        if '재고가 일시 품절된 상품입니다.' in hi_stock_str:
                hi_result = '품절'
        elif '바로구매' in hi_stock_str:
                hi_result = '보유'
        else:
                f.write(hi_info +'오류: 분류할 수 없음\n')
                sys.exit(hi_info +'오류: 분류할 수 없음')
    #네이버페이
        f = open(txt, 'a')
        driver.get(nvr_url)
        nvr_LocalTime = timenow()
        nvr_LocalTime2 = time.strftime('%y-%m-%d_%H:%M:%S', time.localtime(time.time()))
        nvr_html = driver.page_source
        nvr_bs = BeautifulSoup(nvr_html, 'html.parser')
        nvr_title_str = title(nvr_bs, nvr_url)
        nvr_info = nvr_LocalTime + ' 「' + nvr_title_str + '」'

        #가격 선택
        nvr_price = nvr_bs.select('em.num')
        try:
            nvr_price = str(nvr_price).split("<em class=\"num\">")
            nvr_price = str(nvr_price[1]).split("</em>")
            nvr_price = str(nvr_price[0])
        except:
            f.write(nvr_info + "오류: 가격 개체를 찾을 수 없음\n")
            sys.exit(nvr_info + "오류: 가격 개체를 찾을 수 없음")
        nvr_result = '₩' + nvr_price

        if isdebug == True:
            print(hi_info + ' ' + hi_result)
            f.write(hi_info + ' ' + hi_result + '\n')
            print(nvr_info + ' ' + nvr_result)
            f.write(nvr_info + ' ' + nvr_result + '\n')
        else:
            print(nvr_LocalTime + ' ' + hi_result + '; ' + nvr_result)
            f.write(nvr_LocalTime + ' ' + hi_result + '; ' + nvr_result + '\n')

        if hi_result == '보유':
            try:
                htmlf = open('html/' + hi_LocalTime2 + ' 하이마트.html', 'w')
            except FileNotFoundError:
                subprocess.run(['mkdir', 'html'])
                htmlf = open('html/' + hi_LocalTime2 + ' 하이마트.html', 'w')
            htmlf.write(hi_html)
            htmlf.close()

        nvr_intprice = "0"
        for i in nvr_price:
            try:
                int(i)
                nvr_intprice = nvr_intprice + i
            except:
                pass
        nvr_intprice = int(nvr_intprice)
        if nvr_intprice <= 90000:
            try:
                htmlf = open('html/' + nvr_LocalTime2 + ' 네이버.html', 'w')
            except FileNotFoundError:
                subprocess.run(['mkdir', 'html'])
                htmlf = open('html/' + nvr_LocalTime2 + ' 네이버.html', 'w')
            htmlf.write(nvr_html)
            htmlf.close()

        f.close()
        driver.close()
        time.sleep(60)
