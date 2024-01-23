import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service


# Chrome WebDriver 경로 설정
webdriver_path = '/Users/choeseohyeon/.cache/selenium/chromedriver/mac-arm64/120.0.6099.109/chromedriver'
s = Service(webdriver_path)

# 웹 드라이버 초기화
driver = webdriver.Chrome(service=s)

# 쿠키 팝업을 처리하는 함수
def handle_cookie_popup():
    try:
        # '모두 동의' 버튼이 나타날 때까지 최대 10초간 대기
        all_agree_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "모두 동의")]'))
        )
        # '모두 동의' 버튼 클릭
        all_agree_button.click()
        print("쿠키 설정이 처리되었습니다.")
    except TimeoutException:
        # 쿠키 팝업이 표시되지 않는 경우
        print("쿠키 팝업이 없거나 이미 처리되었습니다.")
    except (ElementClickInterceptedException, NoSuchElementException) as e:
        # 버튼 클릭이 가로막힌 경우 또는 버튼을 찾을 수 없는 경우
        print("쿠키 설정 버튼을 클릭할 수 없습니다:", e)

# 페이지 내용을 크롤링하는 함수
def crawl_page():
    # 페이지에 있는 각 항목에 대한 정보를 가져오는 로직을 여기에 작성
    # 예를 들어, 제목과 요약을 가져오려면 해당 요소를 찾아야 함
    articles = driver.find_elements(By.XPATH, "//div[@class='List-results-items']")
    for article in articles:
        # 제목과 요약을 추출
        title = article.find_element(By.XPATH, ".//h2").text
        abstract = article.find_element(By.XPATH, ".//div[@class='description']").text
        print(title, abstract)
        # 필요하다면 추출된 데이터를 파일에 저장하거나 다른 처리를 할 수 있음

# 페이지 네비게이션을 처리하는 함수
def navigate_pages():
    try:
        while True:
            crawl_page()
            next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next Page']")
            if not next_button or not next_button.is_enabled():
                print("마지막 페이지입니다.")
                break
            next_button.click()
            time.sleep(2)  # 페이지 로딩 대기
    except NoSuchElementException:
        print("다음 페이지 버튼을 찾을 수 없습니다.")

# 크롤링할 페이지 URL 리스트
url_list = [
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&highlight=true&returnType=SEARCH&matchPubs=true&returnFacets=ALL&ranges=2019_2019_Year",
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&newsearch=true&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&ranges=2020_2020_Year",
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&ranges=2021_2021_Year&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true",
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&ranges=2022_2022_Year&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true",
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&ranges=2023_2023_Year&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true"
]

# 각 페이지에 대해 크롤링 수행
for url in url_list:
    # 페이지로 이동
    driver.get(url)

    # 쿠키 팝업 처리
    handle_cookie_popup()

    # 페이지 로드를 기다리기 위해 잠시 대기
    time.sleep(2)

    # 페이지 네비게이션 시작
    navigate_pages()

# 웹 드라이버 종료
driver.quit()


