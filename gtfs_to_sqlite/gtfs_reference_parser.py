import re

import requests
from bs4 import BeautifulSoup

from gtfs_to_sqlite.database import Column, Table, Database


def parse_reference():
    url = "https://developers.google.com/transit/gtfs/reference"
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    table_headings = soup.select('h3[id]')

    # manually remove unnecessary tables
    table_headings.pop()
    table_headings.pop()

    table_names: list[str] = []
    i: int
    for i in range(len(table_headings)):
        table_names.append(re.sub('(.*?)\.txt', '\g<1>', table_headings[i].text))

    tables = soup.select('table > tbody')

    # remove manually unnecessary tables
    tables.pop(0)
    tables.pop(4)
    tables.pop()
    tables.pop()
    tables.pop()
    tables.pop()

    final_tables: dict[str, Table] = {}

    for i in range(len(tables)):
        columns: dict[str, Column] = {}
        rows = tables[i].findAll('tr')
        for row in rows:
            tds = row.findAll('td')
            column_name = tds[0].text
            column_type = tds[1].text
            requirement = tds[2].text
            column_name = re.sub('^stop_id$', 'rowid', column_name)
            columns[column_name] = Column(column_name=column_name, column_type=column_type, requirement=requirement)
        final_tables[table_names[i]] = Table(table_names[i], columns)

    return Database("gtfs", final_tables)
