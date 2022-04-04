import mysql.connector as mc
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def getDatabase():
    # set up database connection
    connection = None
    retries = 0
    while not connection:
        try:
            connection = mc.connect(
                host=os.environ["DB_HOST"],
                user=os.environ["DB_USER_2"],
                passwd=os.environ["DB_PASSWD_2"],
                db="sportwettenratings"
            )
            if retries > 0:
                logging.info("Solved!")

        except mc.Error as e:
            logging.info("Fehler bei der Datenbankverbindung. Versuche es in 30 Sekunden erneut.")
            print(e)
            time.sleep(30)
            retries += 1

    return connection


def pushQuery(sql):
    connection = getDatabase()
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        connection.commit()
    except mc.DatabaseError as e:
        print("Fehler bei der Abfrage:", sql)
        print(e)
    finally:
        cursor.close()
        connection.close()


def pullQuery(sql):
    connection = getDatabase()
    cursor = connection.cursor(dictionary=True)
    results = None
    try:
        cursor.execute(sql)
        results = cursor.fetchall()

    except mc.DatabaseError as e:
        print("Fehler bei der Abfrage:", sql)
        print(e)
    finally:
        cursor.close()
        connection.close()

    return results


def getCountry(name, code2=None):
    sql = '''
    SELECT * FROM sportwettenratings_country
    WHERE (name = '{name}' OR alt_name = '{name}')
    '''.format(name=name.replace('-', ' '))

    if code2 is not None:
        sql += ' AND code2 = "{code2}"'.format(code2=code2)

    country = pullQuery(sql)

    return country[0]


def getLeague(league_id):
    sql = '''
        SELECT * FROM sportwettenratings_league
        WHERE id = '{}'
        '''.format(league_id)

    league = pullQuery(sql)

    return league[0]


def getSeasons():
    sql = '''SELECT * FROM sportwettenratings_season
    ORDER BY last_updated, year DESC'''

    seasons = pullQuery(sql)

    return seasons


def getTeamToSeason(team_id, season_id):
    sql = '''SELECT * 
        FROM sportwettenratings_teamtoseason 
        WHERE team_id='{}' AND season_id='{}'
        '''.format(team_id, season_id)

    teamtoseason = pullQuery(sql)

    return teamtoseason[0]
