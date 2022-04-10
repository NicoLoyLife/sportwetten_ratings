import time
import json
import requests
import os
import mydb
from utils import downloader, abfrage
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def main():
    # Put the tasks into the queue
    url = "https://v3.football.api-sports.io/odds/mapping"

    paging = abfrage(url)
    matches = []

    if paging and len(paging['response']) > 0:
        # Anzahl der Ergebnisse
        results = paging['results']
        # Anzahl der Seiten ausgeben
        print(paging['paging']['total'], "Seiten")
        # Alle Seiten durchgehen
        for page in range(1, paging['paging']['total'] + 1):
            url = "https://v3.football.api-sports.io/odds/mapping?page={}".format(page)

            data = abfrage(url)
            print(json.dumps(data, indent=4))

            if data and len(data['response']) > 0:

                results_number = 0
                for d in data['response']:
                    match_id = d['fixture']['id']
                    results_number += 1

                    matches.append(match_id)
                    print(match_id, results_number, "/", results)

    print(len(matches))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
