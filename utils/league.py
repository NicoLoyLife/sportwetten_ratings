import time
import requests
import os
import mydb
from utils import downloader
from slugify import slugify
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def updateSeason(data):
    columns = ', '.join(data.keys())
    spalten = []
    values = []
    for k, v in data.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        elif v is True:
            spalten.append('''{}=1'''.format(k))
            values.append('''1''')
        elif v is False:
            spalten.append('''{}=0'''.format(k))
            values.append('''0''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO sportwettenratings_season ({columns}) 
        VALUES ({values}) 
        ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    mydb.pushQuery(sql)


def updateLeague(data):
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

    sql = '''INSERT INTO sportwettenratings_league ({columns})
        VALUES ({values})
        ON DUPLICATE KEY UPDATE {spalten}'''.format(columns=columns, values=', '.join(values),
                                                    spalten=', '.join(spalten))

    mydb.pushQuery(sql)


# 1 call per hour
def leagues():
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

    current = data['requests']['current']
    limit_day = data['requests']['limit_day']

    if current < limit_day:

        url = 'https://v3.football.api-sports.io/leagues'

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
                        league = {'id': d['league']['id'], 'name': d['league']['name'], 'type': d['league']['type'],
                                  'slug': slugify(d['league']['name'])}

                        if d['league']['logo'] is not None:
                            league['logo'] = 'league-logos/{}'.format(d['league']['logo'].split('/')[-1])
                            downloader(d['league']['logo'], league['logo'])

                        league['country_id'] = mydb.getCountry(d['country']['name'], d['country']['code'])['id']

                        # print(league)
                        updateLeague(league)

                        seasons = d['seasons']

                        for s in seasons:
                            season = {'year': s['year'], 'start': s['start'], 'end': s['end'],
                                      'current': s['current'], 'league_id': d['league']['id'],
                                      'slug': slugify(str(s['year']))}

                            # print(season)
                            updateSeason(season)

    else:
        logging.info("Requests für heute aufgebraucht!")

    # print(json.dumps(data, indent=4))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    leagues()
