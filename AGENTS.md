# Bongo Cat

## Layout

- `bongo_cat/`: PyQt5 desktop application; `tests/`: tests.
- `skins/`, `sounds/`, `img/`: assets.
- `bongo_cat.spec`, `build.py`, `build_unix.sh`, `build_windows.bat`: packaging.
- `requirements.txt`: runtime dependencies; `requirements-dev.txt`: optional development tools.

## Setup and development

Use Python 3.11 to match release CI, with a repo-local venv. From the repo root:

On Linux, installing `requirements.txt` needs a compiler and Python headers (`Python.h`; `python3-dev` or the equivalent package for the selected Python). The `pynput` dependency `evdev` may need to build from source on newer Pythons. Python 3.11 with headers works and remains the release CI match.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install "pyinstaller>=5.0" "Pillow>=10.0.0"
```

Run from source: `python -m bongo_cat`.

## Workflow and completion
- Work on a task branch; never commit to `main`.
- Use repo-local environments and dependencies; do not install packages or toolchains globally.
- Never print, log, or commit secrets, tokens, credentials, or auth-file contents.
- Before claiming done, run the required checks below from the repo root and report results and any blocked or skipped checks.
- Timing-sensitive tests must use a handshake or event, never sleep, extra retries, or a longer timeout to make a test pass.

## Required checks

Tests and packaging must pass:

```sh
PYNPUT_BACKEND=dummy QT_QPA_PLATFORM=offscreen python -m unittest discover tests -v
pyinstaller --clean --noconfirm bongo_cat.spec
```

## Gotchas

- Setup uses `.venv/`, but `.gitignore` ignores `venv/` and `env/`, not `.venv/`; the repo-local `.venv/` shows as untracked. Do not commit it.
- Running the app or tests from the repo root writes `achievements.json` there. It is untracked and not ignored; do not commit it.
- Headless tests need both environment variables shown above.
- Packaging writes platform-specific artifacts under `dist/`.
- Linux packaging needs the xcb runtime libraries listed in `README.md` and `.github/workflows/release.yml`.
- There is no PR CI. Release CI runs only on `v*` tags or `workflow_dispatch`.
- No separate lint gate is defined; pytest, flake8, black, and mypy are optional development tools, not required gates.
