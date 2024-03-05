import os
import csv
from requests import get
import json
from collections import defaultdict
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

# 인용 카운트를 저장할 딕셔너리
citing_counts = defaultdict(int)

# 각 DOI에 대해 API 호출 및 데이터 저장
for doi in doi_list:
    # API 호출을 위한 URL 구성
    API_CALL = f"https://opencitations.net/index/api/v1/references/{doi}"
    # HTTP GET 요청 수행
    response = get(API_CALL, headers=HTTP_HEADERS)

    if response.status_code == 200:
        # 응답 데이터를 JSON 형식으로 변환
        data = response.json()
        
        # 각 응답 아이템에서 'citing' 정보 추출 및 카운트
        for item in data:
            if 'citing' in item:
                citing_counts[item['citing']] += 1

        print(f"Processed DOI: {doi}")
    else:
        # API 호출 실패 시 메시지 출력
        print(f"Failed to fetch data for DOI: {doi}")

# 카운트 결과를 CSV 파일에 저장
with open('Result/citing_counts.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Citing DOI', 'Count'])
    for citing_doi, count in citing_counts.items():
        writer.writerow([citing_doi, count])

print("Citing counts have been saved to Result/citing_counts.csv")
