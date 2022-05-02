from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests

import re

import time

marketInfoList = "https://finance.naver.com/research/market_info_list.naver" #시황정보
investList = "https://finance.naver.com/research/invest_list.naver" #투자정보
compList = "https://finance.naver.com/research/company_list.naver"  #종목분석
industryList = "https://finance.naver.com/research/industry_list.naver" #산업분석
economyList = "https://finance.naver.com/research/economy_list.naver"   #경제분석

# thinkpoolImg = "https://webchart.thinkpool.com/2021ReNew/Stock1Day/A{stockCode}.png" #씽크풀 차트 이미지 URL

def reportGetDriver(Headless, listClass):   #어떤 리포트 리스트 크롤링할지 여부 확인 후 맞는 드라이버 리턴
    # if(Headless):
    if(Headless):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("disable-gpu")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('land=ko_KR')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options=chrome_options)
        driver.implicitly_wait(1)
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("disable-gpu")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('land=ko_KR')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options=chrome_options)

    url = listClass
    driver.get(url)

    return driver

def getmarketInfoList(driver, targetUrl):  #시황정보 리스트페이지 목록 크롤링
    table = driver.find_element(By.CSS_SELECTOR, 'table.type_1')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    titleList = []
    linkList = []
    brokerList = []
    dateList = []

    for value in rows:
        row = value.find_elements(By.TAG_NAME, 'td')
        if len(row)==5: #구분선/공백 필터링
            if(targetUrl == row[0].find_element(By.TAG_NAME, 'a').get_attribute('href')): break
            else:
                titleList.append(row[0].text)
                linkList.append(row[0].find_element(By.TAG_NAME, 'a').get_attribute('href'))
                brokerList.append(row[1].text)
                dateList.append(row[3].text)
        else:
             continue

    # print(pageText)
    # titleList.reverse()
    linkList.reverse()
    brokerList.reverse()
    # dateList.reverse()
    try:
        targetUrl = linkList[-1]
    except:
        print("There are no new reports here")
        titleList = []
        linkList = []
        # brokerList = []
        # dateList = []

    return linkList, brokerList, targetUrl

def getmarketInfoPage(url):    #리포트 개별 페이지 본문 크롤링
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    pageText = ""

    title = soup.select_one('th.view_sbj').get_text().strip().split("\n")[0]

    pageTxt = soup.select('#contentarea_left > div.box_type_m.box_type_m3 > table td.view_cnt > div:nth-child(1)')
    for p in pageTxt:
        a = str(p)
        a=re.sub('<.+?>', '\n', a, 0).strip()+"\n"
        pageText+=a

    return title, pageText

def getstockList(driver, targetUrl):    #네이버 리서치 종목분석 리포트 게시물 리스트 정보 크롤링
    table = driver.find_element(By.CSS_SELECTOR, 'table.type_1')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    stCode = []
    stName = []
    linkList = []
    brokerList = []

    for value in rows:
        row = value.find_elements(By.TAG_NAME, 'td')
        if len(row)==6: #구분선/공백 필터링
            if(targetUrl == row[1].find_element(By.TAG_NAME, 'a').get_attribute('href')): break
            else:
                stCode.append(row[0].find_element(By.TAG_NAME, 'a').get_attribute('href').split('?code=')[-1])
                stName.append(row[0].text)
                linkList.append(row[1].find_element(By.TAG_NAME, 'a').get_attribute('href'))
                brokerList.append(row[2].text)
        else:
             continue

    stCode.reverse()
    stName.reverse()
    linkList.reverse()
    brokerList.reverse()
    try:
        targetUrl = linkList[-1]
    except:
        # print("There are no new reports here")
        stCode = []
        stName = []
        linkList = []
        brokerList = []

    return stCode, stName, linkList, brokerList, targetUrl
    
def getStockInfoPage(url):  #상장분석 리포트 개별 페이지 본문내용 크롤링
    # url = "https://finance.naver.com/research/company_read.naver?nid=59037&page=1"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    pageText = ""

    title = soup.select_one('th.view_sbj').get_text().strip().split("\n")[1].strip()

    targetPrice = soup.select_one('div.view_info_1 > em.money').get_text().strip()
    coment = soup.select_one('div.view_info_1 > em.coment').get_text().strip()

    pageTxt = soup.select('#contentarea_left > div.box_type_m.box_type_m3 > table td.view_cnt > div > p')
    for p in pageTxt:
        a = str(p)
        a=re.sub('<.+?>', '\n', a, 0).strip()+"\n"
        pageText+=a
    
    pageText = re.sub('[.] ', '.\n\n', pageText, 0).strip()

    
    quotation = f'목표가 : {targetPrice}\n투자의견 : {coment}'

    # print(pageText)

    return title, quotation,  pageText

def getFnGuide(code):   #fn가이드 business summary 크롤링
    pageText = ""

    try:
        res = requests.get("https://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A"+code+"&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701")
        # headers={'User-Agent':'Mozilla/5.0'}
        soup = BeautifulSoup(res.text, "html.parser")
        summaryHeader = soup.select_one("#bizSummaryHeader").text
        summaryContent = soup.select("ul#bizSummaryContent>li")

    except:
        summaryHeader = ""
        summaryContent = ""

    for p in summaryContent:
        a = str(p)
        a=re.sub('<.+?>', '\n', a, 0).strip()+"\n\n\n"
        pageText+=a

    pageText = re.sub('[.]\xa0', '.\n\n', pageText)

    return summaryHeader, pageText

def getLogoUrl(code):       #상장온라인 종목 로고 크롤링
    # code = "005930"
    url = f'https://media.kisline.com/highlight/mainHighlight.nice?paper_stock={code}&nav=1'
    header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    res = requests.get(url, headers=header)
    soup = BeautifulSoup(res.text, "html.parser")

    url = soup.select_one("table.logo > tr > td").find("img")["src"]
    # print(url)

    return url

def getniceCompSearch(code):    #나이스 종목 개요/현황 크롤링
    url = f"https://comp.kisline.com/hi/HI0100M010GE.nice?stockcd={code}&nav=1"

    title = []
    contents = []

    print("\n\n\n※나이스 종목 개요/현황 크롤링※")
    niceCompDriver = reportGetDriver(True, url)

    element = niceCompDriver.find_element(By.XPATH, '//*[@id="contents"]/section[5]/div/table/thead/tr/th[1]')
    niceCompDriver.execute_script("arguments[0].scrollIntoView(true);", element)

    title.append(element.text)

    element = niceCompDriver.find_element(By.XPATH, '//*[@id="contents"]/section[5]/div/table/tbody/tr/td[1]')
    text = element.text.replace("\n", "\n\n")
    text += "\n"

    contents.append(text)

    element = niceCompDriver.find_element(By.XPATH, '//*[@id="contents"]/section[5]/div/table/thead/tr/th[2]')

    title.append(element.text)

    element = niceCompDriver.find_element(By.XPATH, '//*[@id="contents"]/section[5]/div/table/tbody/tr/td[2]')
    # print(element.text)#현황 내용
    text = element.text.replace("\n", "\n\n")
    text += "\n"

    contents.append(text)

    niceCompDriver.quit()
    # print(contents)

    return title, contents

def getSupDem(code): #씽크풀 수급 특이사항 크롤링(보류)
    url = f"https://www.thinkpool.com/item/{code}/trend/trading"

    print("\n\n\n※수급 특이사항 크롤링※")
    supDemDriver = reportGetDriver(True, url)
    element = supDemDriver.find_elements(By.CLASS_NAME, "nblboder")

    supDem = ""

    for i in range(len(element)):
        element1 = supDemDriver.find_element(By.XPATH, f'//*[@id="content"]/div/div/div[2]/div[3]/table/tbody/tr[{i+1}]/td[7]/span')#내용
        element2 = supDemDriver.find_element(By.XPATH, f'//*[@id="content"]/div/div/div[2]/div[3]/table/tbody/tr[{i+1}]/td[1]/span')#날짜
        if not element1.text:
            continue 
        supDem += f"\xa0· {element2.text} - {element1.text}\n"

    supDem.strip()
    supDemDriver.quit()

    return supDem

def getInfoStock(code, isId, isPw):

    if not isId:
        themeList = []
        content = []
        print("infoStock Crawling Passed")
        return themeList, content

    loginUrl = "https://www.infostock.co.kr/login.asp"
    stockUrl = f"https://www.infostock.co.kr/3d.asp?Code={code}"

    print("\n\n\n※인포스탁 관련테마 분석 내용 크롤링※")
    driver = reportGetDriver(True, loginUrl)

    driver.find_element(By.ID, 'id').send_keys(isId)
    driver.find_element(By.ID, 'pw').send_keys(isPw)
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="button"]').click()
    time.sleep(1)

    driver.get(stockUrl)
    
    element = driver.find_elements(By.CSS_SELECTOR, 'table.bb_table > tbody > tr:nth-child(11)')

    relateTheme = ""

    for i in element:
        text = str(i.text)
        text = text.replace("[관련종목]", "[관련종목]\n")
        text = text.replace("상세보기>", "\n")
        relateTheme += f"{text.strip()}"
    
    data = str(relateTheme).split("...")

    themeList=[]
    content=[] 
    for i in data:
        if len(i)==0:
            continue
        # print(i)

        theme = re.compile('\[.*\]').search(i)
        themeList.append(theme.group())
        content.append(re.split('\[.*\]', i, 1)[1])

    # for idx in range(len(themeList)):
    #     print(f'{themeList[idx]}\n')
    #     print(f'{content[idx]}\n\n')

    driver.quit()
    return themeList, content

def getNewsDisclosure(code):
    url = f'https://finance.naver.com/item/news.naver?code={code}'
    header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    res = requests.get(url, headers=header)
    soup = BeautifulSoup(res.text, "html.parser")

    # url = soup.select_one("table.logo > tr > td").find("img")["src"]
    newsList = soup.select("table.type5 > tbody > tr > td.title")
    print(newsList)


# if __name__ == "__main__" :
#     code = "001680"
#     getNewsDisclosure(code)