## Open Citations api 연동

import os
import csv
from requests import get
import json
from dotenv import load_dotenv

load_dotenv()

# HTTP 헤더 설정
HTTP_HEADERS = {"Authorization": os.getenv("OPEN_CITATION_KEY")}

# 'Result' 폴더가 없으면 생성
if not os.path.exists('Result'):
    os.makedirs('Result')

# CSV 파일에서 DOI 리스트를 읽기
doi_list = []
with open('paperlist_doi.csv', mode='r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if 'DOI' in row:  # 'DOI' 열이 있는지 확인
            doi_list.append(row['DOI'])

# 각 DOI에 대해 API 호출 및 데이터 저장
for doi in doi_list:
    # API 호출을 위한 URL 구성
    API_CALL = f"https://opencitations.net/index/api/v1/references/{doi}"
    # HTTP GET 요청 수행
    response = get(API_CALL, headers=HTTP_HEADERS)

    if response.status_code == 200:
        # 응답 데이터를 JSON 형식으로 변환
        data = response.json()
        # 파일 이름에 사용될 수 있도록 DOI 내의 '/'를 '_'로 대체
        safe_filename = doi.replace("/", "_")
        filename = f'Result/{safe_filename}.json'
        
        # JSON 데이터를 파일에 쓰기
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Data saved to {filename}")
    else:
        # API 호출 실패 시 메시지 출력
        print(f"Failed to fetch data for DOI: {doi}")



