# =====================================================
# Task 1: Season assignment and season summary table
#
# Season is decoded from GAME_ID rather than the calendar
# date, because calendar filtering misclassifies the two
# pandemic-disrupted seasons (2019-20 ended in October
# 2020; 2020-21 began in December). Digit 3 of GAME_ID
# gives the game type (2 = regular season); digits 4 and
# 5 give the season's starting year.
#
# Output: season_summary.csv, one row per season with
# points per attempt and three-point share, the two
# headline series in Figure 1.
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
  COUNT(*) AS attempts,
  SUM(CASE WHEN SHOT_TYPE = '3PT Field Goal' THEN 1 ELSE 0 END) AS attempts_3pt,
  SUM(CASE WHEN SHOT_TYPE = '3PT Field Goal' THEN 3 * SHOT_MADE_FLAG
           ELSE 2 * SHOT_MADE_FLAG END) AS points,
  COUNT(DISTINCT GAME_ID) AS games,
  MIN(GAME_DATE) AS first_game,
  MAX(GAME_DATE) AS last_game,
  SUM(CASE WHEN SUBSTR(GAME_ID, 3, 1) <> '2' THEN 1 ELSE 0 END) AS odd_rows
FROM shots
GROUP BY season
ORDER BY season
"""
summary = pd.read_sql(query, con)
con.close()

# The two headline series
summary["ppa"] = (summary["points"] / summary["attempts"]).round(4)
summary["share_3pt"] = (summary["attempts_3pt"] / summary["attempts"]).round(4)

print(summary.to_string(index=False))
summary.to_csv("season_summary.csv", index=False)
