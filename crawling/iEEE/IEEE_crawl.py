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
    collected_data = []
    articles = driver.find_elements(By.CSS_SELECTOR, ".List-results-items .hide-mobile .d-flex.result-item .col.result-item-align.px-3 .text-md-md-lh")

    for article in articles:
        try:
            # 상세 페이지로 이동
            detail_link = article.find_element(By.TAG_NAME, "a")
            detail_link.click()
            
            # 새 탭으로의 전환을 처리합니다.
            current_tab = driver.current_window_handle
            driver.switch_to.window(driver.window_handles[-1])

            # 여기에서 상세 페이지의 데이터 수집 로직을 구현합니다.
            # 제목(title)
            title = driver.find_element(By.CSS_SELECTOR, 'h1.document-title span').text

            # 저자들(authors)
            authors_elements = driver.find_elements(By.CSS_SELECTOR, 'div.authors-info-container span.authors-info span span a span')
            authors = [author.text for author in authors_elements]

            # 인용 횟수(citing_paper_count)
            citing_paper_count = driver.find_element(By.CSS_SELECTOR, 'button.document-banner-metric div.document-banner-metric-count').text

            # 초록(abstract)
            abstract = driver.find_element(By.CSS_SELECTOR, 'div.abstract-text').text

            # 출판물 제목(publication_title)
            publication_title = driver.find_element(By.CSS_SELECTOR, 'div.document-abstract a').text

            # 출판 날짜(publication_date)
            publication_date = driver.find_element(By.CSS_SELECTOR, 'div.doc-abstract-confdate').text

            # DOI
            doi_suffix = driver.find_element(By.CSS_SELECTOR, 'div.stats-document-abstract-doi').text
            doi = f"https://doi.org/{doi_suffix}"

            paper_data = {
                'title': title,
                'authors': authors,
                'citing_paper_count': citing_paper_count,
                'abstract': abstract,
                'publication_title': publication_title,
                'publication_date': publication_date,
                'DOI': doi
            }

            collected_data.append(paper_data)

            # 새 탭을 닫고 원래 탭으로 돌아갑니다.
            driver.close()
            driver.switch_to.window(current_tab)

        except NoSuchElementException:
            print("필요한 요소를 찾을 수 없습니다.")
            continue
        except Exception as e:
            print("데이터 수집 중 오류 발생:", e)

    return collected_data




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

# 크롤링할 페이지 URL 리스트 생성
base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?contentType=conferences&queryText=ieee%20Vis&highlight=true&returnType=SEARCH&matchPubs=true&returnFacets=ALL&ranges="
url_list = [f"{base_url}{year}_{year}_Year" for year in range(2010, 2024)]

# 크롤링 실행
crawl_pages(url_list)

# 드라이버 종료
driver.quit()

