import time
from json import JSONDecodeError
import json
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

    retries = 0
    success = False

    while not success and retries <= 5:
        try:
            response = requests.get(url=url, headers=headers, timeout=60)
            response.encoding = 'utf-8'
            response.raise_for_status()
            success = response.ok
            if success and retries > 0:
                logging.info("Solved! {}".format(response.status_code))
            open(dateiname, 'wb').write(response.content)
        except requests.exceptions.HTTPError as errh:
            retries += 1
            wait = 30 * retries
            logging.info("HTTPError beim Downloaden: {0} in Versuch Nummer {1}".format(errh, retries))
            time.sleep(wait)
        except requests.exceptions.ConnectionError as errc:
            retries += 1
            wait = 30 * retries
            logging.info("ConnectionError beim Downloaden: {0} in Versuch Nummer {1}".format(errc, retries))
            time.sleep(wait)
        except requests.exceptions.Timeout as errt:
            retries += 1
            wait = 30 * retries
            logging.info("Timeout beim Downloaden: {0} in Versuch Nummer {1}".format(errt, retries))
            time.sleep(wait)
        except requests.exceptions.RequestException as err:
            retries += 1
            wait = 30 * retries
            logging.info("RequestException beim Downloaden: {0} in Versuch Nummer {1}".format(err, retries))
            time.sleep(wait)


def abfrage(url):
    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    retries = 0
    success = False

    while not success:
        try:
            response = requests.get(url=url, headers=headers, timeout=60)
            response.encoding = 'utf-8'
            response.raise_for_status()
            success = response.ok
            if success and retries > 0:
                logging.info("Solved! {}".format(response.status_code))
            try:
                fehler = response.json()['errors']
                if not fehler:
                    data = response.json()
                    return data
                else:
                    logging.info(fehler)
            except JSONDecodeError as err:
                logging.info(response.status_code)
                logging.info("JSONDecodeError: {0}".format(err))
                logging.info(response.content)
        except requests.exceptions.HTTPError as errh:
            retries += 1
            wait = 30 * retries
            logging.info("HTTPError: {0} in Versuch Nummer {1}".format(errh, retries))
            time.sleep(wait)
        except requests.exceptions.ConnectionError as errc:
            retries += 1
            wait = 30 * retries
            logging.info("ConnectionError: {0} in Versuch Nummer {1}".format(errc, retries))
            time.sleep(wait)
        except requests.exceptions.Timeout as errt:
            retries += 1
            wait = 30 * retries
            logging.info("Timeout: {0} in Versuch Nummer {1}".format(errt, retries))
            time.sleep(wait)
        except requests.exceptions.RequestException as err:
            retries += 1
            wait = 30 * retries
            logging.info("RequestException: {0} in Versuch Nummer {1}".format(err, retries))
            time.sleep(wait)

    # logging.info("Problem bei: {}".format(url))
