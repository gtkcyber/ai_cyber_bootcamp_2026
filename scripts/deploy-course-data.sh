#!/usr/bin/env bash
# Upload the course data, slides and (optionally) notebooks to a Databricks workspace.
# Credentials come from the Databricks CLI profile (DATABRICKS_CONFIG_PROFILE or --profile),
# the same ones Terraform uses. Nothing secret is written here.
#
# Usage:
#   scripts/deploy-course-data.sh --profile PROFILE --catalog CATALOG --schema SCHEMA [--home EMAIL] [--dry-run]
#
#   --catalog/--schema  the catalog and schema Terraform created (defaults: ai_cyber_bootcamp / course)
#   --home EMAIL        also import the notebooks and utils into that user's home folder
#   --dry-run           print the commands instead of running them
set -euo pipefail

PROFILE="${DATABRICKS_CONFIG_PROFILE:-}"
CATALOG="ai_cyber_bootcamp"
SCHEMA="course"
HOME_USER=""
DRY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --catalog) CATALOG="$2"; shift 2 ;;
    --schema)  SCHEMA="$2"; shift 2 ;;
    --home)    HOME_USER="$2"; shift 2 ;;
    --dry-run) DRY="echo"; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$PROFILE" ] || { echo "set --profile or DATABRICKS_CONFIG_PROFILE" >&2; exit 2; }

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VOL="dbfs:/Volumes/${CATALOG}/${SCHEMA}"
DBX=(databricks -p "$PROFILE")

# Data volume: everything under data/, including bpe_merges.json, datasets and the pickles.
$DRY "${DBX[@]}" fs cp -r "$ROOT/data" "$VOL/data" --overwrite

# Wheelhouse pins: the job in setup/01_wheelhouse.py reads this file from the volume.
$DRY "${DBX[@]}" fs cp "$ROOT/setup/wheelhouse-pins.txt" "$VOL/data/wheelhouse/wheelhouse-pins.txt" --overwrite

# Slides: one shared copy, per the add-students runbook.
$DRY "${DBX[@]}" fs cp -r "$ROOT/slides" "$VOL/data/slides" --overwrite

# Optional: a student's home folder gets the notebooks, answers and utils.
if [ -n "$HOME_USER" ]; then
  DEST="/Users/${HOME_USER}/AI Cyber Bootcamp 2026"
  $DRY "${DBX[@]}" workspace mkdirs "$DEST/work"
  $DRY "${DBX[@]}" workspace import-dir "$ROOT/notebooks" "$DEST/notebooks" --overwrite
  $DRY "${DBX[@]}" workspace import-dir "$ROOT/answers" "$DEST/answers" --overwrite
  $DRY "${DBX[@]}" workspace import-dir "$ROOT/utils" "$DEST/utils" --overwrite
fi

echo "done: data and slides to ${VOL}; the library wheelhouse is NOT uploaded; build it first, see the wheelhouse runbook"
