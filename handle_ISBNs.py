from pathlib import Path

path_tickets = Path("WELCM tickets.tsv")
path_isbns = Path("MCS_Ingestion_Tracker Test_Banks ISBN Sybex.txt")

tickets = list()
with open(path_tickets, 'r') as file_tickets:
    tickets = file_tickets.readlines()

with open(path_isbns, 'r') as file_isbns:
    for row in file_isbns.readlines():
        for ticket in tickets:
            if row[-7:-1] in ticket:
                print(row, end='')
                break
