from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time
import os

collected_data = []

driver = webdriver.Chrome()
# 브라우저 창을 최대화
driver.maximize_window()  
url = 'https://dl.acm.org/doi/proceedings/10.1145/2556288'
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
json_title = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/div/div[1]/div').text
print(json_title, '\n')

# 상위 요소(accordion-tabbed rlist)를 찾음
wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="skip-to-main-content"]/main/div[4]/div/div[2]/div[1]/div/div[2]/div/div')))
container = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[4]/div/div[2]/div[1]/div/div[2]/div/div')

# 상위 요소 내의 모든 div 요소(session 목록)를 찾음
sessions = container.find_elements(By.XPATH, './div')
sessions_count = len(sessions)

print('#################################################')

for session in sessions:
    # sessionCheck : session의 토글
    # 최상위 session을 제외하고 나머지 모든 session은 토글을 열기.
    sessionCheck = session.find_element(By.XPATH, './/a')
    if sessionCheck.get_attribute('id') != 'heading1':
        sessionCheck.click()
    
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

        # # 논문 doi
        # try:
        #     doi = paper.find_element(By.XPATH, './/div[contains(@class, "issue-item__detail")]/span/a').text
        # except NoSuchElementException:
        #     doi = "NONE"
        
        current_tab = driver.window_handles[0]
        # 새 탭 전환 ########################################################################################
        paper_new_tab = paper.find_element(By.XPATH, './/h5[@class="issue-item__title"]/a')
        # 요소의 `target` 속성을 `_blank`로 설정(변경)하여 새 탭에서 열릴 수 있도록
        driver.execute_script("arguments[0].target='_blank'; arguments[0].click();", paper_new_tab)
        new_tab = driver.window_handles[1]

        driver.switch_to.window(new_tab)


        # 논문 날짜
        try:
            # date = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/article/div[1]/div[2]/div/div/div[4]/div/span[1]/span').text
            date = driver.find_element(By.XPATH, '//div[@class="issue-item__detail"]/span[1]').text
        except NoSuchElementException:
            date = "NONE"
        
        # 논문 초록
        try:
            abstract = driver.find_element(By.XPATH, '//div[@class="abstractSection abstractInFull"]/p').text
        except NoSuchElementException:
            abstract = "NONE"

        # 논문 저자
        try:
            authors_li = driver.find_elements(By.XPATH, '//*[@id="sb-1"]/ul/li')
            authors_li = authors_li[1:]
            authors = []
            for author_li in authors_li:
                author = author_li.find_element(By.XPATH, './/a/span/div/span/span').text
                authors.append(author)

        except NoSuchElementException:
            authors = ["NONE"]

        # 논문 doi
        try:
            last_span = driver.find_element(By.XPATH, '(//div[@class="issue-item__detail"]/span)[last()]')
            doi = last_span.text
        except NoSuchElementException:
            doi = "NONE"

        # 논문 citation
        try:
            citation = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/article/div[1]/div[2]/div/div/div[6]/div/div[1]/div/ul/li[1]/span/span[1]').text
        except NoSuchElementException:
            citation = "NONE"

        print('title:', title)
        print('conferenceTitle:', json_title)
        print('session:', sessionTitle)
        print('date:', date)
        print('authors:', ', '.join(authors))   # 저자 이름들을 쉼표로 구분하여 출력
        print('doi:', doi)
        print('citation:', citation)
        print('abstract:', abstract)

        print('\n')

        # 각 논문의 데이터를 딕셔너리로 저장
        paper_data = {
            'title': title,
            'conferenceTitle': json_title,
            'Session': sessionTitle,
            'data': date,
            'authors': authors,
            'DOI': doi,
            'citation': citation,
            'abstract': abstract,
        }

        # 수집된 데이터 리스트에 추가
        collected_data.append(paper_data)

        # 기존 탭으로 돌아가기
        driver.close()  # 새로 열린 페이지 닫기
        driver.switch_to.window(current_tab) 


# # JSON 파일로 저장
# with open('collected_data.json', 'w', encoding='utf-8') as f:
#     json.dump(collected_data, f, ensure_ascii=False, indent=4)


# json_title.text에서 파일명으로 사용할 수 없는 문자 제거 또는 대체
safe_filename = json_title.replace("'", "").replace(":", "").replace(" ", "_")
# 파일명 생성
filename = f'{safe_filename}.json'
file_path = os.path.join('Result', filename)

# JSON 파일로 저장
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(collected_data, f, ensure_ascii=False, indent=4)

driver.quit()