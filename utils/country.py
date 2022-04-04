import time
import requests
import os
import mydb
from utils import downloader
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

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    data = False
    while not data:
        response = requests.get(url=url, headers=headers, timeout=60)
        response.encoding = 'utf-8'
        data = response.json()['response']
        # print(json.dumps(data, indent=4))

    current = data['requests']['current']
    limit_day = data['requests']['limit_day']

    if current < limit_day:

        url = 'https://v3.football.api-sports.io/countries'

        headers = {
            'x-rapidapi-host': "v3.football.api-sports.io",
            'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"]
        }

        retries = 1
        success = False

        while not success and retries <= 5:
            try:
                response = requests.get(url=url, headers=headers, timeout=60)
                response.encoding = 'utf-8'
                success = response.ok
                if success and retries > 1:
                    logging.info("Solved!")
            except requests.exceptions.RequestException:
                wait = 30 * retries
                logging.info("Request-Error! Versuche es in {wait} Sekunden erneut.".format(wait=wait))
                time.sleep(wait)
                retries += 1
            else:
                errors = response.json()['errors']
                if not errors:
                    data = response.json()['response']

                    for d in data:
                        country = {'name': d['name'].replace('-', ' '), 'slug': slugify(d['name'].lower())}

                        if d['code'] is not None:
                            country['code2'] = d['code']

                        if d['flag'] is not None:
                            country['flag'] = 'country-flags/{}'.format(d['flag'].split('/')[-1])
                            downloader(d['flag'], country['flag'])

                        # print(country)
                        updateCountry(country)

    else:
        logging.info("Requests für heute aufgebraucht!")

    # print(json.dumps(data, indent=4))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    countries()
