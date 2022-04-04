import time
from json import JSONDecodeError

import requests
import os
import mydb
from slugify import slugify
import json
from queue import Queue
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def updateOdds(data):
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

    sql = '''INSERT INTO sportwettenratings_odd ({columns})
                VALUES ({values})
                ON DUPLICATE KEY UPDATE {spalten}'''.format(columns=columns, values=', '.join(values),
                                                            spalten=', '.join(spalten))

    mydb.pushQuery(sql)


class Worker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue
            season_id, year, league_id = self.queue.get()

            try:
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

                    url = "https://v3.football.api-sports.io/players?season={}&league={}".format(year, league_id)

                    headers = {
                        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
                        'x-rapidapi-host': 'v3.football.api-sports.io'
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
                            try:
                                errors = response.json()['errors']
                            except JSONDecodeError:
                                print(json.dumps(response.json(), indent=4))
                            else:
                                if not errors:
                                    data = response.json()['response']

                                    bookies = data[0]['bookmakers']

                                    for bookie in bookies:
                                        bookmaker_id = bookie['id']
                                        bets = bookie['bets']

                                        for bet in bets:
                                            bet_id = bet['id']
                                            values = bet['values']

                                            for v in values:
                                                quoten = {'match_id': match_id, 'bookmaker_id': bookmaker_id,
                                                          'bet_id': bet_id, 'value': v['value'],
                                                          'odd': v['odd']}

                                                print(quoten)
                                                updateOdds(quoten)

                else:
                    logging.info("Requests für heute aufgebraucht.")

            finally:
                self.queue.task_done()


# 1 call per day
def players():
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
        queue = Queue()

        # create 10 worker threads
        for x in range(1):
            worker = Worker(queue)
            worker.daemon = True
            worker.start()

            # Put the tasks into the queue
            all_seasons = mydb.getSeasons()

            for s in all_seasons:
                season_id = s['id']
                year = s['year']
                league_id = s['league_id']

                queue.put((season_id, year, league_id))

            # Causes the main thread to wait for the queue to finish processing all the tasks
            queue.join()

    else:
        logging.info("Requests für heute aufgebraucht!")

    # print(json.dumps(data, indent=4))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    players()
