import os
from requests import get
import json

# HTTP 헤더 설정
HTTP_HEADERS = {"Authorization": "089eb33b-2ab6-4679-9425-9ab03157d3e0"}

# 'Result' 폴더가 없으면 생성
if not os.path.exists('Result'):
    os.makedirs('Result')

# 파일에서 DOI 리스트를 읽기, 빈 줄 무시
with open('doi_list.txt', 'r') as file:
    doi_list = [line.strip() for line in file if line.strip()]

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
        filename = f'{safe_filename}.json'
        file_path = os.path.join('Result', filename)
        
        # JSON 데이터를 파일에 쓰기
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Data saved to {file_path}")
    else:
        # API 호출 실패 시 메시지 출력
        print(f"Failed to fetch data for DOI: {doi}")


