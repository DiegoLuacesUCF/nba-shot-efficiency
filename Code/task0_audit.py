# =====================================================
# Task 0: Data audit for nba_shots.db
#
# Confirms the structure and contents of the shots table
# before any analysis code is written: column names and
# types, row count, date range, how outcomes are coded,
# and the raw format of GAME_ID.
# =====================================================

import sqlite3
import pandas as pd

db_path = "../Data/nba_shots.db"
con = sqlite3.connect(db_path)

# Every column name and type
print(pd.read_sql("PRAGMA table_info(shots)", con)[["name", "type"]].to_string(index=False))

# Row count, should be 4,678,387
print(pd.read_sql("SELECT COUNT(*) AS total_rows FROM shots", con))

# Date range of the data
print(pd.read_sql("SELECT MIN(GAME_DATE) AS first_game, MAX(GAME_DATE) AS last_game FROM shots", con))

# How outcomes and shot types are coded
print(pd.read_sql("SELECT SHOT_TYPE, SHOT_MADE_FLAG, COUNT(*) AS n FROM shots GROUP BY SHOT_TYPE, SHOT_MADE_FLAG", con))

# What GAME_ID actually looks like
print(pd.read_sql("SELECT GAME_ID, GAME_DATE FROM shots LIMIT 5", con))

con.close()
