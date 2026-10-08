#!/usr/bin/env bash
# =====================================================
# DoWork.sh: rebuilds every result, figure, and the paper
#
# Requires Data/nba_shots.db (not included in this repo).
# Run from the repository root:   bash DoWork.sh
# =====================================================
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f Data/nba_shots.db ]; then
  echo "Missing Data/nba_shots.db - see README.md (the data are not included)." >&2
  exit 1
fi

PY=$(command -v python3 || command -v python)

# Analysis: scripts read ../Data and write their CSVs into Code/
cd Code
"$PY" task0_audit.py
"$PY" task1_season_summary.py
"$PY" task2_zone_by_season.py
"$PY" task3_decomposition.py
"$PY" task4_shot_grid.py
"$PY" make_figures.py
cd ..

# Paper: compile only if a LaTeX toolchain is installed
if command -v pdflatex >/dev/null 2>&1 && command -v bibtex >/dev/null 2>&1; then
  cd Papers
  pdflatex -interaction=nonstopmode Papers.tex >/dev/null
  bibtex Papers >/dev/null
  pdflatex -interaction=nonstopmode Papers.tex >/dev/null
  pdflatex -interaction=nonstopmode Papers.tex >/dev/null
  cd ..
  echo "Paper written to Papers/Papers.pdf"
else
  echo "pdflatex/bibtex not found: skipped compiling the paper."
fi
