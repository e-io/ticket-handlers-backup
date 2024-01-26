from pathlib import Path

from logger import logger

path_tickets = Path('WELCM tickets.tsv')
path_isbns = Path('MCS_Ingestion_Tracker Test_Banks ISBN Sybex.txt')

path_tickets_new = path_tickets.stem + '_handled' + path_tickets.suffix

tickets = []
with open(path_tickets) as file_tickets:
    tickets = file_tickets.readlines()

isbn_intersection = []

with open(path_isbns) as file_isbns:
    for row in file_isbns.readlines():
        for ticket in tickets:
            if row[-7:-1] in ticket:
                logger.debug(f"'{row.rstrip()}'")
                isbn_intersection.append(row.rstrip())
                break

with (
    open(path_tickets) as file_tickets,
    open(path_tickets_new, 'w') as file_tickets_new,
):
    rows = file_tickets.readlines()
    file_tickets_new.write(rows[0].rstrip() + '\t' + 'ISBN' + '\n')
    for row in rows[1:]:
        # logger.debug(row + '\n\n\n')
        tail = 'not for migration'
        for isbn in isbn_intersection:
            if isbn[-6:] in row:
                tail = isbn
                break
        new_row = row.rstrip() + '\t' + tail + '\n'
        logger.debug(new_row)
        file_tickets_new.write(new_row)
