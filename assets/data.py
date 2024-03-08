import os
import json
import re
import csv

FILE_PATH = os.path.realpath(__file__)
DIR = os.path.dirname(FILE_PATH)
ORIG_PATH = DIR + '/data/new'
FILES = sorted([file for file in os.listdir(ORIG_PATH)])

conference_session = [['id', 'name', 'upper_category_id', 'year']]  # journals 테이블
authors = dict()
conference_session_nameList = dict()    
author_paper = [['author_id', 'paper_id']]
papers = [['id', 'abstract', 'title', 'author',
           'conference_session_id', 'date', 'DOI', 'citation']]

for file in FILES:
    # .json 분리
    file_name, extra = file.split('.')
    if extra != 'json':
        continue
    # conference: 영문자 또는 밑줄로 구성된 그룹 / year: 하나 이상의 숫자로 구성된 그룹
    # 두 그룹을 추출하여 각각 변수에 할당
    conference, year = re.search(r'([A-Za-z_]+)([0-9]+)+', file_name).groups()
    # conference : conference의 밑줄을 공백으로 바꾸고, 문자열의 양쪽 끝 공백 제거(strip함수)
    conference = conference.replace('_', ' ').strip()
    # year : 처리
    year = int(year)
    if year < 24:
        year += 2000
    elif 23 < year < 100:
        year += 1900
    else:
        pass
    print(conference, year)

    # (1) journals(conference_session): conference 정보에 대한 raw 추가
    conference_session_nameList[conference + str(year)] = len(conference_session_nameList) + 1
    conference_id = conference_session_nameList[conference + str(year)]

    conference_session.append([len(conference_session), conference, None, year])

    with open(ORIG_PATH + '/' + file) as f:
        json_data = json.load(f)
        for paper in json_data:
            # (1) 에서 추가된 conference에 session이 존재하는 paper가 있는 경우
            if (paper['Session'] if 'Session' in paper else '') + conference + str(year) not in conference_session_nameList:
                # conference_session_nameList 예시) "CHI2000": 1, "CHI2001": 2, "CHI2002": 3, "Session: Contextual DisplaysCHI2002": 4
                conference_session_nameList[paper['Session'] + conference + str(year)] = len(conference_session_nameList) + 1
                # (2) journals(conference_session): session 정보에 대한 raw 추가 (session의 경우 upper_category가 본 conference 이름으로 추가)
                conference_session.append([len(conference_session), paper['Session'], conference_id, year])

            if 'data' in paper:
                paper_date = paper['data']  
            elif 'date' in paper:
                paper_date = paper['date']
            papers.append([len(papers), paper['abstract'], paper['title'], paper['authors'], 
                           len(conference_session)-1, paper_date, paper['DOI'], (paper['citation'] if paper['citation'] else 0)])
            # 위 papers에 raw 추가 코드에서 날짜의 키 값을 data/date로 한 것은 CHI, ETRA 크롤링 결과의 키값 오류 때문.
            
            for author in paper['authors']:
                # strip() : 양 끝에 있는 공백 제거
                author = author.strip()
                if author not in authors:
                    authors[author] = len(authors)+1
                author_idx = authors[author]
                author_paper.append([author_idx, len(papers)-1])

# authors 딕셔너리: {'John Doe': 1, 'Jane Smith': 2} => [[1, 'John Doe'], [2, 'Jane Smith']]로 변환
authors = [[id, auth] for (auth, id) in authors.items()]
authors.insert(0, ['id', 'name'])

# print(conference_session)
# print(authors[::1000])
# print(author_paper[::1000])
# print(papers[::1000])

# authors = authors[0] + [", ".join(author) for author in authors[1:]]
# id,abstract,title,author,conference_session_id,date,DOI,citation
ID_IDX = 0
ABSTRACT_IDX = 1
TITLE_IDX = 2
AUTHOR_IDX = 3
CONF_SESS_ID_IDX = 4
DATE_IDX = 5
DOI_IDX = 6
CITATION_IDX = 7
month_to_number = {
    'January': 1,
    'Jan': 1,
    'February': 2,
    'Feb': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}
for paper_idx in range(1, len(papers)):

    # ABSTRACT
    # 예외처리: papers Abstract이 NONE인 경우
    if papers[paper_idx][ABSTRACT_IDX] == "NONE":
        papers[paper_idx][ABSTRACT_IDX] = None

    # AUTHOR
    if len(papers[paper_idx][AUTHOR_IDX]):
        # json 형태의 저자 목록을 변환(['A. Lopes', 'K. Brodlie'] => A. Lopes, K. Brodlie)
        papers[paper_idx][AUTHOR_IDX] = ", ".join(papers[paper_idx][AUTHOR_IDX])
        # 예외처리: 저자가 NONE인 경우
        if papers[paper_idx][AUTHOR_IDX] == "NONE":
            papers[paper_idx][AUTHOR_IDX] = None
    else:
        # 예외처리: 저자가 없는 경우
        papers[paper_idx][AUTHOR_IDX] = None

    # DATE
    if papers[paper_idx][DATE_IDX] == "NONE":
        papers[paper_idx][DATE_IDX] = f'0000-01-01'
    else:
        # 예외처리: 5-7 March 2008 형식
        if re.search(r'([0-9]{1,2}-[0-9]{1,2}) ([A-Za-z_]+) ([0-9]+)', papers[paper_idx][DATE_IDX]):
            # print("1")
            # print(papers[paper_idx][DATE_IDX])
            dummy, month, year = re.search(r'([0-9]{1,2}-[0-9]{1,2}) ([A-Za-z_]+) ([0-9]+)', papers[paper_idx][DATE_IDX]).groups()

        # 예외처리: 28 Feb.-2 March 2012 형식
        elif re.search(r'([0-9]{1,2}) ([A-Za-z]+)\.-([0-9]{1,2}) ([A-Za-z_]+) ([0-9]+)', papers[paper_idx][DATE_IDX]):
            # print("2")
            # print(papers[paper_idx][DATE_IDX])
            dummy1, dummy2, dummy3, month, year = re.search(r'([0-9]{1,2}) ([A-Za-z]+)\.-([0-9]{1,2}) ([A-Za-z_]+) ([0-9]+)', papers[paper_idx][DATE_IDX]).groups()
        
        # 예외처리: Jan.-March 2003 형식
        elif re.search(r'([A-Za-z]+)\.-([A-Za-z]+).? ([0-9]+)', papers[paper_idx][DATE_IDX]):
            # print("3")
            # print(papers[paper_idx][DATE_IDX])
            month, dummy, year = re.search(r'([A-Za-z]+)\.-([A-Za-z]+).? ([0-9]+)', papers[paper_idx][DATE_IDX]).groups()
        # 예외처리: Jan. 2011
        elif re.search(r'([A-Za-z]+)\. ([0-9]+)', papers[paper_idx][DATE_IDX]):
            # print("4")
            # print(papers[paper_idx][DATE_IDX])
            month, year = re.search(r'([A-Za-z]+)\. ([0-9]+)', papers[paper_idx][DATE_IDX]).groups()

        else:
            # print("10")
            # print(papers[paper_idx][DATE_IDX])
            month, year = papers[paper_idx][DATE_IDX].split()
            
        # DATE 형식 'YYYY-MM-DD' 표준화
        papers[paper_idx][DATE_IDX] = f'{year}-{month_to_number[month]:02d}-01'

    # CITATION
    # 예외처리: citation인 NONE인 경우
    if papers[paper_idx][CITATION_IDX] == "NONE":
        papers[paper_idx][CITATION_IDX] = 0
    # 예외처리: citation이 1000회 이상으로 1,000 형식의 ,가 들어간 경우(IEEE 논문들의 citation이 integer이므로 문자열 처리)
    elif str(papers[paper_idx][CITATION_IDX]).count(','):
        papers[paper_idx][CITATION_IDX] = papers[paper_idx][CITATION_IDX].replace(',', '')


DATA_PATH = DIR + '/data/new_csv'
with open(DATA_PATH + '/journals.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerows(conference_session)

with open(DATA_PATH + '/authors.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerows(authors)

with open(DATA_PATH + '/author_paper.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerows(author_paper)

with open(DATA_PATH + '/papers.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerows(papers)
