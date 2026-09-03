# Bongo Cat verification map

This directory maps Bongo Cat's main user paths to repeatable checks. Read this index first, then open the feature file that matches the change.

## Baseline preconditions

- Install `requirements.txt` in the selected Python environment.
- Change to the repository root.
- Run `python .codex/skills/verify-bongocat/scripts/control.py doctor` and require all three bundled skins.
- Use a new absolute evidence directory for each reviewed run.
- Do not drive an existing Bongo Cat process.

## Driving conventions

- Run source checks with `QT_QPA_PLATFORM=offscreen` and `PYNPUT_BACKEND=dummy`. `control.py` sets both values before importing Bongo Cat.
- Use Qt `objectName` values rather than coordinates or tab order.
- Exercise the production widget and signal path.
- Read persisted values with a new `ConfigManager`.
- Keep evidence outside the helper's scratch directory.

## Proof and skip reporting

- Capture the rendered state before and after the user action.
- Record the selected skin as both a value and a Python type.
- Copy only the isolated config. Never copy a user's config into evidence.
- Report source-level proof separately from a packaged Windows run and a reporter retest.
- Name any mapped entry point that the current helper cannot drive.

## Feature entry contract

Each feature file has exactly four H2 sections. Follow the commands and observable results in order. Do not claim a different entry point as proof for a skipped path.

## Features

- [Settings](settings.md) covers opening the settings window, applying values, and reloading the saved config.
- [Skins](skins.md) covers bundled discovery, selection, and unrelated-working-directory launches.
- [Slap counter](slap-counter.md) covers visible count changes and preservation of completed direct INI edits.
