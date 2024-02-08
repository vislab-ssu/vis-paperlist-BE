import mysql.connector
import os
import json

# 데이터베이스 연결 설정
config = {
    "host": "localhost",
    "user": "root",
    "passwd": "shdoit!1019",
    "database": "vis_sql"
}

# 데이터베이스 연결
db = mysql.connector.connect(**config)
cursor = db.cursor()

# 'Result' 폴더 내의 모든 JSON 파일 처리
folder_path = 'Result'  # JSON 파일이 저장된 폴더 경로
json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

for json_file in json_files:
    file_path = os.path.join(folder_path, json_file)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        # 데이터를 citing 기준으로 그룹화
        grouped_data = {}
        for item in data:
            citing = item.get('citing')
            if citing not in grouped_data:
                grouped_data[citing] = []
            grouped_data[citing].append(item)

        # 그룹화된 데이터를 데이터베이스에 삽입
        for citing, citations in grouped_data.items():
            for citation in citations:
            # 'creation' 필드 처리
                creation = citation.get('creation', '0000-01-01')
                # 연도만 있는 경우에는 월과 일을 추가
                if len(creation) == 4:
                    creation += "-01-01"
                # 연도와 월만 있는 경우에는 일을 추가
                elif len(creation) == 7:
                    creation += "-01"
                
                # 삽입할 데이터를 준비합니다. 
                values = (
                    citation.get('timespan', ''),
                    citation.get('cited', ''),
                    citation.get('journal_sc', ''),
                    citation.get('author_sc', ''),
                    citation.get('oci', ''),
                    creation,  # 수정된 'creation' 변수를 사용
                    citing  # 그룹화 기준
                )
                sql = """INSERT INTO citations (timespan, cited, journal_sc, author_sc, oci, creation, citing)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, values)
        db.commit()

# 데이터베이스 연결 종료
db.close()

