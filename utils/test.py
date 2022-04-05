import time
import json
import requests
import os
import mydb
from utils import downloader
import logging
import http.client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def main():
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"]
    }

    conn.request("GET", "/status", headers=headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
