# =====================================================
# Task 3: Counterfactual decomposition
#
# Reads season_summary.csv and zone_by_season.csv (Tasks
# 1 and 2) and separates the change in points per attempt
# between 1997-98 and 2021-22 into a shot selection effect
# and a shot making effect, following equations (2)-(4) of
# the paper. Also verifies the zone table reproduces the
# season-level PPA exactly, and reports each effect's
# zone-by-zone contribution (Table 4).
#
# Output: decomposition_results.csv
# =====================================================

import pandas as pd

summary = pd.read_csv("season_summary.csv")
zones = pd.read_csv("zone_by_season.csv")
zones["ppa_zone"] = zones["make_rate"] * zones["pts_value"]

# ---- Consistency check: the zone table must reproduce Task 1's PPA ----
rebuilt = zones.assign(x=zones["share"] * zones["ppa_zone"]).groupby("season")["x"].sum()
check = rebuilt.reset_index().merge(summary[["season", "ppa"]], on="season")
max_diff = (check["x"] - check["ppa"]).abs().max()
print("Consistency check, max |rebuilt PPA - Task 1 PPA|: %.5f" % max_diff)

# ---- The decomposition, endpoint seasons ----
z97 = zones[zones.season == 1997].set_index("zone")
z21 = zones[zones.season == 2021].set_index("zone").reindex(z97.index)

A = (z97["share"] * z97["ppa_zone"]).sum()               # 1997 actual
D = (z21["share"] * z21["ppa_zone"]).sum()                # 2021 actual
making = (z97["share"] * z21["ppa_zone"]).sum() - A       # 2021 rates, 1997 mix
selection = (z21["share"] * z97["ppa_zone"]).sum() - A    # 1997 rates, 2021 mix
interaction = (D - A) - making - selection

print("\n================ Decomposition, 1997-98 to 2021-22 ================")
print("PPA 1997-98 (actual): %.4f" % A)
print("PPA 2021-22 (actual): %.4f" % D)
print("Total change:        %+.4f" % (D - A))
print("Shot making:         %+.4f  (%.0f%%)" % (making, 100 * making / (D - A)))
print("Shot selection:      %+.4f  (%.0f%%)" % (selection, 100 * selection / (D - A)))
print("Interaction:         %+.4f  (%.0f%%)" % (interaction, 100 * interaction / (D - A)))

# ---- Zone-level contribution to each effect (Table 4) ----
# Selection part: change in share, priced at the 1997 return
# Making part: change in return, priced at the 1997 share
contrib = pd.DataFrame({
    "share_1997": z97["share"],
    "share_2021": z21["share"],
    "ppa_1997": z97["ppa_zone"],
    "ppa_2021": z21["ppa_zone"],
})
contrib["selection_part"] = ((contrib["share_2021"] - contrib["share_1997"]) * contrib["ppa_1997"]).round(4)
contrib["making_part"] = (contrib["share_1997"] * (contrib["ppa_2021"] - contrib["ppa_1997"])).round(4)

print("\n================ Zone-level contributions (Table 4) ================")
print(contrib[["selection_part", "making_part"]].to_string())

# ---- Save everything for the record ----
summary_out = pd.DataFrame({
    "quantity": ["ppa_1997", "ppa_2021", "total_change", "making", "selection", "interaction"],
    "value": [A, D, D - A, making, selection, interaction],
})
summary_out.to_csv("decomposition_results.csv", index=False)
contrib.reset_index().rename(columns={"index": "zone"}).to_csv("decomposition_by_zone.csv", index=False)
