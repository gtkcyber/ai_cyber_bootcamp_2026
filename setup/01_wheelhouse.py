# Databricks notebook source
# MAGIC %md
# MAGIC # 1. Build the course library wheelhouse
# MAGIC Downloads the pinned packages into `/Volumes/<catalog>/<schema>/data/wheelhouse/wheels` and writes the
# MAGIC cluster init script. Run it once after `scripts/deploy-course-data.sh` has uploaded `wheelhouse/wheelhouse-pins.txt`.
# MAGIC Linux only, so it must run on a cluster.

# COMMAND ----------

dbutils.widgets.text("catalog", "ai_cyber_bootcamp")
dbutils.widgets.text("schema", "course")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
WH = f"/Volumes/{CATALOG}/{SCHEMA}/data/wheelhouse"
PINS = f"{WH}/wheelhouse-pins.txt"
WHEELS = f"{WH}/wheels"

import os, subprocess, sys, shutil, glob

assert os.path.exists(PINS), f"missing {PINS}: run scripts/deploy-course-data.sh first"
os.makedirs(WHEELS, exist_ok=True)

# COMMAND ----------

# Binary wheels first. Source-only packages (sdists) are built into wheels separately below.
def pip(*args):
    return subprocess.run([sys.executable, "-m", "pip", *args], capture_output=True, text=True)

platform_flags = []
for p in ["manylinux_2_17_x86_64", "manylinux_2_28_x86_64", "manylinux2014_x86_64", "any"]:
    platform_flags += ["--platform", p]
r = pip("download", "-q", "--no-deps", "--only-binary=:all:", *platform_flags,
        "--python-version", "3.12", "--implementation", "cp", "-d", WHEELS, "-r", PINS)
print("binary download exit", r.returncode, r.stderr[-400:] if r.returncode else "")

# COMMAND ----------

# Any pin without a binary wheel: download the source and build a pure wheel here (Linux).
have = {os.path.basename(f).split("-")[0].lower().replace("_", "-") for f in glob.glob(f"{WHEELS}/*.whl")}
missing = []
for line in open(PINS):
    line = line.strip()
    if "==" not in line:
        continue
    name, ver = line.split("==", 1)
    if name.lower().replace("_", "-") not in have:
        missing.append(line)
print("pins without a binary wheel:", missing)
for pin in missing:
    src = "/tmp/wh-src"
    os.makedirs(src, exist_ok=True)
    d = pip("download", "-q", "--no-deps", "--no-binary=:all:", "-d", src, pin)
    tars = glob.glob(f"{src}/*.tar.gz") + glob.glob(f"{src}/*.zip")
    for t in tars:
        b = pip("wheel", "-q", "--no-deps", "-w", WHEELS, t)
        print("built", os.path.basename(t), "exit", b.returncode)
    shutil.rmtree(src, ignore_errors=True)

# COMMAND ----------

# Init script and the pins the cluster installs. Same contents as the course's install-wheelhouse.sh.
shutil.copy(PINS, f"{WH}/delta-pins.txt")
init = f"""#!/bin/bash
# Course libraries from the pinned wheelhouse: no PyPI, no resolver (--no-deps).
set -e
WH={WH}
/databricks/python/bin/pip install --no-deps --no-index --find-links "$WH/wheels" -r "$WH/delta-pins.txt" > /tmp/wheelhouse-install.log 2>&1 \\
  || {{ cat /tmp/wheelhouse-install.log; exit 1; }}
"""
open(f"{WH}/install-wheelhouse.sh", "w").write(init)
print("wrote", f"{WH}/delta-pins.txt", "and install-wheelhouse.sh")
print("wheels:", len(glob.glob(f"{WHEELS}/*.whl")))
