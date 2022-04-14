import time
import requests
import os
import mydb
from utils import downloader, abfrage, status
from slugify import slugify
import json
from queue import Queue
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def updateTeamToSeason(data):
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

    sql = '''INSERT INTO sportwettenratings_teamtoseason ({columns})
            VALUES ({values})
            ON DUPLICATE KEY UPDATE {spalten}'''.format(columns=columns, values=', '.join(values),
                                                        spalten=', '.join(spalten))

    mydb.pushQuery(sql)


def updateTeam(data):
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

    sql = '''INSERT INTO sportwettenratings_team ({columns}) 
            VALUES ({values}) 
            ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    mydb.pushQuery(sql)


class Worker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue
            season_id, year, league_id, country_id, counter, total_number = self.queue.get()

            try:
                url = "https://v3.football.api-sports.io/status"

                data = status(url)

                if data and len(data['response']) > 0:
                    current = data['response']['requests']['current']
                    limit_day = data['response']['requests']['limit_day']

                    if current < limit_day:

                        url = "https://v3.football.api-sports.io/teams?league={league_id}&season={year}".format(
                            league_id=league_id, year=year)

                        data = abfrage(url)

                        if data and len(data['response']) > 0:
                            for d in data['response']:
                                team = {'id': d['team']['id'], 'name': d['team']['name'],
                                        'national': d['team']['national'],
                                        'slug': slugify(d['team']['name']),
                                        'country_id': country_id}

                                if d['team']['code'] is not None:
                                    team['code'] = d['team']['code']

                                if d['team']['logo'] is not None:
                                    team['logo'] = 'team-logos/{}'.format(
                                        d['team']['logo'].split('/')[-1])
                                    downloader(d['team']['logo'], team['logo'])

                                teamtoseason = {'season_id': season_id, 'team_id': team['id']}

                                # print(team)
                                updateTeam(team)
                                updateTeamToSeason(teamtoseason)
                            print("Finished with {} from {}".format(counter, total_count))

                    else:
                        logging.info("Requests für heute aufgebraucht.")

            finally:
                self.queue.task_done()


# 1 call per day
def teams():
    url = "https://v3.football.api-sports.io/status"

    data = status(url)

    if data and len(data['response']) > 0:
        current = data['response']['requests']['current']
        limit_day = data['response']['requests']['limit_day']

        if current < limit_day:
            logging.info("Started with Teams!")
            queue = Queue()

            # create 10 worker threads
            for x in range(30):
                worker = Worker(queue)
                worker.daemon = True
                worker.start()

            # Put the tasks into the queue
            all_seasons = mydb.getSeasons()
            counter = 0

            for s in all_seasons:
                counter += 1
                season_id = s['id']
                year = s['year']
                league_id = s['league_id']
                country_id = mydb.getLeague(league_id)['country_id']

                queue.put((season_id, year, league_id, country_id, counter, len(all_seasons)))

            # Causes the main thread to wait for the queue to finish processing all the tasks
            queue.join()
            logging.info("Finished with all Teams!")

        else:
            logging.info("Requests für heute aufgebraucht!")

        # print(json.dumps(data, indent=4))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    teams()
