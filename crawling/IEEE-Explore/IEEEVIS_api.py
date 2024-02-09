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

def save_data(year, papers):
    # 저장할 데이터 형식에 맞게 파싱
    formatted_papers = []
    for paper in papers:
        authors = [author['full_name'] for author in paper.get('authors', {}).get('authors', [])]
        formatted_paper = {
            "title": paper.get("title", ""),
            "conferenceTitle": paper.get("publication_title", ""),
            "Content Type": paper.get("content_type", ""),
            "date": paper.get("publication_date", ""),
            "authors": authors,
            "DOI": paper.get("doi", ""),
            "citation": paper.get("citing_paper_count", 0),
            "abstract": paper.get("abstract", "")
        }
        formatted_papers.append(formatted_paper)
    
    # 연도별 파일에 저장
    filename = f'IEEE_{year}.json'
    file_path = os.path.join(save_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_papers, f, ensure_ascii=False, indent=4)
    
    print(f"Data saved to {file_path}")

def fetch_and_save_data(year):
    search_params = {
        "query": "ieee Vis",
        "content_type": "Conferences",
        "start_year": year,
        "end_year": year,
        "apikey": api_key,
        "start_record": 1,
        "max_records": 200  
    }
    
    # API 호출 및 응답 받기
    response = requests.get(base_url, params=search_params)
    if response.status_code == 200:
        data = response.json()
        papers = data.get('articles', [])
        save_data(year, papers)
    else:
        print(f"Error in {year}: {response.status_code}")
        print(response.text)

# 연도별로 API 호출 및 데이터 저장
for year in range(2010, 2024):  # 2010년부터 2023년까지
    fetch_and_save_data(year)

