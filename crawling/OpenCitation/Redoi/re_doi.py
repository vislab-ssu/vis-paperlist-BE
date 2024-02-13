## 링크 형식인 doi를 doi 부분만 추출하는 코드

import csv

# 원본 CSV 파일 경로
input_file_path = 'paperlist_doi_input.csv'  
# 수정된 데이터를 저장할 새 CSV 파일 경로
output_file_path = 'paperlist_doi.csv'  

# CSV 파일을 열고 수정하기
with open(input_file_path, mode='r', encoding='utf-8') as infile, open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
    
    for row in reader:
        # URL이 있는 열의 인덱스는 1로 가정 (0번째는 ID)
        row[1] = row[1].replace('https://doi.org/', '')  # URL에서 'https://doi.org/' 제거
        writer.writerow(row)
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)


