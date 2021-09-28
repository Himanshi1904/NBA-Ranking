"""
Import necessary libraries
"""
from itertools import chain
import sqlalchemy as db
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import json
from time import sleep


def build_team() -> dict[str, str]:
    """
    This function access espn's nba page and extract names of each roster. For each roster name, URL of the team page
    is created. :return:
    """
    f = urlopen('https://www.espn.com/nba/teams')
    teams_source = f.read().decode('utf-8')
    teams = dict(re.findall("www\.espn\.com/nba/team/_/name/(\w+)/(.+?)\",", teams_source))
    roster_urls = []
    for key in teams.keys():
        roster_urls.append('https://www.espn.com/nba/team/roster/_/name/' + key + '/' + teams[key])
        teams[key] = str(teams[key])
    return dict(zip(teams.values(), roster_urls))


def get_info_players(roster_url) -> dict:
    """
    Function retrieves info such as age, height salary etc for each player within a roster.
    :param roster_url:
    :return:
    """
    f = urlopen(roster_url)
    roster_source = f.read().decode('utf-8')
    sleep(0.6)
    player_regex = '\{\"name\"\:\"(\w+\s\w+)\",\"href\"\:\"https?\://www\.espn\.com/nba/player/.*?\",(.*?)\}'
    player_info = re.findall(player_regex, roster_source)
    player_dict = dict()
    for player in player_info:
        player_dict[player[0]] = json.loads("{" + player[1] + "}")
    return player_dict


def career_stats(all_players_df) -> pd.DataFrame:
    """
    Steps involved in this function: 1. Data Frame created for storing stats for each player 2. For each player,
    espn webpage is parsed and career stats average is retrieved 3.Some of the stats contain non-numerical symbols (
    example: - 3PT means 3-Point Field Goals Made-Attempted Per Game, so 5.3-12.7 is split as 3PTM - 5.3 and
    3PTA - 12.7 similarly is done for FG and FT as well.

    :return:
    """
    career_stats_df = pd.DataFrame(
        columns=["GP", "GS", "MIN", "FGM", "FGA", "FG%", "3PTM", "3PTA", "3P%", "FTM", "FTA", "FT%", "OR", "DR", "REB",
                 "AST", "BLK", "STL", "PF", "TO", "PTS"])
    for player_index in all_players_df.index:
        url = "https://www.espn.com/nba/player/stats/_/id/" + str(all_players_df.loc[player_index]['id'])
        f = urlopen(url)
        soup = BeautifulSoup(f, 'html.parser')
        sleep(0.5)
        try:
            content = soup.find_all('div', class_='ResponsiveTable ResponsiveTable--fixed-left pt4')[0]
            year = []
            scores = []
            tr = content.find_all('tr', class_='Table__TR Table__TR--sm Table__even')
            for i, point in enumerate(tr):
                td = point.find_all('td')
                i = 0
                scr = []
                for element in td:
                    if len(td) <= 2:
                        year.append(td[i].text)
                    elif len(td) >= 2:
                        scr.append(td[i].text)
                    i += 1
                scores.append(scr)
            career_info = list(chain.from_iterable([i.split("-") for i in scores[-2]]))
            career_info = list(map(float, career_info))
            career_stats_df = career_stats_df.append(
                pd.Series(career_info, index=career_stats_df.columns, name=player_index))

        except Exception:
            # if no career stats were returned, the player has not played any game
            print(player_index + " has no info, ", end="")
    return career_stats_df


def save_df_sql(all_stats_df):
    """
    Saves dataframe to in-memory database - sqlite
    :param all_stats_df:
    :return:
    """
    engine = db.create_engine('sqlite:///save_dataframe.db', echo=False)
    sqlite_connection = engine.connect()
    sqlite_table = "all_players_stats"
    all_stats_df.to_sql(sqlite_table, sqlite_connection, if_exists='fail')
    sqlite_connection.close()
