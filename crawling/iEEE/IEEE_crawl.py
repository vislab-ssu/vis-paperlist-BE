import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


# 웹 드라이버 초기화
service = Service('/Users/choeseohyeon/.cache/selenium/chromedriver/mac-arm64/120.0.6099.109/chromedriver')
driver = webdriver.Chrome(service=service)

# 브라우저 창을 최대화
driver.maximize_window()

# 쿠키 팝업 처리하는 함수
def handle_cookie_popup():
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(., "모두 동의")]'))).click()
        print("쿠키 설정이 처리되었습니다.")
    except NoSuchElementException:
        print("쿠키 설정 버튼을 찾을 수 없습니다.")
    except TimeoutException:
        print("쿠키 설정 대화 상자가 표시되지 않습니다.")

# 특정 페이지의 데이터를 수집하는 함수
def collect_data_from_page():
    data = []
    articles = driver.find_elements(By.XPATH, "//div[@class='List-results-items']")
    for article in articles:
        try:
            # 기사 제목과 요약 텍스트 추출
            title = article.find_element(By.XPATH, ".//h2").text
            abstract = article.find_element(By.XPATH, ".//div[contains(@class, 'description')]").text
            # 기사 제목을 클릭하여 상세 페이지로 이동
            article.find_element(By.XPATH, ".//h2/a").click()
            
            # 새로운 탭으로의 전환을 처리
            driver.switch_to.window(driver.window_handles[1])
            
            # 새 페이지에서 필요한 추가 데이터 수집 로직을 여기에 구현
            paper_url = driver.current_url

            # 추가 데이터 수집 후 원래 페이지로 돌아오기
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
            # 수집된 데이터 저장
            data.append({'title': title, 'abstract': abstract, 'url': paper_url})
        except NoSuchElementException:
            continue
        except Exception as e:
            print("Error while collecting data:", e)
    return data


# 수집된 데이터를 JSON 파일로 저장하는 함수
def save_data_to_json(data, filename):
    if not os.path.exists('collected_data'):
        os.makedirs('collected_data')
    path = os.path.join('collected_data', filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 각 페이지에 대해 크롤링 수행하는 함수
def crawl_pages(url_list):
    for url in url_list:
        driver.get(url)
        handle_cookie_popup()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='List-results-items']")))
        data = collect_data_from_page()
        save_data_to_json(data, 'results.json')

# 크롤링할 페이지 URL 리스트
url_list = [
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&highlight=true&returnType=SEARCH&matchPubs=true&returnFacets=ALL&ranges=2019_2019_Year",
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&newsearch=true&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&ranges=2020_2020_Year",
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&ranges=2021_2021_Year&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true",
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&ranges=2022_2022_Year&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true",
    "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:IEEE%20Transactions%20on%20Visualization%20and%20Computer%20Graphics)%20AND%20(%22All%20Metadata%22:1)&ranges=2023_2023_Year&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true"
]

# 크롤링 실행
crawl_pages(url_list)

# 드라이버 종료
driver.quit()