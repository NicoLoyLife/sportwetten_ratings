import time
from json import JSONDecodeError
import requests
import os
import mydb
from utils import abfrage
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
            match_id = self.queue.get()

            try:
                url = "https://v3.football.api-sports.io/status"

                data = abfrage(url)

                if data and len(data['response']) > 0:
                    current = data['response']['requests']['current']
                    limit_day = data['response']['requests']['limit_day']

                    if current < limit_day:

                        url = "https://v3.football.api-sports.io/odds?fixture={}".format(match_id)

                        data = abfrage(url)
                        if data and len(data['response']) > 0:
                            try:
                                bookies = data['response'][0]['bookmakers']
                            except IndexError:
                                print(json.dumps(data, indent=4))
                            else:
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

                                            # print(quoten)
                                            updateOdds(quoten)

                    else:
                        logging.info("Requests für heute aufgebraucht.")

            finally:
                self.queue.task_done()


# 1 call per day
def odds_mapping():
    url = "https://v3.football.api-sports.io/status"

    data = abfrage(url)

    if data and len(data['response']) > 0:
        current = data['response']['requests']['current']
        limit_day = data['response']['requests']['limit_day']

        if current < limit_day:
            queue = Queue()

            # create 10 worker threads
            for x in range(10):
                worker = Worker(queue)
                worker.daemon = True
                worker.start()

            # Put the tasks into the queue
            url = "https://v3.football.api-sports.io/odds/mapping"
            print(url)

            paging = abfrage(url)

            if paging and len(paging['response']) > 0:
                for page in range(1, paging['paging']['total']+1):
                    url = "https://v3.football.api-sports.io/odds/mapping?page={}".format(page)

                    data = abfrage(url)

                    if data and len(data['response']) > 0:

                        for d in data['response']:
                            match_id = d['fixture']['id']

                            queue.put(match_id)

            # Causes the main thread to wait for the queue to finish processing all the tasks
            queue.join()
            logging.info("Finished!")

        else:
            logging.info("Requests für heute aufgebraucht!")

    # print(json.dumps(data, indent=4))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    odds_mapping()
