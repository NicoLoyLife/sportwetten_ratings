import time
import json
import requests
import os
import mydb
from utils import downloader, abfrage
from slugify import slugify
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def main():
    # get all fixtures from db
    sql = 'SELECT * FROM sportwettenratings_fixture'

    fixtures = mydb.pullQuery(sql)
    counter = 0

    for f in fixtures:
        slug = slugify(f['slug'])
        mid = f['id']
        sql = """UPDATE sportwettenratings_fixture 
        SET slug='{}'
        WHERE id='{}'""".format(slug, mid)

        mydb.pushQuery(sql)

        counter += 1
        print("{}/{}".format(counter, len(fixtures)))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
