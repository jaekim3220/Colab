

# %%
# 모듈 준비
import requests
from bs4 import BeautifulSoup


# %%

# URL 파싱을 위해서는 카테고리, 페이지 번호에 따른 URL 변화를 확인
# 메인 url : https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=

# IT/과학 : 105, 경제 : 101, 사회 : 102, 생활/문화 : 103, 세계 : 104, 정치 : 100
CATEGORIES = [105, 101, 102, 103, 104, 100]

# 수집할 카테고리(IT/과학)
CATEGORY = 102

# 수집할 페이지 범위
PAGES = range(51, 100)  #51~100 페이지까지

# 네이버 뉴스 URL 형식
# https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100#&date=%2000:00:00&page=2  #정치
# https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101#&date=%2000:00:00&page=2  #경제
URL = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={category}#&date=%2000:00:00&page={page}"


# %%
# 접속 객체 생성
session = requests.Session()

# 접속객체에 부가정보(header) 삽입
session.headers.update({
    "Regerer" : "",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
})


# %%

# 수집한 뉴스기사의 수를 저장할 변수
counter = 1

# 수집한 뉴스 기사를 저장할 파일 이름
fileName = "./{myname}_naver_news_{category}_{counter}.txt"

# 주어진 카테고리에 대해 주어진 페이지 범위만큼 뉴스 정보 수집
for page in PAGES:  #PAGES = range(1, 10)
    # 접속할 url 생성
    targetUrl = URL.format(category=CATEGORY, page=page)    #{category}, {page}의 내용
    print("목표 URL :",targetUrl)

    # 생성한 접속객체를 활용해 뉴스 목록 페이지에 접속
    r = session.get(targetUrl)

    # 접속 실패시 에러코드 생성
    if r.status_code != 200: #정상 메세지 아닌 경우
        msg = "[%d Error] %s 에러 발생" % (r.status_code, r.reason)
        # 에러 강제 생성
        raise Exception(msg)
    
    # 응답 결과를 텍스트로 변환
    r.encoding = "euc-kr"   #utf-8아님
    soup = BeautifulSoup(r.text)
    # print(soup)

    # 뉴스 기사 제목을 위한 CSS 선택자(개발자 환경)
    # 1차는 헤드라인 뉴스, 
    selector = ".sh_item .sh_text .sh_text_headline, #section_body ul li dl dt a"

    # 뉴스기사 제목 추출
    headlines = soup.select(selector)
    # print(headlines)

    # 각 페이지별로 추출된 뉴스기사의 본문 URL
    for h in headlines:
        href = h.attrs["href"]
        # print("주소 :",href)

        # 기사 본문에 대한 세부 내용 수집
        if href:
            print("href :",href)
            bodyRes = session.get(href)
            # print("bodyRes :",bodyRes)

            # 접속에 실패한 경우 에러 발생
            if bodyRes.status_code != 200:
                msg = "[%d Error] %s 에러 발생" % (bodyRes.status_code, bodyRes.reason)
                raise Exception(msg)
            
            bodyRes.encoding = "utf-8"
            # print(bodyRes.text)
            bodySoup = BeautifulSoup(bodyRes.text)
            # print("\nbodySoup :", bodySoup)

            # 제목
            title = bodySoup.select("#title_area span")[0].text  #title_area span의 0번째 텍스트 추출
            print("뉴스 제목 :",title)

            # 본문
            content = bodySoup.select("#dic_area")[0]

            # 본문 요소에 포함된 사진과 같은 불필요한 항목 제거 
            # (태그, 클래스) 형식으로
            for target in content.find_all("span", {"class": "end_photo_org"}):    #사진 데이터
                target.extract()

            for target in content.find_all("strong", {"class": "media_end_summary"}):    #요약 데이터
                target.extract()
            
            for target in content.find_all("table", {"class": "nbd_table"}):
                target.extract()

            for target in content.find_all("div", {"class": "highlightBlock"}):
                target.extract()

            for target in content.find_all("div", {"style": "display:none;"}):
                target.extract()

            for target in content.find_all("br"):
                target.replace_with("\n")   #br 태그는 제거할 필요 없으므로 extract 대신 줄바꿈으로 변경

            contentBody = content.text.strip()

            with open(fileName.format(myname="kim", category=CATEGORY, counter=counter), "w", encoding="utf-8") as f:
                f.write(title)
                f.write("\n\n")
                f.write(contentBody)

            counter += 1

            print("%d news article crawled" % counter)

    # break   #break 넣었던 이유는 반복문을 한 번 수행할 때마다 결과를 확인하기 위함


# %%