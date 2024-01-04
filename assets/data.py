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
papers = [['id', 'abstract', 'title', 'author','conference_session_id', 'date', 'DOI', 'citation']]

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
    
    conference_session.append([len(conference_session), conference, None, year])

    with open(ORIG_PATH + '/' + file) as f:
        json_data = json.load(f)
        for paper in json_data:
            if (paper['Session'] if 'Session' in paper else '') + conference + str(year) not in session:
                session[paper['Session'] + conference + str(year)] = len(session) + 1
                conference_session.append([len(conference_session), paper['Session'], conference_id, year])
            papers.append([len(papers), paper['abstract'],
                          paper['title'], paper['authors'], len(conference_session)-1, paper['data'], paper['DOI'], paper['citation']])
            for author in paper['authors']:
                author = author.strip()
                if author not in authors:
                    authors[author] = len(authors)+1
                author_idx = authors[author]
                author_paper.append([author_idx, len(papers)-1])


authors = [[id, auth] for (auth, id) in authors.items()]
authors.insert(0, ['id', 'name'])

print(conference_session)
print(authors[::1000])
print(author_paper[::1000])
print(papers[::1000])

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
