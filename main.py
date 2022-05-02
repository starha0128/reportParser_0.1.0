import report_parser
from post import Naver
import time
from datetime import datetime

compList = "https://finance.naver.com/research/company_list.naver"  #종목분석

Headless = False

if __name__ == '__main__':
    id = input("1. 포스팅할 네이버 계정\n - ID : ")
    pw = input(" - PW : ")

    isId = input("\n2. 인포스탁 정회원 계정\n※없을 경우 자동포스팅 시 관련테마 분석이 포함되지 않습니다.※\n계정이 없을 경우 ENTER↵로 넘겨주세요.\n - ID : ")
    if isId:
        isPw = input(" - PW : ")
    else:
        isPw = None

    cafeWriteUrl = input("\n3. 포스팅할 카페 게시판 글쓰기 폼 주소\n포스팅 희망하는 게시판 이동 ▶ 글쓰기 버튼 클릭 ▶ 주소 복사\n※게시판별 글쓰기 주소가 다릅니다※\n입력 : ")

    naver = Naver(id, pw)
    if naver.login():
        comptargetUrl = ""
        compDriver = report_parser.reportGetDriver(True, compList)
        while 1:
            if naver.is_logged_in():    #네이버 계정 로그인 여부 확인
                try:
                    compDriver.refresh()    #네이버리서치 종목분석 게시판 리스트 새로고침

                    compCode, compName, compLink, compBroker, comptargetUrl = report_parser.getstockList(compDriver, comptargetUrl)

                    if compLink:
                        title, quotation, pageText1 = report_parser.getStockInfoPage(compLink[-1]) #네이버 리서치 종목분석 리포트 개별 페이지 제목/본문/투자의견 크롤링
                        title = f'{compName[-1]}[{compCode[-1]}] 종목분석 : {title}' #포스팅 제목정보 f-string
                        imgUrl = f'https://webchart.thinkpool.com/2021ReNew/Stock1Day/A{compCode[-1]}.png'  #씽크풀 종목차트 이미지 주소 f-string
                        sumH, pageText2 = report_parser.getFnGuide(compCode[-1]) #FN가이드 Business Summary 크롤링
                        logoUrl = report_parser.getLogoUrl(compCode[-1]) #상장온라인 로고정보 크롤링
                        niceTitle, niceText = report_parser.getniceCompSearch(compCode[-1])
                        # supDem = report_parser.getSupDem(compCode[-1]) #보류
                        
                        themeList, themeCont = report_parser.getInfoStock(compCode[-1], isId, isPw) #인포스탁 관련테마 분석 크롤링

                        res = naver.compPost(cafeWriteUrl, title, logoUrl, imgUrl, compLink[-1], quotation, pageText1, sumH, pageText2, niceTitle, niceText, themeList, themeCont)  #포스팅
                        date = datetime.now()

                        print(f'\n\n[{date}]\n - "{title}" 포스팅 {res}')   #포스팅 성공여부 프린트

                        time.sleep(5)
                    else:
                        time.sleep(30)
                        continue

                except Exception as e:
                    print(e)
                    print("※componyList posting error!!※")
            else:
                naver.login()
