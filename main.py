# -*- encoding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import sys

hi_url = 'http://www.e-himart.co.kr/app/goods/goodsDetail?goodsNo=0003948195'
nvr_url = 'https://search.shopping.naver.com/detail/detail.nhn?nvMid=20985197108&query=%25EB%25A7%2581%25ED%2594%25BC%25ED%258A%25B8&NaPm=ct%3Dkbofpcqw%7Cci%3D15eb519cd6f277cf5994fb88bb92649e3bc9d4cb%7Ctr%3Dslsl%7Csn%3D95694%7Chk%3D3c9d80bd94fd8219167c801ab7cb962c46741e44'
txt = 'stock.log'
cycle = True

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

f = open(txt, 'a')
f.write(timenow()+' ----------------시작----------------\n')
print(timenow()+' ----------------시작----------------')
#파이어폭스  설정
try:
    firefox_options = webdriver.firefox.options.Options()
    firefox_options.headless = True
    driver = webdriver.Firefox(options=firefox_options)
    driver.implicitly_wait(3)
    f.write(timenow()+' --------geckodriver를 불러옴--------\n')
    print(timenow()+' --------geckodriver를 불러옴--------')
except:
    f.write(timenow() + ' geckdriver를 찾을 수 없음\n')
    sys.exit(timenow() + ' geckodriver를 찾을 수 없음')

f.close()
while True:
    time15 = int(time.strftime('%M', time.localtime(time.time())))
    if (time15 == 00 or time15 == 15 or time15 == 30 or time15 == 45):
        f = open(txt, 'a')
        driver.get(hi_url)  #파이어폭스에서 불러오기
        hi_LocalTime = timenow()
        hi_html = driver.page_source
        newtab()
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
        f.close()

        f = open(txt, 'a')
        driver.get(nvr_url)
        nvr_LocalTime = timenow()
        nvr_html = driver.page_source
        newtab()
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
        print(nvr_LocalTime + ' ' + hi_result + '; ' + nvr_result)
        f.write(nvr_LocalTime + ' ' + hi_result + '; ' + nvr_result + '\n')
        f.close()


        time.sleep(60)
