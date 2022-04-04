import time
import json
import requests
import os
import mydb
from utils import downloader
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def main():
    league_id = 78
    year = 2021
    season_id = 68
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
            errors = response.json()['errors']
            if not errors:
                paging = response.json()['paging']['total']

                for page in range(1, paging+1):
                    url = "https://v3.football.api-sports.io/players?season={}&league={}&page={}".format(
                        year, league_id, page)

                    headers = {
                        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
                        'x-rapidapi-host': 'v3.football.api-sports.io'
                    }

                    response = requests.get(url=url, headers=headers, timeout=60)
                    response.encoding = 'utf-8'
                    data = response.json()['response']

                    for d in data:
                        player = {'id': d['player']['id'], 'name': d['player']['name'],
                                  'firstname': d['player']['firstname'], 'lastname': d['player']['lastname'],
                                  'age': d['player']['age'], 'birth_date': d['player']['birth']['date'],
                                  'birth_place': d['player']['birth']['place'],
                                  'birth_country': d['player']['birth']['country'],
                                  'nationality': d['player']['nationality'], 'height': d['player']['height'],
                                  'weight': d['player']['weight'], 'injured': d['player']['injured'],
                                  'photo': 'player-photos/{}'.format(d['player']['photo'].split('/')[-1])}

                        downloader(d['player']['photo'], player['photo'])

                        playerteamseason = {'player_id': player['id'],
                                            'team_id': mydb.getTeamToSeason(d['statistics']['team']['id'], season_id)}

                        print(player)
                        print(playerteamseason)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
