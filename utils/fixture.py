import time
from datetime import datetime, date
import requests
import os
import mydb
from utils import abfrage, status
import json
from queue import Queue
from threading import Thread
import logging

# 1 call per minute for the leagues, teams, fixtures
# who have at least one fixture in progress
# otherwise 1 call per day.

# You can also retrieve all the events of the fixtures in progress
# thanks to the endpoint fixtures?live=all

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def seasonLastUpdated(season_id, datum):
    sql = '''UPDATE sportwettenratings_season SET last_updated='{}' WHERE id='{}'
    '''.format(datum, season_id)

    mydb.pushQuery(sql)


def updateStats(data):
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

    sql = '''INSERT INTO sportwettenratings_statistic ({columns})
                    VALUES ({values})
                    ON DUPLICATE KEY UPDATE {spalten}'''.format(columns=columns, values=', '.join(values),
                                                                spalten=', '.join(spalten))

    mydb.pushQuery(sql)


def updateFixture(data):
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

    sql = '''INSERT INTO sportwettenratings_fixture ({columns})
                VALUES ({values})
                ON DUPLICATE KEY UPDATE {spalten}'''.format(columns=columns, values=', '.join(values),
                                                            spalten=', '.join(spalten))

    mydb.pushQuery(sql)


def getTeam(team_id):
    sql = '''
            SELECT * FROM sportwettenratings_team
            WHERE id = '{}'
            '''.format(team_id)

    team = mydb.pullQuery(sql)

    return team[0]


def statistics(match_id):
    url = "https://v3.football.api-sports.io/fixtures/statistics?fixture={}".format(match_id)

    statistic = abfrage(url)

    if statistic and len(statistic['response']) > 0:

        stats = {'id': match_id}

        hometeam = statistic['response'][0]['statistics']
        for t in hometeam:
            if t['value'] is not None:
                name = t['type'].replace(' ', '_').replace(
                    '%', 'percent').lower() + '_h'
                if t['type'] == 'Ball Possession' or \
                        t['type'] == 'Passes %':
                    stats[name] = int(t['value'].replace('%', '')) / 100
                else:
                    stats[name] = t['value']

        awayteam = statistic['response'][1]['statistics']
        for t in awayteam:
            if t['value'] is not None:
                name = t['type'].replace(' ', '_').replace(
                    '%', 'percent').lower() + '_a'
                if t['type'] == 'Ball Possession' \
                        or t['type'] == 'Passes %':
                    stats[name] = int(t['value'].replace('%', '')) / 100
                else:
                    stats[name] = t['value']

        # print(stats)
        updateStats(stats)


def fixtures(season_id, year, league_id, counter, total_count):
    print("Started with season_id {}".format(season_id))
    url = '''https://v3.football.api-sports.io/fixtures?league={}&season={}&timezone=Europe/Berlin'''. \
        format(league_id, year)

    data = abfrage(url)

    if data and len(data['response']) > 0:
        print(data['results'], "Results in season", season_id)
        for d in data['response']:
            match_id = d['fixture']['id']

            fixture = {'id': match_id,
                       'date': datetime.fromtimestamp(d['fixture']['timestamp']),
                       'status_long': d['fixture']['status']['long'],
                       'status_short': d['fixture']['status']['short'], 'season_id': season_id,
                       'round': d['league']['round'],
                       'homescore_ht': d['score']['halftime']['home'],
                       'awayscore_ht': d['score']['halftime']['away'],
                       'homescore_ft': d['score']['fulltime']['home'],
                       'awayscore_ft': d['score']['fulltime']['away'],
                       'homescore_et': d['score']['extratime']['home'],
                       'awayscore_et': d['score']['extratime']['away'],
                       'homescore_p': d['score']['penalty']['home'],
                       'awayscore_p': d['score']['penalty']['away']}

            try:
                fixture['slug'] = getTeam(d['teams']['home']['id'])['name'] + "-" + \
                                  getTeam(d['teams']['away']['id'])['name'] + "-" + \
                                  str(d['fixture']['id'])
                fixture['hometeam_id'] = mydb.getTeamToSeason(
                    d['teams']['home']['id'], season_id)['id']
                fixture['awayteam_id'] = mydb.getTeamToSeason(
                    d['teams']['away']['id'], season_id)['id']
            except IndexError:
                print(d)

            # print(fixture)
            updateFixture(fixture)

            # Statistics holen
            statistics(match_id)

        seasonLastUpdated(season_id, date.today())
        print("Finished with {} from {}".format(counter, total_count))


class Worker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue
            season_id, year, league_id, counter, total_count = self.queue.get()

            try:
                fixtures(season_id, year, league_id, counter, total_count)

            finally:
                self.queue.task_done()


def main():
    url = "https://v3.football.api-sports.io/status"

    data = status(url)

    if data and len(data['response']) > 0:
        current = data['response']['requests']['current']
        limit_day = data['response']['requests']['limit_day']

        if current < limit_day:
            logging.info("Started with Fixtures!")
            queue = Queue()

            # create 10 worker threads
            for x in range(20):
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

                queue.put((season_id, year, league_id, counter, len(all_seasons)))

            # Causes the main thread to wait for the queue to finish processing all the tasks
            queue.join()
            logging.info("Finished with all Fixtures!")

        else:
            logging.info("Requests für heute aufgebraucht!")

    # print(json.dumps(data, indent=4))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
