### ieee xplore

import requests
import json
import os
from collections import defaultdict
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키와 기본 URL 설정
api_key = os.getenv("IEEE_API_KEY")
base_url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

# 결과 저장 디렉토리 확인 및 생성
save_dir = 'Result'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 연도별로 API 호출 및 데이터 저장
for year in range(2010, 2024):  # 2010년부터 2023년까지
    search_params = {
        "query": "ieee Vis",
        "content_type": "Conferences",
        "start_year": year,
        "end_year": year,
        "apikey": api_key,
        "start_record": 1,
        "max_records": 200  # API의 최대 반환 항목 수를 고려하여 설정
    }
    
    # API 호출 및 응답 받기
    response = requests.get(base_url, params=search_params)
    
    # 응답 상태 확인 및 데이터 처리
    if response.status_code == 200:
        # JSON 응답 확인
        data = response.json()
        papers = data.get('articles', [])
        
        # 연도별 파일에 저장
        filename = f'IEEE_{year}.json'
        file_path = os.path.join(save_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=4)
        
        print(f"Data saved to {file_path}")
    else:
        print(f"Error in {year}: {response.status_code}")
        print(response.text)
