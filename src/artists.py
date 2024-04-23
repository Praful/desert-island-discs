
"""
=============================================================================
File: artists.py
Description: Create single list of artists from already created output. Used 
             in Excel output spreadsheet to find most occurring artists.
Author: Praful https://github.com/Praful/desert-island-discs
Licence: GPL v3
=============================================================================
"""

import csv
import sys

# print(sys.argv)

ARTIST_COLUMNS = 8
count = 0
with open(sys.argv[1], newline='') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        for n in range(1, ARTIST_COLUMNS + 1):
            column = f'Artist {n}'
            if row[column] is not None and row[column].strip() != '':
                print(row[column])
                count += 1

    print(f'Total rows: {count}')
