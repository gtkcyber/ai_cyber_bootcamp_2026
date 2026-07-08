# Setup

Create a Python 3.12 virtual environment and install the dependencies.

## Prerequisite: Python 3.12

Check if you already have it:

```bash
python3.12 --version
```

If not, install it:

- **macOS:** `brew install python@3.12`
- **Windows:** `winget install Python.Python.3.12` (or download from [python.org](https://www.python.org/downloads/))
- **Linux (Debian/Ubuntu):** `sudo apt install python3.12 python3.12-venv`
- **Any OS:** use [`pyenv`](https://github.com/pyenv/pyenv) — `pyenv install 3.12`

## macOS prerequisite: libomp

XGBoost (a TPOT dependency) needs `libomp` or importing it fails. Install it once:

```bash
brew install libomp
```

## 1. Create the virtual environment

```bash
python3.12 -m venv venv
```

If `python3.12` isn't found, install it first (macOS: `brew install python@3.12`) or use a version manager like `pyenv`.

## 2. Activate it

```bash
# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

Your prompt should now show `(venv)`.

## 3. Install the requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Verify

```bash
python --version   # should print Python 3.12.x
pip list           # shows the installed packages
```

When you're done working, run `deactivate` to exit the environment.

## Troubleshooting

- **`setuptools` version conflicts** — `setuptools` is pinned to `<82` in `requirements.txt` because newer versions break some dependencies. Don't run `pip install --upgrade setuptools`; if something already bumped it, reinstall with `pip install -r requirements.txt` to restore the pinned version.
- **`import xgboost` fails on macOS** — install `libomp` (see the prereq above): `brew install libomp`.
- **`python3.12: command not found`** — Python 3.12 isn't installed or isn't on your PATH. See the prereq section above.
- **Wrong Python inside the venv** — `python --version` doesn't show 3.12. The venv was built with the wrong interpreter. Delete it (`rm -rf venv`) and recreate with `python3.12 -m venv venv`.