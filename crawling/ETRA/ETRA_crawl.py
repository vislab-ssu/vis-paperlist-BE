import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ETRA_url_list_sessionTrue = [
    "https://dl.acm.org/doi/proceedings/10.1145/3588015"    # 2023-1
    "https://dl.acm.org/doi/proceedings/10.1145/3517031"    # 2022-1
    "https://dl.acm.org/doi/proceedings/10.1145/3448018"    # 2021-2
    "https://dl.acm.org/doi/proceedings/10.1145/3379156"    # 2020-2
    "https://dl.acm.org/doi/proceedings/10.1145/3379157"    # 2020-3
]

ETRA_url_list_sessionTrue_unusal = [
    "https://dl.acm.org/doi/proceedings/10.1145/3448017"    # 2021-1
    "https://dl.acm.org/doi/proceedings/10.1145/3450341"    # 2021-3
    "https://dl.acm.org/doi/proceedings/10.1145/3379155"    # 2020-1
]

ETRA_url_list_sessionFalse = [
    "https://dl.acm.org/doi/proceedings/10.1145/3314111"    # 2019

]

ETRA_url_list_unusal_domStructure = [
    "https://dl.acm.org/do/10.1145/event-17181/abs/"    # 2023-2
    "https://dl.acm.org/do/10.1145/event-16137/abs/"    # 2022-2
]

# /////////////////////////////////////////////////////////////////

# session 구분이 있는 ETRA
def ETRA_sessionTrue(url:str) -> list[dict]:
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

    # # JSON 파일로 저장
    # with open('collected_data.json', 'w', encoding='utf-8') as f:
    #     json.dump(collected_data, f, ensure_ascii=False, indent=4)


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

# session 구분이 있는 ETRA(session이 모두 열려있음)
def ETRA_sessionTrue_unusal(url:str) -> list[dict]:
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
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tableOfContent"]')))
    container = driver.find_element(By.XPATH, '//*[@id="tableOfContent"]')

    # 상위 요소 내의 모든 div 요소(session 목록)를 찾음
    sessions_raw_data = container.find_elements(By.XPATH, './div')
    sessions = sessions_raw_data[1:]
    for session in sessions:
        print('#################################################')
        sessionTitle = session.find_element(By.XPATH, './div')
        sessionTitle = sessionTitle.text
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

    # # JSON 파일로 저장
    # with open('collected_data.json', 'w', encoding='utf-8') as f:
    #     json.dump(collected_data, f, ensure_ascii=False, indent=4)


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

# session 구분이 없는 ETRA
def ETRA_sessionFalse(url:str) -> list[dict]:
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

# /////////////////////////////////////////////////////////////////
    
# 일반적이지 않은 구조의 ETRA
def ETRA_unusal_domStructure(url:str) -> list[dict]:
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
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="pb-page-content"]/div/div[1]/div[1]/div/div/div[1]/div')))
    json_title = driver.find_element(By.XPATH, '//*[@id="pb-page-content"]/div/div[1]/div[1]/div/div/div[1]/div')
    print(json_title.text, '\n')

    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="skip-to-main-content"]/main/div')))
    container = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div')

    papers_raw_data= container.find_elements(By.XPATH, '//*[@id="skip-to-main-content"]/main/div/div/div')
    papers = papers_raw_data[1:]
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

# /////////////////////////////////////////////////////////////////

def crawl(url: str, logic:callable(str)) -> None:
    logic(url)

for url in ETRA_url_list_sessionTrue:
    crawl(url, ETRA_sessionTrue)

for url in ETRA_url_list_sessionTrue_unusal:
    crawl(url, ETRA_sessionTrue_unusal)

for url in ETRA_url_list_sessionFalse:
    crawl(url, ETRA_sessionFalse)

for url in ETRA_url_list_unusal_domStructure:
    crawl(url, ETRA_unusal_domStructure)