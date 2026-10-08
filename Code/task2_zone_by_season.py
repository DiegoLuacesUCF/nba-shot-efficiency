# =====================================================
# Task 2: Shot mix and make rates by zone, every season
#
# For each season and each of the dataset's seven court
# zones: the number of attempts, the make rate, the
# average point value of the shot (2 or 3), and the
# zone's share of that season's total attempts.
#
# This table is the entire input to the counterfactual
# decomposition in Task 3, and to Figures 2, 3, and 5.
#
# Output: zone_by_season.csv
# =====================================================

import sqlite3
import pandas as pd

db_path = "../Data/nba_shots.db"
con = sqlite3.connect(db_path)

query = """
SELECT
  CASE WHEN CAST(SUBSTR(GAME_ID, 4, 2) AS INTEGER) >= 90
       THEN 1900 + CAST(SUBSTR(GAME_ID, 4, 2) AS INTEGER)
       ELSE 2000 + CAST(SUBSTR(GAME_ID, 4, 2) AS INTEGER)
  END AS season,
  SHOT_ZONE_BASIC AS zone,
  COUNT(*) AS attempts,
  ROUND(AVG(SHOT_MADE_FLAG), 4) AS make_rate,
  ROUND(AVG(CASE WHEN SHOT_TYPE = '3PT Field Goal' THEN 3.0 ELSE 2.0 END), 4) AS pts_value
FROM shots
GROUP BY season, zone
ORDER BY season, attempts DESC
"""
zones = pd.read_sql(query, con)
con.close()

zones["share"] = zones["attempts"] / zones.groupby("season")["attempts"].transform("sum")
zones["share"] = zones["share"].round(4)

print(zones.to_string(index=False))
zones.to_csv("zone_by_season.csv", index=False)
