from mydb import countFixtures
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.info("Anzahl Fixtures: {}".format(countFixtures()))
