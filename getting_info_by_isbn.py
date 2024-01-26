"""
This script returns information about a book by its ISBN with Google Books API.
How to run.
Example:
python3 getting_info_by_isbn.py 978-1-119-70711-0 9781394186921 9781394182930 9781119909378
general view:
<python> <path/to/script.py> <isbn1> <isbn2> ... <isbn100500>
example of isbn: "978-1-119-70711-0". It can be 10 digits or 13 digits. It can be with hyphens or without them.
"""

import csv
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pprint import pprint

import requests
from text_to_num import alpha2digit

from logger import logger

logger.setLevel(level='INFO')


class Book:
    def __init__(self):
        pass

    def print_info(self):
        print()
        info = self.__dict__
        pprint(info, sort_dicts=False, underscore_numbers=True)
        print()

    def create_folder_name(self):
        """
        :return: suggested folder name
        """
        author = self.authors[0].split(' ')[-1]
        tuple_ = (author, str(self.edition) + 'e', self.isbn) if self.edition is not None else (author, self.isbn)
        folder = '_'.join(tuple_)
        self.folder_name = folder
        logger.debug(folder)

    def search_edition(self, description: str):
        """------Searching edition----------"""
        match = re.search(r'([A-Za-z0-9_-]*)\s+edition', description)
        self.edition = match.group(1).lower() if match is not None else None
        logger.debug('edition is %s', self.edition)
        if self.edition is not None:
            logger.debug(self.edition)
            if self.edition == 'second':
                self.edition = 2
            elif self.edition == 'third':
                self.edition = 3
            else:
                self.edition = alpha2digit(self.edition, 'en')
                match_num = re.search('([0-9]*)', self.edition)
                if match_num is not None:
                    num = match_num.group(1)
                    if len(num) != 0:
                        self.edition = int(num)
                    else:
                        self.edition = None
        # ---------------------


def get_info_by_isbn(isbn: str):
    url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:' + isbn

    response = requests.get(url, timeout=15)

    if not bool(response):
        msg = "Answer wasn't gotten. Response: " + response
        raise Exception(msg)

    json_all = response.json()
    if json_all['totalItems'] == 0:
        logger.warning('There is no information on server about book with ISBN %s. \nBook is skipped.', isbn)
        return 0

    if json_all['totalItems'] > 1:
        logger.warning(
            "Book with ISBN %s has several 'items'. Book is not skipped. \n"
            'First item is taken, because usually items are identical.\n',
            isbn,
        )
        # logger.debug('\n-------\n%s\n-------\n', json.dumps(json_all['items'], indent=2))  # to show all items inside
        # return 0

    data_all = json_all['items'][0]
    info = data_all['volumeInfo']

    # print all json
    logger.debug('\n-------\n%s\n-------\n', json.dumps(data_all, indent=2))

    book = Book()

    def add_field(dict_: dict, field: str):
        return dict_[field] if field in dict_ else None

    book.isbn = isbn  # or info['industryIdentifiers'][0 <or> 1]['identifier']
    book.authors = info['authors']
    book.title = info['title']
    book.subtitle = add_field(info, 'subtitle')
    book.publisher = info['publisher']

    description = (info['description'] + ' ' + data_all['searchInfo']['textSnippet']).lower().replace('canadian', '')
    logger.debug(description)

    book.search_edition(description)

    book.category = info['categories'][0]
    book.published_date = info['publishedDate']
    if 'pageCount' in info and info['pageCount'] > 0:
        book.page_count = info['pageCount']
    else:
        book.page_count = add_field(info, 'printedPageCount')
    book.text_snippet = data_all['searchInfo']['textSnippet']

    book.thumbnail = info['imageLinks']['thumbnail']
    book.info_link = info['infoLink']
    book.full_json = data_all['selfLink']

    book.rating = add_field(info, 'averageRating')
    book.ratings_count = add_field(info, 'ratingsCount')
    book.create_folder_name()

    if logger.level == 'DEBUG':
        book.print_info()

    return book


def create_tsv(results: list):
    books = [result for result in results if result != 0]

    output = Path('output')
    output.mkdir(exist_ok=True)
    path = output / 'Products.tsv'

    with (
        open(path, 'w+') as file,
        # remove this and related lines (`# Sybex`) below if you use script for other purposes
        open('Tickets_Sybex.tsv') as file_tickets,  # Sybex
    ):
        writer = csv.writer(file, delimiter='\t')
        header = [
            'isbn',
            'published',
            'edition (supposed)',
            'pages',
            'publisher',
            'authors',
            'title',
            'subtitle',
            'category',
            'full JSON',
            'info link',
            '# of tickets',
        ]

        tickets = ' '.join(file_tickets.readlines())  # Sybex

        writer.writerow(header)
        for book in books:
            last6 = book.isbn[-6:]  # Sybex
            n = tickets.count(last6)  # Sybex

            row = [
                book.isbn,
                book.published_date,
                book.edition,
                book.page_count,
                book.publisher,
                ', '.join(book.authors),
                book.title,
                book.subtitle,
                book.category,
                book.full_json,
                book.info_link,
                n,  # Sybex
            ]
            writer.writerow(row)


def main(args: list):
    logger.info('Work started')

    with ThreadPoolExecutor() as pool:
        results = pool.map(get_info_by_isbn, args)

    create_tsv(results)

    logger.info('Work completed')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        msg = 'Not enough arguments. Pass ISBN(s) as arguments.'
        raise Exception(msg)
    main(sys.argv[1:])
