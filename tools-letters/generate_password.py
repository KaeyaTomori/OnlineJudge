import csv
import random

data = []
with open('2019-users.csv') as f:
    reader = csv.reader(f)
    data = [row for row in reader]

assert(len(data) > 0)
if len(data[0]) < 7:
    for i in range(len(data)):
        data[i].append(''.join(random.sample('ABCDEFGHIJKabcdefghijk', 8)))

with open('2019-users-with-pwd.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(data)