import time
import requests
import os
import mydb
from utils import downloader, abfrage, status
import json
from slugify import slugify
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def updateCountry(data):
    columns = ', '.join(data.keys())
    values = []
    spalten = []
    for k, v in data.items():
        if v is not None:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))
        else:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')

    sql = '''INSERT INTO sportwettenratings_country ({columns})
    VALUES ({values})
    ON DUPLICATE KEY UPDATE {spalten}'''.format(columns=columns, values=', '.join(values), spalten=', '.join(spalten))

    mydb.pushQuery(sql)


# 1 call per day
def countries():
    url = "https://v3.football.api-sports.io/status"

    data = status(url)

    if data and len(data['response']) > 0:
        current = data['response']['requests']['current']
        limit_day = data['response']['requests']['limit_day']

        if current < limit_day:
            logging.info("Started with Countries!")
            url = 'https://v3.football.api-sports.io/countries'

            data = abfrage(url)

            if data and len(data['response']) > 0:

                for d in data['response']:
                    country = {'name': d['name'].replace('-', ' '), 'slug': slugify(d['name'].lower())}

                    if d['code'] is not None:
                        country['code2'] = d['code']

                    if d['flag'] is not None:
                        country['flag'] = 'country-flags/{}'.format(country['slug'])
                        downloader(d['flag'], country['flag'])

                    # print(country)
                    updateCountry(country)
                    print("Finished with country {}".format(country))

            logging.info("Finished with all Countries!")

        else:
            logging.info("Requests für heute aufgebraucht!")

        # print(json.dumps(data, indent=4))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    countries()
