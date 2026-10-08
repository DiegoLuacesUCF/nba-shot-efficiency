# =====================================================
# Figures: builds all six figures used in the paper
#
# Reads season_summary.csv, zone_by_season.csv, and
# shot_grid.csv (Tasks 1, 2, and 4) and produces every
# figure exactly as numbered in the paper. Each figure
# is saved directly under ../Figures/ as FigureN.pdf.
# =====================================================

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.colors import PowerNorm
from scipy.ndimage import gaussian_filter

OUT = "../Figures/"
NAVY, BLUE, LTBLUE = "#1F3864", "#2E5496", "#8EAADB"
ORANGE, GOLD, GRAY = "#C55A11", "#E8A33D", "#999999"

summary = pd.read_csv("season_summary.csv")
zones = pd.read_csv("zone_by_season.csv")
zones["ppa_zone"] = zones["make_rate"] * zones["pts_value"]

# Corners are combined throughout, matching Table 2 in the paper
zones["zone2"] = zones["zone"].replace({"Left Corner 3": "Corner 3", "Right Corner 3": "Corner 3"})
zones_made = zones.assign(made=zones["attempts"] * zones["make_rate"])
zc = zones_made.groupby(["season", "zone2"], as_index=False).agg(
    attempts=("attempts", "sum"), made=("made", "sum"), share=("share", "sum"))
zc["make_rate"] = zc["made"] / zc["attempts"]
zc["pts_value"] = np.where(zc["zone2"].isin(["Above the Break 3", "Corner 3"]), 3.0, 2.0)
zc["ppa_zone"] = zc["make_rate"] * zc["pts_value"]

all_seasons = list(range(1997, 2022))  # 2002-03 is absent by design
zone_order = ["Restricted Area", "In The Paint (Non-RA)", "Mid-Range",
              "Above the Break 3", "Corner 3", "Backcourt"]
zone_colors = [NAVY, BLUE, LTBLUE, ORANGE, GOLD, GRAY]


def with_gap(series_by_season):
    return pd.Series(series_by_season).reindex(all_seasons)


# ============================================================
# Figure 1: the two headline trends
# ============================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
ppa = with_gap(summary.set_index("season")["ppa"])
sh3 = with_gap(summary.set_index("season")["share_3pt"])

ax1.plot(all_seasons, ppa, color=NAVY, marker="o", ms=4, lw=2)
ax1.set_ylabel("Points per attempt")
ax1.set_title("The NBA scores more per shot: +0.107 points per attempt, 1997-98 to 2021-22")
ax1.annotate("0.956", (1997, 0.9561), textcoords="offset points", xytext=(6, -14), color=NAVY)
ax1.annotate("1.063", (2021, 1.0634), textcoords="offset points", xytext=(-32, 8), color=NAVY)

ax2.plot(all_seasons, sh3, color=ORANGE, marker="o", ms=4, lw=2)
ax2.set_ylabel("Share of attempts from 3")
ax2.set_title("...while the three-point share went from 1 in 6 shots to 2 in 5")
ax2.set_xlabel("Season (start year; 2002-03 not in dataset)")
ax2.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
for ax in (ax1, ax2):
    ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(OUT + "Figure1.pdf")
plt.close(fig)

# ============================================================
# Figure 2: shot mix by zone, all 24 seasons (stacked area)
# ============================================================
fig, ax = plt.subplots(figsize=(9.5, 5.5))
for seg in [range(1997, 2002), range(2003, 2022)]:
    seg = list(seg)
    mat = [pd.Series(zc[zc.zone2 == zn].set_index("season")["share"]).reindex(seg).values
           for zn in zone_order]
    ax.stackplot(seg, mat, colors=zone_colors,
                 labels=zone_order if seg[0] == 1997 else [], alpha=0.92)
ax.set_xlim(1997, 2021)
ax.set_ylim(0, 1)
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.set_xlabel("Season (start year; gap = missing 2002-03)")
ax.set_ylabel("Share of all attempts")
ax.set_title("The mid-range dies, the three takes its place: shot mix by zone")
ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
fig.tight_layout()
fig.savefig(OUT + "Figure2.pdf")
plt.close(fig)

# ============================================================
# Figure 3: endpoint comparison (dumbbell)
# ============================================================
z97 = zc[zc.season == 1997].set_index("zone2")["share"]
z21 = zc[zc.season == 2021].set_index("zone2")["share"]
order = ["Mid-Range", "Restricted Area", "In The Paint (Non-RA)",
         "Above the Break 3", "Corner 3", "Backcourt"]

fig, ax = plt.subplots(figsize=(9, 5))
for i, zn in enumerate(order):
    a, b = z97[zn], z21[zn]
    ax.plot([a, b], [i, i], color=GRAY, lw=2.5, zorder=1)
    ax.scatter([a], [i], s=110, color=LTBLUE, zorder=2, label="1997-98" if i == 0 else "")
    ax.scatter([b], [i], s=110, color=NAVY, zorder=2, label="2021-22" if i == 0 else "")
    ax.annotate(f"{b - a:+.0%}", ((a + b) / 2, i + 0.18), ha="center", fontsize=9,
                color=ORANGE if b > a else BLUE, fontweight="bold")
ax.set_yticks(range(len(order)))
ax.set_yticklabels(order)
ax.invert_yaxis()
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.set_xlabel("Share of all shot attempts")
ax.set_title("Where the shots went: mid-range money moved behind the arc")
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(OUT + "Figure3.pdf")
plt.close(fig)

# ============================================================
# Figure 4: shot density on the court, endpoint seasons
# ============================================================
grid = pd.read_csv("shot_grid.csv")
X_MIN, X_MAX, Y_MIN, Y_MAX = -25, 25, -5, 35


def draw_court(ax):
    ax.add_patch(Circle((0, 0), 0.75, fill=False, color="#333333", lw=1.1))
    ax.add_patch(Rectangle((-8, 0), 16, 19, fill=False, color="#333333", lw=1.1))
    ax.add_patch(Arc((0, 19), 12, 12, theta1=0, theta2=180, color="#333333", lw=1.1))
    ax.plot([-22, -22], [0, 14], color="#333333", lw=1.1)
    ax.plot([22, 22], [0, 14], color="#333333", lw=1.1)
    ax.add_patch(Arc((0, 0), 47.5, 47.5, theta1=22, theta2=158, color="#333333", lw=1.1))
    ax.plot([-3, 3], [0, 0], color="#333333", lw=1.5)


fig, axes = plt.subplots(1, 2, figsize=(10, 5.6))
for ax, season, title in zip(axes, [1997, 2021], ["1997-98", "2021-22"]):
    d = grid[grid.season == season]
    hb = ax.hexbin(d.x_ft.values, d.y_ft.values, C=d.attempts.values,
                    reduce_C_function=np.sum, gridsize=26,
                    extent=[X_MIN, X_MAX, Y_MIN, Y_MAX], cmap="Reds",
                    mincnt=1, linewidths=0.2, edgecolors="#00000022",
                    norm=PowerNorm(gamma=0.42))
    draw_court(ax)
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_title(title, fontsize=13)
    ax.set_aspect("equal")
    ax.axis("off")
fig.tight_layout()
fig.savefig(OUT + "Figure4.pdf", facecolor="white")
plt.close(fig)

# ============================================================
# Figure 5: make rate by zone, all 24 seasons
# ============================================================
fig, ax = plt.subplots(figsize=(9.5, 5.5))
for zn, c in zip(zone_order[:-1], zone_colors[:-1]):  # Backcourt excluded, too few attempts
    s = with_gap(zc[zc.zone2 == zn].set_index("season")["make_rate"])
    ax.plot(all_seasons, s, color=c, marker="o", ms=3, lw=1.8, label=zn)
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.set_xlabel("Season (start year; 2002-03 not in dataset)")
ax.set_ylabel("Make rate")
ax.set_title("Where the shot MAKING happened: finishing inside improved, 3-pt accuracy barely moved")
ax.legend(fontsize=8)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(OUT + "Figure5.pdf")
plt.close(fig)

# ============================================================
# Figure 6: decomposition waterfall
# ============================================================
decomp = pd.read_csv("decomposition_results.csv").set_index("quantity")["value"]

fig, ax = plt.subplots(figsize=(9, 5.5))
steps = [("1997-98\nactual", decomp["ppa_1997"], None),
         ("Better shot\nselection", decomp["selection"], ORANGE),
         ("Better shot\nmaking", decomp["making"], BLUE),
         ("Interaction", decomp["interaction"], GRAY),
         ("2021-22\nactual", decomp["ppa_2021"], None)]
running = 0.0
for i, (label, val, color) in enumerate(steps):
    if color is None:
        ax.bar(i, val, color=NAVY, width=0.62)
        ax.annotate(f"{val:.3f}", (i, val), ha="center", va="bottom", fontweight="bold")
        running = val if i == 0 else running
    else:
        bottom = running if val >= 0 else running + val
        ax.bar(i, abs(val), bottom=bottom, color=color, width=0.62)
        ax.annotate(f"{val:+.4f}", (i, running + max(val, 0)), ha="center",
                    va="bottom", fontweight="bold", color=color)
        ax.plot([i - 1 + 0.31, i - 0.31], [running, running], color="black", lw=0.8, ls=":")
        running += val
ax.plot([3 + 0.31, 4 - 0.31], [running, running], color="black", lw=0.8, ls=":")
ax.set_xticks(range(5))
ax.set_xticklabels([s[0] for s in steps])
ax.set_ylim(0.90, 1.10)
ax.set_ylabel("Points per attempt")
ax.set_title("From 0.956 to 1.063: what built the modern NBA offense")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT + "Figure6.pdf")
plt.close(fig)

print("All six figures written to", OUT)
