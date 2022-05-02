from contextlib import nullcontext
from selenium import webdriver
from selenium.webdriver.remote.command import Command
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
import pyperclip

options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
    'profile.default_content_setting_values.notifications': 1,
    'profile.default_content_setting_values.clipboard': 1
})
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
# options.add_argument('--blink-settings=imagesEnabled=false') #브라우저에서 이미지 로딩을 하지 않습니다.
options.add_argument('--mute-audio') #브라우저에 음소거 옵션을 적용합니다.
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36')

class MyChrome(webdriver.Chrome):
    def quit(self):
      print(self)
      webdriver.Chrome.quit(self)
      self.session_id = None

class Naver:
    def __init__(self, id, pw) -> None:
        self.id=id
        self.pw=pw
        self.driver = MyChrome(ChromeDriverManager().install(), options=options)

    def login(self):
        self.driver.get("https://nid.naver.com/nidlogin.login")
        self.driver.execute_script("document.getElementsByName('id')[0].value=\'" + self.id + "\'")
        self.driver.execute_script("document.getElementsByName('pw')[0].value=\'" + self.pw + "\'")
        time.sleep(1)
        # self.driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
        self.driver.find_element(By.CLASS_NAME, 'btn_login').click()
        # self.driver.find_element_by_class_name('btn_login').click()
        time.sleep(1)
        return self.is_logged_in()

    def is_logged_in(self):
        try:
            self.driver.get('https://shopping.naver.com/my/p/home.nhn') #로그인 필요한 메뉴로 이동
            
            time.sleep(1)
            current_url = self.driver.current_url
            if current_url.split('?')[0] == 'https://nid.naver.com/nidlogin.login':
                print('===========login error=============')
                return False
            return True
        except:
            return False

    def cafeLinkPost(self, link):
        element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'se-oglink-toolbar-button.se-document-toolbar-basic-button.se-text-icon-toolbar-button')))    #링크
        time.sleep(0.5)
        element.click()

        element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//input[@class="se-popup-oglink-input"]')))   #링크 주소 붙여넣기
        time.sleep(0.5)
        element.send_keys(link)

        element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'se-popup-oglink-button')))    #링크 붙여넣고 검색버튼 활성화 여부 체크
        time.sleep(0.5)
        element.click()

        element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'se-popup-button.se-popup-button-confirm')))      #링크 활성화 시 "확인"버튼 활성화 여부 체크
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", element)

    def setQuot(self, quotSentence, quotSource):
        self.driver.execute_script("window.scrollTo(0,0)")

        element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'se-document-toolbar-select-option-button.se-text-icon-toolbar-select-option-button')))
        time.sleep(0.5)
        element.click()

        element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'se-toolbar-option-icon-button.se-toolbar-option-insert-quotation-quotation_line-button')))
        time.sleep(0.5)
        element.click() #좌측 바 인용문 선택

        pyperclip.copy(quotSentence)
        time.sleep(0.5)
        pyautogui.hotkey("ctrl","v")
        time.sleep(0.5)
        pyautogui.hotkey("down")
        time.sleep(0.5)

        if str(type(quotSource))=="<class 'str'>":
            pyperclip.copy(quotSource)
            time.sleep(0.5)
            pyautogui.hotkey("ctrl","v")
            time.sleep(0.5)

        pyautogui.hotkey("down")
        time.sleep(0.5)
        pyautogui.hotkey("enter")   #인용문 양식 탈출

    def postNiceInfo(self, niceTitle, niceText):

        for idx in range(len(niceTitle)):
            self.setQuot(niceTitle[idx], 0) #두번째 인자 str형만 아니면 출처영역 입력 안함.

            pyperclip.copy(niceText[idx])
            time.sleep(0.5)
            pyautogui.hotkey("ctrl","v")
            time.sleep(0.5)
            pyautogui.hotkey("enter")
            time.sleep(0.5)
            pyautogui.hotkey("enter")
            time.sleep(0.5)
            pyautogui.hotkey("enter")
            time.sleep(0.5)



    def compPost(self, editor_link, title, logoUrl, imgUrl, url, quotation, text1, sumH, text2, niceTitle, niceText, themeList, themeCont):
        self.driver.get(editor_link)    #카페 글쓰기 폼 이동

        time.sleep(0.5)

        win = pyautogui.getWindowsWithTitle('카페 글쓰기')[0]   #카페 글쓰기 창 포커스(활성화)

        if win.isActive == False:
            win.activate()
        
        try:
            element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'se-image-toolbar-button.se-document-toolbar-basic-button.se-text-icon-toolbar-button')))

            if "null" not in logoUrl:
                time.sleep(0.5)
                element.click()

                pyperclip.copy(logoUrl)             #로고 URL 삽입
                time.sleep(2)
                pyautogui.hotkey("ctrl","v")
                time.sleep(1)
                pyautogui.hotkey("enter")

                time.sleep(10)

            self.driver.execute_script("window.scrollTo(0,0)")

            self.setQuot(quotation, 0) #목표가/투자의견 삽입

            pyperclip.copy(text1)               #네이버 리서치 종목 리포트 개별 페이지 본문 삽입(복붙)
            pyautogui.hotkey("ctrl","v")
            time.sleep(0.5)

            self.cafeLinkPost(imgUrl)     #씽크풀 종목 차트 이미지 삽입

            self.setQuot(sumH, 0)

            pyperclip.copy(text2)               #FN가이드 크롤링 business summary 삽입(복붙)
            pyautogui.hotkey("ctrl","v")
            time.sleep(0.5)

            self.driver.execute_script("window.scrollTo(0,0)")  #스크롤 상단 이동

            time.sleep(0.5)

            self.cafeLinkPost(url)    #리포트 링크 삽입

            time.sleep(0.5)

            self.postNiceInfo(niceTitle, niceText)

            time.sleep(0.5)
            time.sleep(0.5)

            self.driver.execute_script("window.scrollTo(0,0)")

            element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'se-document-toolbar-select-option-button.se-text-icon-toolbar-select-option-button')))
            time.sleep(0.5)
            element.click()

            element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'se-toolbar-option-icon-button.se-toolbar-option-insert-quotation-default-button')))
            time.sleep(0.5)
            element.click() #좌측 바 인용문 선택

            pyperclip.copy("관련테마 분석")
            time.sleep(0.5)
            pyautogui.hotkey("ctrl","v")
            time.sleep(0.5)
            pyautogui.hotkey("down")
            time.sleep(0.5)
            pyautogui.hotkey("down")
            time.sleep(0.5)
            pyautogui.hotkey("enter")

            self.postNiceInfo(themeList, themeCont)
            time.sleep(0.5)

            self.driver.find_element_by_class_name('textarea_input').send_keys(title) #제목 입력
            time.sleep(1)

            element = self.driver.find_element_by_xpath('//span[contains(text(),"등록")]') #등록 버튼 클릭
            self.driver.execute_script("arguments[0].click();", element)

            time.sleep(1)

            try:
                popup = Alert(self.driver)
                if "금칙어" in popup.text:
                    popup.accept()
                    return "스팸 감지"
                elif "등록 제한" in popup.text:
                    popup.accept()
                    return "일일 등록 제한"
            except:
                return "성공"

        except Exception as e:
            print(e)
            return "실패"