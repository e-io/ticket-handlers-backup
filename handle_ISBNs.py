"""
How to run?
python3 handle_ISBNs.py

result is in output/ISBNs_TB_import_Sybex_with_issues.tsv

Add those ISBNs as command line arguments for the next script - getting_info_by_isbn.py
"""

from pathlib import Path

from logger import logger

path_isbns = Path('ISBNs_TB_import_Sybex.tsv')
path_tickets = Path('Tickets_Sybex.tsv')

output = Path('output')
output.mkdir(exist_ok=True)

path_isbns_intersection = output / (path_isbns.stem + '_with_issues' + path_isbns.suffix)
path_tickets_new = output / (path_tickets.stem + '_handled' + path_tickets.suffix)

with open(path_tickets) as file_tickets:
    tickets = file_tickets.readlines()

isbn_intersection = []
with (
    open(path_isbns) as file_isbns,  # default mode for 'open' is always 'r' (reading).
    open(path_isbns_intersection, 'w+') as file_isbns_new,
):
    file_isbns_new.write('ISBN\n')
    for row in file_isbns.readlines()[1:]:
        for ticket in tickets:
            if row[-7:-1] in ticket:
                file_isbns_new.write(row.rstrip() + '\n')
                isbn_intersection.append(row.rstrip())
                break

logger.info("file %s is ready", path_isbns_intersection)

with (
    open(path_tickets) as file_tickets,
    open(path_tickets_new, 'w+') as file_tickets_new,
):
    rows = file_tickets.readlines()
    file_tickets_new.write(rows[0].rstrip() + '\t' + 'ISBN' + '\n')
    for row in rows[1:]:
        tail = 'not for migration'
        for isbn in isbn_intersection:
            if isbn[-6:] in row:
                tail = isbn
                break
        new_row = row.rstrip() + '\t' + tail + '\n'
        file_tickets_new.write(new_row)

logger.info("file %s is ready", path_tickets_new)
