import time
import requests
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def downloader(url, dateiname):
    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    retries = 1
    success = False

    while not success and retries <= 5:
        try:
            response = requests.get(url=url, headers=headers, allow_redirects=True, timeout=60)
            response.encoding = 'utf-8'
            success = response.ok
            if success and retries > 1:
                logging.info("Solved!")
        except requests.exceptions.RequestException:
            wait = 30 * retries
            logging.info("Request-Error beim Downloaden! Versuche es in {wait} Sekunden erneut.".format(wait=wait))
            time.sleep(wait)
            retries += 1
        else:
            open(dateiname, 'wb').write(response.content)
