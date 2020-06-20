# -*- encoding: utf-8 -*-


from selenium import webdriver
from bs4 import BeautifulSoup
import time
import sys

url = 'http://www.e-himart.co.kr/app/goods/goodsDetail?goodsNo=0003948195'
txt = 'stock.log'
cycle = True

#파이어폭스  설정
firefox_options = webdriver.firefox.options.Options()
firefox_options.headless = True
driver = webdriver.Firefox(options=firefox_options)
driver.implicitly_wait(3)


f = open(txt, 'a')  #결과값 저장
while True:
    if (cycle == True) and int(time.strftime('%M', time.localtime(time.time()))) == 00 or 15 or 30 or 45:
        LocalTime = '['+time.strftime('%y-%m-%d %H:%M:%S', time.localtime(time.time()))+']'  #불러온 시간 저장
        driver.get(url)  #파이어폭스에서 불러오기
        time.sleep(3)
        html = driver.page_source

        #웹페이지 제목 선택
        soup = BeautifulSoup(html, "html.parser")
        title = soup.select('head > title')
        try:
                title_str = str(title[0]).split('<title>')
                title_str = str(title_str[1]).split('</title>')
                title_str = str(title_str[0])
        except:
                f.write(Localtime + ' 「' + url + '」' + '의 결과: 오류: <title> 헤더를 찾을 수 없음')
                sys.exit(Localtime + ' 「' + url + '」' + '오류: <title> 헤더를 찾을 수 없음')


        info = LocalTime + ' 「' + title_str + '」' + '의 결과: '


        #재고값 선택
        stock = soup.select("#content > div.detailArea > div.prdSec > div.rightSec > div")
        try:
                stock_str = str(stock[0])
        except:
                f.write(info + '재고값 개체를 찾을 수 없음')
                sys.exit(info + '오류: 재고값 개체를 찾을 수 없음')  #오류 종료



        #결과 분류
        if '재고가 일시 품절된 상품입니다.' in stock_str:
                print(info+'품절')
                f.write(info +'품절\n')
        elif '바로구매' in stock_str:
                print(info +'보유')
                f.write(info +'보유\n')
        else:
                f.write(info +'오류: 분류할 수 없음\n')
                sys.exit(info +'오류: 분류할 수 없음')
        f.close()
        f = open(txt, 'a')
        time.wait(60)
        cycle = False
        
