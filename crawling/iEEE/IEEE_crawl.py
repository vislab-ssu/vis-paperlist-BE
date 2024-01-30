######## 아직 연도별 논문 총갯수 개산 + 네비바 이동 구현 x

import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

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

# 페이지의 데이터를 수집하는 함수
def collect_data_from_page():
    data = []

    articles = driver.find_elements(By.CSS_SELECTOR, ".List-results-items .hide-mobile .d-flex.result-item .col.result-item-align.px-3 .text-md-md-lh")

    # articles를 루프 돌면서 각 논문의 상세 페이지로 이동
    for article in articles:
        try:
            # 상세 페이지로 이동
            detail_link = article.find_element(By.TAG_NAME, "a")
            detail_link.click()

            # 새 탭으로 전환
            driver.switch_to.window(driver.window_handles[-1])

            # 상세 페이지에서 데이터 수집
            retry_count = 3
            while retry_count > 0:
                try:
                    title = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'span.document-title-text'))
                    ).text

                    authors = []
                    authors_info = driver.find_elements(By.CSS_SELECTOR, '.blue-tooltip span.hover a span')
                    for author_info in authors_info:
                        authors.append(author_info.text)

                    citing_paper_count = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button.document-banner-metric-count'))
                    ).text

                    abstract = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.abstract-text'))
                    ).text

                    publication_title = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.row.g-0.u-pt-1 a'))
                    ).text

                    publication_date = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-6.u-pb-1.doc-abstract-confdate'))
                    ).text

                    doi = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-6.u-pb-1.stats-document-abstract-doi'))
                    ).text

                    # 수집된 데이터를 딕셔너리로 저장
                    paper_data = {
                        'title': title,
                        'authors': authors,
                        'citing_paper_count': citing_paper_count,
                        'abstract': abstract,
                        'publication_title': publication_title,
                        'publication_date': publication_date,
                        'DOI': f'https://doi.org/{doi}'
                    }

                    # 수집된 데이터를 리스트에 추가
                    data.append(paper_data)

                    # 원래 탭으로 돌아가기
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    break  # while 루프 종료
                except StaleElementReferenceException:
                    print("Stale element 오류 발생. 재시도 중...")
                    retry_count -= 1

        except NoSuchElementException:
            print("필요한 요소를 찾을 수 없습니다.")
            continue
        except Exception as e:
            print("데이터 수집 중 오류 발생:", e)

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
    collected_data = []  # 전체 데이터를 저장할 리스트 초기화
    for url in url_list:
        driver.get(url)
        handle_cookie_popup()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='List-results-items']")))
        data = collect_data_from_page()
        collected_data.extend(data)  # 수집된 데이터를 전체 데이터 리스트에 추가
        driver.close()  # 현재 연도의 페이지를 모두 확인한 후에 브라우저를 닫음

    # 모든 페이지의 데이터를 한 번에 JSON 파일로 저장
    save_data_to_json(collected_data, 'results.json')

# 크롤링할 페이지 URL 리스트 생성
base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?contentType=conferences&queryText=ieee%20Vis&highlight=true&returnType=SEARCH&matchPubs=true&returnFacets=ALL&ranges="
url_list = [f"{base_url}{year}_{year}_Year" for year in range(2010, 2024)]

# 크롤링 실행
crawl_pages(url_list)

# 드라이버 종료
driver.quit()


