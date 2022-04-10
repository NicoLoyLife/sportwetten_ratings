import json
import requests
import mydb
from utils import abfrage
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def updateBookmaker(data):
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

    sql = '''INSERT INTO sportwettenratings_bookmaker ({columns})
        VALUES ({values})
        ON DUPLICATE KEY UPDATE {spalten}'''.format(columns=columns, values=', '.join(values),
                                                    spalten=', '.join(spalten))

    mydb.pushQuery(sql)


# 1 call per day.
def bookmakers():
    url = "https://v3.football.api-sports.io/status"

    data = abfrage(url)

    if data and len(data['response']) > 0:
        current = data['response']['requests']['current']
        limit_day = data['response']['requests']['limit_day']

        if current < limit_day:
            logging.info("Started with Bookmakers!")
            url = "https://v3.football.api-sports.io/odds/bookmakers"

            data = abfrage(url)

            if data and len(data['response']) > 0:
                for d in data['response']:
                    bookie = {'id': d['id'], 'name': d['name']}

                    print(bookie)
                    updateBookmaker(bookie)

            logging.info("Finished with all Bookmakers!")
        else:
            logging.info("Requests für heute aufgebraucht.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bookmakers()
