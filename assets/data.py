import os
import json
import re
import csv

FILE_PATH = os.path.realpath(__file__)
DIR = os.path.dirname(FILE_PATH)
ORIG_PATH = DIR + '/data/new'
FILES = sorted([file for file in os.listdir(ORIG_PATH)])

conference_session = [['id', 'name', 'upper_category_id', 'year']]
authors = dict()
session = dict()
author_paper = [['author_id', 'paper_id']]
papers = [['id', 'abstract', 'title', 'author',
           'conference_session_id', 'date', 'DOI', 'citation']]

for file in FILES:
    file_name, ext = file.split('.')
    if ext != 'json':
        continue
    conference, year = re.search(r'([A-Za-z_]+)([0-9]+).+', file_name).groups()
    conference = conference.replace('_', ' ').strip()
    year = int(year)
    if year < 24:
        year += 2000
    elif 23 < year < 100:
        year += 1900
    print(conference, year)

    session[conference + str(year)] = len(session) + 1
    conference_id = session[conference + str(year)]

    conference_session.append(
        [len(conference_session), conference, None, year])

    with open(ORIG_PATH + '/' + file) as f:
        json_data = json.load(f)
        for paper in json_data:
            if (paper['Session'] if 'Session' in paper else '') + conference + str(year) not in session:
                session[paper['Session'] + conference +
                        str(year)] = len(session) + 1
                conference_session.append(
                    [len(conference_session), paper['Session'], conference_id, year])
            papers.append([len(papers), paper['abstract'],
                          paper['title'], paper['authors'], len(conference_session)-1, paper['data'], paper['DOI'], (paper['citation'] if paper['citation'] else 0)])
            for author in paper['authors']:
                author = author.strip()
                if author not in authors:
                    authors[author] = len(authors)+1
                author_idx = authors[author]
                author_paper.append([author_idx, len(papers)-1])


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
    'February': 2,
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

    if papers[paper_idx][ABSTRACT_IDX] == "NONE":
        papers[paper_idx][ABSTRACT_IDX] = None

    # print(type(papers[paper_idx][AUTHOR_IDX]),
    #       papers[paper_idx][AUTHOR_IDX][0])
    if len(papers[paper_idx][AUTHOR_IDX]):
        papers[paper_idx][AUTHOR_IDX] = ", ".join(
            papers[paper_idx][AUTHOR_IDX])
        if papers[paper_idx][AUTHOR_IDX] == "NONE":
            papers[paper_idx][AUTHOR_IDX] = None
    else:
        papers[paper_idx][AUTHOR_IDX] = None

    if papers[paper_idx][DATE_IDX] == "NONE":
        papers[paper_idx][DATE_IDX] = f'0000-01-01'
    else:
        month, year = papers[paper_idx][DATE_IDX].split()
        papers[paper_idx][DATE_IDX] = f'{year}-{month_to_number[month]:02d}-01'

    if papers[paper_idx][CITATION_IDX] == "NONE":
        papers[paper_idx][CITATION_IDX] = 0
    elif papers[paper_idx][CITATION_IDX].count(','):
        papers[paper_idx][CITATION_IDX] = papers[paper_idx][CITATION_IDX].replace(
            ',', '')


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
