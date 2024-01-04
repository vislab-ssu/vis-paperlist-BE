import csv
import os

FILE_PATH = os.path.realpath(__file__)
DIR = os.path.dirname(FILE_PATH)

max_len = [0 for _ in range(8)]

with open(DIR + "/papers.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader, None)
    for row in reader:
        for idx in range(8):
            if max_len[idx] < len(row[idx]):
                max_len[idx] = len(row[idx])

print(header)
print(max_len)
