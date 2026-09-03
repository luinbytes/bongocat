---
name: verify-bongocat
description: Drive Bongo Cat's PyQt settings window when a change needs real Apply-button, skin-discovery, rendered-state, or config-persistence proof.
---

# Verify Bongo Cat

Use this skill for source-level checks of Bongo Cat's desktop UI. Read the [feature map](features/README.md) before choosing a recipe. A Windows PyInstaller build and a reporter retest remain separate acceptance checks.

## Launch

Run commands from the repository root. The helper resolves the repository from its own path and creates a short-lived offscreen Qt application.

```bash
python .codex/skills/verify-bongocat/scripts/control.py settings-apply \
  --evidence-dir /tmp/verify-bongocat-settings
```

The helper exits after the drive. Exit code `0` means that the real Apply-button path and its persistence checks passed.

## Doctor

Run the read-only doctor before a drive or when Qt setup looks wrong.

```bash
python .codex/skills/verify-bongocat/scripts/control.py doctor
```

Require `status` to be `ok`, `skin_count` to be `3`, and `skin_ids` to contain `default`, `neon`, and `retro`. Doctor does not create a Bongo Cat config file.

## Drive

Use `settings-apply` for the settings and skin recipes. The helper changes to an unrelated temporary working directory before it imports the app. It sets an isolated `APPDATA`, uses the dummy `pynput` backend, and renders Qt offscreen.

The drive opens the production settings window. It locates `skinDropdown`, `soundEnabledCheckbox`, and `applySettingsButton` by Qt `objectName`. It captures the panel, unchecks sounds, clicks the real Apply button with `QTest.mouseClick()`, captures the result, and reloads the saved config through a new `ConfigManager`.

## Evidence

Pass an absolute, task-owned evidence directory. The helper preserves these files:

- `settings-before.png` shows the populated skin selector before the action.
- `settings-after.png` shows the rendered unchecked sound setting after Apply.
- `result.json` records the source revision, Python and Qt versions, resolved skin path, skin IDs, selected skin value and type, error-dialog count, persisted sound value, and cleanup result.
- `bongo.ini` is a copy of the isolated saved config.

Keep the evidence until the task handoff. A final screenshot without the action and persisted read-back is not proof.

## Cleanup

The helper hides and deletes only the Qt widgets it creates. It quits its own `QApplication` and removes its temporary working and `APPDATA` directories. It does not start `InputManager`, kill by process name, or touch an existing Bongo Cat session. Cleanup preserves the evidence directory.

## Helpers

`scripts/control.py` is the only helper. Run `python .codex/skills/verify-bongocat/scripts/control.py --help` for its commands. Do not import it into production code.
