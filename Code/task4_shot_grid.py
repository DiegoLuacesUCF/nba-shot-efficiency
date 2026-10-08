# =====================================================
# Task 4: Shot location grid
#
# Bins each shot's on-court location (LOC_X, LOC_Y, given
# in tenths of a foot) into one-foot grid cells, for the
# two endpoint seasons only. This is the raw material for
# the shot density comparison in Figure 4.
#
# Output: shot_grid.csv
# =====================================================

import sqlite3
import pandas as pd

db_path = "../Data/nba_shots.db"
con = sqlite3.connect(db_path)

query = """
SELECT
  CAST(SUBSTR(GAME_ID, 4, 2) AS INTEGER) AS yy,
  CAST(ROUND(LOC_X / 10.0) AS INTEGER) AS x_ft,
  CAST(ROUND(LOC_Y / 10.0) AS INTEGER) AS y_ft,
  COUNT(*) AS attempts,
  SUM(SHOT_MADE_FLAG) AS made
FROM shots
WHERE SUBSTR(GAME_ID, 4, 2) IN ('97', '21') AND LOC_Y <= 350
GROUP BY yy, x_ft, y_ft
"""
grid = pd.read_sql(query, con)
con.close()

grid["season"] = grid["yy"].map({97: 1997, 21: 2021})
grid = grid[["season", "x_ft", "y_ft", "attempts", "made"]]

print("Grid cells:", len(grid))
print(grid.groupby("season")["attempts"].sum().to_string())
grid.to_csv("shot_grid.csv", index=False)
