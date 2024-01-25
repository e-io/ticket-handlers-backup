"""
This script returns information about a book by its ISBN with Google Books API.
How to run.
Example:
python3 getting_info_by_isbn.py 978-1-119-70711-0
general view:
<python> <path/to/script.py> <isbn1> <isbn2> ... <isbn100500>
example of isbn: "978-1-119-70711-0". It can be 10 digits or 13 digits. It can be with hyphens or without them.
"""

import re
import sys
from pathlib import Path
from pprint import pprint

import requests
from text_to_num import alpha2digit

read_from = Path("Prioritized_products_containing_issues.tsv")

class Book:

    def __init__(self):
        pass

    def print_info(self):
        info = self.__dict__
        print()
        pprint(info, sort_dicts=False, underscore_numbers=True)
        print()

        """
        print("ISBN:", '\n\t', isbn, sep='')
        print("Authors:")
        for author in book.authors:
            print('\t', author)
        print("Title:")
        print('\t', title)
        print("Published on:")
        print('\t', publishedDate)
        print("Short description:", '\n\t', short_description, sep='')
        print("Number of pages:", '\n\t', pages, sep='')

        for item, data in info_to_print:
            print(item, '\n\t', data, sep='')
        """

    def folder_name(self):
        author = self.authors[0].split(' ')[-1]
        if self.edition is not None:
            tuple_ = (author, str(self.edition) + 'e', self.isbn)
        else:
            tuple_ = (author, self.isbn)
        folder = '_'.join(tuple_)
        print(folder)


def get_info_by_isbn(isbn: str):
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn

    response = requests.get(url)

    if not bool(response):
        raise Exception("Answer wasn't gotten. Response:", response)

    json_all = response.json()
    if json_all['totalItems'] == 0:
        print("There is no information on server about book with ISBN", isbn, ". \nBook is skipped.")
        return 0
    elif json_all['totalItems'] > 1:
        print("Book with ISBN", isbn, "has several 'items'. \nBook is skipped.")
        return 0

    data_all = json_all['items'][0]
    info = data_all['volumeInfo']

    # print all json
    # print("-------\n", json.dumps(data_all, indent=2), "\n-------\n", sep='', end='')

    book = Book()

    def add_field(dict_: dict, field: str):
        return dict_[field] if field in dict_ else None

    book.isbn = info['industryIdentifiers'][0]['identifier']
    book.authors = info['authors']
    book.title = info['title']
    description = (info['description'] + ' ' + data_all['searchInfo']['textSnippet']).lower().replace('canadian', '')
    print(description)
    match = re.search("([A-Za-z0-9_-]*)\s+edition", description)
    book.edition = match.group(1).lower() if match is not None else None
    print('edition is ', book.edition)
    if book.edition is not None:
        print(book.edition)
        if book.edition == 'second':
            book.edition = 2
        elif book.edition == 'third':
            book.edition = 3
        else:
            book.edition = alpha2digit(book.edition, 'en')
            match_num = re.search("([0-9]*)", book.edition)
            if match_num is not None:
                num = match_num.group(1)
                if len(num) != 0:
                    book.edition = int(num)
                else:
                    book.edition = None

    book.category = info['categories'][0]
    book.published_date = info['publishedDate']
    book.page_count = add_field(info, 'pageCount')
    book.text_snippet = data_all['searchInfo']['textSnippet']

    book.thumbnail = info["imageLinks"]['thumbnail']

    book.rating = add_field(info, 'averageRating')
    book.ratings_count = add_field(info, 'ratingsCount')

    book.print_info()
    book.folder_name()


def main(args: list):
    for arg in args:
        get_info_by_isbn(arg)


if __name__ == "__main__":
    main(sys.argv[1:])