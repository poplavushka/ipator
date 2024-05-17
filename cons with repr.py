import csv
with open('sounds.csv', 'r') as f:
    reader = csv.read(f)
    print(len(row[1]))
    next(reader)
    representation = {row[0] : row[37] for row in reader}
