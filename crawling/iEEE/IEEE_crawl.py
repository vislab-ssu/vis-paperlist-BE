import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# Chrome WebDriver 경로 설정
webdriver_path = '/path/to/chromedriver'  # 실제 chromedriver 위치로 수정해주세요.

# 웹 드라이버 초기화
driver = webdriver.Chrome(executable_path=webdriver_path)

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

    # 페이지 소스를 출력 (여기서는 예시로 페이지 제목만 출력)
    print(driver.title)

    # 추가적인 데이터 추출이 필요한 경우, 여기에 코드 추가

# 웹 드라이버 종료
driver.quit()

