"""
Import necessary libraries
"""
import pandas as pd
import re
import warnings

from pandas.core.common import SettingWithCopyWarning
from Functions import build_team, get_info_players, career_stats, save_df_sql
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

# gathering information regarding roster
rosters = build_team()

all_nba_players = dict()
for team in rosters.keys():
    print("Gathering player info for team: " + team)
    all_nba_players[team] = get_info_players(rosters[team])

all_players_df = pd.DataFrame()
for team in all_nba_players.keys():
    team_df = pd.DataFrame.from_dict(all_nba_players[team], orient="index")
    team_df['team'] = team
    all_players_df = all_players_df.append(team_df)

print("========================================")
print("Following Players information is not available:")
career_stats_df = career_stats(all_players_df)
# saving career stats dataframe to csv file
career_stats_df.to_csv("NBA_player_stats_all_2020-2021.csv")

all_stats_df = all_players_df.join(career_stats_df)

print("========================================")
print("Print first three values from Salary field:")
print(all_stats_df['salary'].head(3))

# cleaning salary column
all_stats_df['salary'] = [int(re.sub(r'[^\d.]+', '', s)) if isinstance(s, str)
                          else s for s in all_stats_df['salary'].values]

# saving all stats dataframe to csv file
all_stats_df.to_csv("NBA_player_info_and_stats_joined_2020-2021.csv")

# Taking average stats and multiplying with Games Played to get absolute values
all_stats_df['time_played_season'] = all_stats_df['MIN'] * all_stats_df['GP']
all_stats_df['points_scored'] = all_stats_df['PTS'] * all_stats_df['GP']
all_stats_df['assists'] = all_stats_df['AST'] * all_stats_df['GP']
all_stats_df['rebounds'] = all_stats_df['REB'] * all_stats_df['GP']

# creating a dataframe with columns like salary, points, assists and rebounds
all_stats_df_final = all_stats_df[['id', 'salary', 'points_scored', 'assists', 'rebounds', 'time_played_season']]
all_stats_df_final = all_stats_df_final.fillna(0)

# calculating the ratio's to get scaled values
all_stats_df_final['points_scored_ratio'] = all_stats_df_final['points_scored'] / \
                                            all_stats_df_final['time_played_season']
all_stats_df_final['assists_ratio'] = all_stats_df_final['assists'] / all_stats_df_final['time_played_season']
all_stats_df_final['rebounds_ratio'] = all_stats_df_final['rebounds'] / all_stats_df_final['time_played_season']
all_stats_df_final = all_stats_df_final.fillna(0)

# filtering only players who have played more than 300 minutes in the entire season
all_stats_df_filtered = all_stats_df_final[all_stats_df_final['time_played_season'] >= 300]

"""
Defining a metric - weighted ratio, which gives 50% weightage to points_scored, 
25% to assists and 25% to rebounds. 
Compared this ratio with https://www.nbcsports.com/washington/wizards/2021-ranking-top-20-nba-players-right-now
 and 7 out of 10 players displayed falls in top 10 ranking
"""
all_stats_df_filtered['weighted_ratio'] = (1 / 2) * all_stats_df_filtered['points_scored_ratio'] + (1 / 4) * \
                                        all_stats_df_filtered['assists_ratio'] + (1 / 4) \
                                        * all_stats_df_filtered['rebounds_ratio']

print("=================================")
print("Top n Players are:")
print(all_stats_df_filtered.sort_values(by=['weighted_ratio'], ascending=False).head(10).index.tolist())

print("=================================")
print("Saving all stats dataframe to sql...")
save_df_sql(all_stats_df)
