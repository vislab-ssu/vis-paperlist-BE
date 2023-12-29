import os
import json
import re
import csv

FILE_PATH = os.path.realpath(__file__)
DIR = os.path.dirname(FILE_PATH)
ORIG_PATH = DIR + '/data/original'
FILES = sorted([file for file in os.listdir(ORIG_PATH)])

journals = [['id', 'name', 'year']]
authors = dict()
author_paper = [['author_id', 'paper_id']]
papers = [['id', 'abstract', 'title', 'author', 'journal_id']]

for file in FILES:
    file_name, ext = file.split('.')
    if ext != 'json':
        continue
    conference, year = re.search(r'([^0-9]+)([0-9]+)', file_name).groups()
    year = int(year)
    if year < 24:
        year += 2000
    elif 23 < year < 100:
        year += 1900
    print(conference, year)
    journals.append([len(journals), conference, year])

    with open(ORIG_PATH + '/' + file) as f:
        json_data = json.load(f)
        for paper in json_data:
            papers.append([len(papers), paper['abstract'],
                          paper['title'], paper['authors'], len(journals)-1])
            for author in paper['authors'].split(',' if conference in ['chi', 'etra'] else ';'):
                author = author.strip()
                if author not in authors:
                    authors[author] = len(authors)+1
                author_idx = authors[author]
                author_paper.append([author_idx, len(papers)-1])


authors = [[id, auth] for (auth, id) in authors.items()]
authors.insert(0, ['id', 'name'])

# print(journals)
# print(authors[::1000])
# print(author_paper[::1000])
# print(papers[::1000])

DATA_PATH = DIR + '/data'
with open(DATA_PATH + '/journals.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerows(journals)

with open(DATA_PATH + '/authors.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerows(authors)

with open(DATA_PATH + '/author_paper.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerows(author_paper)

with open(DATA_PATH + '/papers.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerows(papers)
