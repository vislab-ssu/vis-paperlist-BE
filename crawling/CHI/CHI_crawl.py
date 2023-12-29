import json
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup

# https://dl.acm.org/doi/proceedings/10.1145/3173574    # 2018 구조 개이상함
# https://dl.acm.org/doi/proceedings/10.1145/507752   # 2002-2 구조 이상함


CHI_url_list_sessionTrue = [
    # "https://dl.acm.org/doi/proceedings/10.1145/3544548", #2023
    # "https://dl.acm.org/doi/proceedings/10.1145/3491102", #2022
    # "https://dl.acm.org/doi/proceedings/10.1145/3411764", #2021
    # "https://dl.acm.org/doi/proceedings/10.1145/3025453", #2017
    # "https://dl.acm.org/doi/proceedings/10.1145/2858036", #2016
    # "https://dl.acm.org/doi/proceedings/10.1145/2702123", #2015
    "https://dl.acm.org/doi/proceedings/10.1145/2556288", #2014
    "https://dl.acm.org/doi/proceedings/10.1145/2470654", #2013
    "https://dl.acm.org/doi/proceedings/10.1145/2207676", #2012
    "https://dl.acm.org/doi/proceedings/10.1145/1978942", #2011
    "https://dl.acm.org/doi/proceedings/10.1145/1753326", #2010
    "https://dl.acm.org/doi/proceedings/10.1145/1518701", #2009
    "https://dl.acm.org/doi/proceedings/10.1145/1357054", #2008
    "https://dl.acm.org/doi/proceedings/10.1145/1240624", #2007
    "https://dl.acm.org/doi/proceedings/10.1145/1124772", #2006
    "https://dl.acm.org/doi/proceedings/10.1145/1054972", #2005
    "https://dl.acm.org/doi/proceedings/10.1145/642611", #2003
    "https://dl.acm.org/doi/proceedings/10.1145/503376", #2002-1
]

CHI_url_list_sessionFalse = {
    "https://dl.acm.org/doi/proceedings/10.1145/3313831", #2020
    "https://dl.acm.org/doi/proceedings/10.1145/3290605", #2019
    "https://dl.acm.org/doi/proceedings/10.1145/985692", #2004
    "https://dl.acm.org/doi/proceedings/10.1145/365024", #2001
    "https://dl.acm.org/doi/proceedings/10.1145/332040", #2000
    "https://dl.acm.org/doi/proceedings/10.1145/302979", #1999
    "https://dl.acm.org/doi/proceedings/10.1145/286498", #1998-1
    "https://dl.acm.org/doi/proceedings/10.5555/274644", #1998-2
    "https://dl.acm.org/doi/proceedings/10.1145/258549", #1997
}

# session 구분이 있는 CHI
def CHI_sessionTrue(url:str) -> list[dict]:
    collected_data = []

    driver = webdriver.Chrome()
    # 브라우저 창을 최대화
    driver.maximize_window()  
    driver.get(url)    

    # 페이지의 동적 콘텐츠 로드를 기다림 (드라이버가 모든 요소를 찾는데 최대 10초 동안 기다리게 함)
    driver.implicitly_wait(10)  
    # html = driver.page_source   # 페이지의 소스 가져오기
    wait = WebDriverWait(driver, 10)

    # chrome driver를 통해 페이지를 열고 나서 뜨는 cookie를 클릭하여 제거
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')))
    driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()

    # json_title로 설정할 연도
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/div/div[1]/div')))
    json_title = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/div/div[1]/div')
    print(json_title.text, '\n')

    # 상위 요소를 찾음
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="skip-to-main-content"]/main/div[4]/div/div[2]/div[1]/div/div[2]/div/div')))
    container = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[4]/div/div[2]/div[1]/div/div[2]/div/div')

    # 상위 요소 내의 모든 div 요소(session 목록)를 찾음
    sessions = container.find_elements(By.XPATH, './div')
    for session in sessions:
        #최상위 session을 제외하고 나머지 모든 session은 토글을 열기.
        sessionCheck = session.find_element(By.XPATH, './/a')
        if sessionCheck.get_attribute('id') != 'heading1':
            sessionCheck.click()

        print('#################################################')
        sessionTitle = session.text
        print(sessionTitle)
        print('\n')
        papers = session.find_elements(By.XPATH, './/div[contains(@class,"issue-item__content-right")]')
        for paper in papers:
            # 논문 제목
            try:
                title = paper.find_element(By.XPATH, './/h5[contains(@class,"issue-item__title")]').text
            except NoSuchElementException:
                title = "NONE"

            # 논문 저자
            try:
                # 클릭 시도
                try:
                    ## 요소가 존재할 때까지 기다림
                    ## WbeDriverWait : 특정 요소에 대해 명시적으로 대기시간을 설정. 10초동안 만족하는 요소를 찾음
                    ## EC.presence_of_element_located 조건을 사용하여 특정 요소의 존재를 확인

                    # more_button = WebDriverWait(paper, 20).until(
                    #     EC.element_to_be_clickable((By.XPATH, './/li[contains(@class, "count-list")]/a'))
                    # )
                    # # 요소를 찾은 후 해당 요소를 찾아서 스크롤하기까지의 시간을 부여한다.
                    # time.sleep(1)
                    # more_button.click()

                    more_button_xpath = './/li[contains(@class, "count-list")]/a[contains(@class, "removed-items-count")]'
                    WebDriverWait(paper, 10).until(
                        EC.element_to_be_clickable((By.XPATH, more_button_xpath))
                    )
                    more_button = paper.find_element(By.XPATH, more_button_xpath)
                    more_button.click()
                    print("다중저자처리")

                    # DOM이 업데이트될 때까지 기다림
                    wait.until(EC.visibility_of_element_located((By.XPATH, '//li/a[contains(@class, "read-less")]')))

                # 클릭 실패
                except:
                    print("클릭 실패, 기존 요소 사용")
                    pass
                
                authors_list = paper.find_elements(By.XPATH, './/ul[@class="rlist--inline loa truncate-list trunc-done"]/li/a[not(contains(@class, "removed-items-count")) and not(contains(@class, "read-less"))]')
                authors = [author.text for author in authors_list]
                # print("authors: ", authors) 
                # print("\n")      

            except NoSuchElementException:
                authors = ["NONE"]

            # 논문 DOI
            try:
                DOI = paper.find_element(By.XPATH, './/div[contains(@class, "issue-item__detail")]/span/a').text
            except NoSuchElementException:
                DOI = "NONE"

            # 논문 초록
            try:
                abstract = paper.find_element(By.XPATH, './/div[contains(@class, "issue-item__abstract")]/p').text
            except NoSuchElementException:
                abstract = "NONE"

            print('title:', title)
            # print(authors)
            print('authors:', ', '.join(authors))  # 저자 이름들을 쉼표로 구분하여 출력
            print('DOI:', DOI)
            print('abstract:', abstract)
            print('Session:', sessionTitle)

            print('\n')

            # 각 논문의 데이터를 딕셔너리로 저장
            paper_data = {
                'title': title,
                'authors': authors,
                'DOI': DOI,
                'abstract': abstract,
                'Session': sessionTitle
            }

            # 수집된 데이터 리스트에 추가
            collected_data.append(paper_data)

    # json_title.text에서 파일명으로 사용할 수 없는 문자 제거 또는 대체
    safe_filename = json_title.text.replace("'", "").replace(":", "").replace(" ", "_")
    # 파일명 생성
    filename = f'{safe_filename}.json'
    file_path = os.path.join('Result', filename)

    # JSON 파일로 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(collected_data, f, ensure_ascii=False, indent=4)

    driver.quit()

# /////////////////////////////////////////////////////////////////

# session 구분이 없는 CHI
def CHI_sessionFalse(url:str) -> list[dict]:
    collected_data = []

    driver = webdriver.Chrome()
    driver.maximize_window()  # 브라우저 창을 최대화합니다.
    driver.get(url)

    driver.implicitly_wait(10)  # 페이지의 동적 콘텐츠 로드를 기다림
    html = driver.page_source   # 페이지의 소스 가져오기
    wait = WebDriverWait(driver, 10)

    # chrome driver를 통해 페이지를 열고 나서 뜨는 cookie를 제거
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')))
    driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()

    # json title로 설정할 연도
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/div/div[1]/div')))
    json_title = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/div/div[1]/div')
    print(json_title.text, '\n')

    # 상위 요소를 찾음 ( class="accordion-tabbed rlist" )
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="skip-to-main-content"]/main/div[4]/div/div[2]/div[1]/div/div[2]/div/div')))
    container = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[4]/div/div[2]/div[1]/div/div[2]/div/div')

    papers = container.find_elements(By.XPATH, './/div[contains(@class,"issue-item__content-right")]')
    for paper in papers:
        # 논문 제목
        try:
            title = paper.find_element(By.XPATH, './/h5[contains(@class,"issue-item__title")]').text
        except NoSuchElementException:
            title = "NONE"

        # 논문 저자
        try:
            # 클릭 시도
            try:
                ## 요소가 존재할 때까지 기다림
                ## WbeDriverWait : 특정 요소에 대해 명시적으로 대기시간을 설정. 10초동안 만족하는 요소를 찾음
                ## EC.presence_of_element_located 조건을 사용하여 특정 요소의 존재를 확인

                # more_button = WebDriverWait(paper, 20).until(
                #     EC.element_to_be_clickable((By.XPATH, './/li[contains(@class, "count-list")]/a'))
                # )
                # # 요소를 찾은 후 해당 요소를 찾아서 스크롤하기까지의 시간을 부여한다.
                # time.sleep(1)
                # more_button.click()

                more_button_xpath = './/li[contains(@class, "count-list")]/a[contains(@class, "removed-items-count")]'
                WebDriverWait(paper, 10).until(
                    EC.element_to_be_clickable((By.XPATH, more_button_xpath))
                )
                more_button = paper.find_element(By.XPATH, more_button_xpath)
                more_button.click()
                print("다중저자처리")

                # DOM이 업데이트될 때까지 기다림
                wait.until(EC.visibility_of_element_located((By.XPATH, '//li/a[contains(@class, "read-less")]')))

            # 클릭 실패
            except:
                print("클릭 실패, 기존 요소 사용")
                pass

            authors_list = paper.find_elements(By.XPATH, './/ul[@class="rlist--inline loa truncate-list trunc-done"]/li/a[not(contains(@class, "removed-items-count")) and not(contains(@class, "read-less"))]')
            authors = [author.text for author in authors_list]
            # print("authors: ", authors) 
            # print("\n")      

        except NoSuchElementException:
            authors = ["NONE"]
        
        # 논문 DOI
        try:
            DOI = paper.find_element(By.XPATH, './/div[contains(@class, "issue-item__detail")]/span/a').text
        except NoSuchElementException:
            DOI = "NONE"

        # 논문 초록
        try:
            abstract = paper.find_element(By.XPATH, './/div[contains(@class, "issue-item__abstract")]/p').text
        except NoSuchElementException:
            abstract = "NONE"

        print('Title: ', title)
        print('authors:', ', '.join(authors))  # 저자 이름들을 쉼표로 구분하여 출력
        print('DOI: ', DOI)
        print('Abstract: ', abstract)
        print('\n')

        # 각 논문의 데이터를 딕셔너리로 저장
        paper_data = {
            'title': title,
            'authors': authors,
            'DOI': DOI,
            'abstract': abstract,
        }

        # 수집된 데이터 리스트에 추가
        collected_data.append(paper_data)

    # json_title.text에서 파일명으로 사용할 수 없는 문자 제거 또는 대체
    safe_filename = json_title.text.replace("'", "").replace(":", "").replace(" ", "_")
    # 파일명 생성
    filename = f'{safe_filename}.json'
    file_path = os.path.join('Result', filename)

    # JSON 파일로 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(collected_data, f, ensure_ascii=False, indent=4)

    driver.quit()

# ////////////////////////////////////////////////

def crawl(url: str, logic: callable(str)) -> None:
    logic(url)


for url in CHI_url_list_sessionTrue:
    crawl(url, CHI_sessionTrue)
for url in CHI_url_list_sessionFalse:
    crawl(url, CHI_sessionFalse)