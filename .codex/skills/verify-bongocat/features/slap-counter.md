# Slap counter

The slap counter increments for global input and saves the count without replacing completed direct INI edits.

## Sub-features

- `slap-visible` updates the count shown by Bongo Cat.
- `slap-persist` restores the saved count after restart.
- `slap-preserve-settings` changes only `slaps` in the latest valid INI file.

## How to get to it (user POV)

- Press a key, click a mouse button, or use a controller while Bongo Cat is running.
- Open the INI file from the footer, finish an edit, and restart Bongo Cat to load it.

## Driving it with control.py

Preconditions:

- `python .codex/skills/verify-bongocat/scripts/control.py doctor` reports `status` as `ok`.
- No existing Bongo Cat session uses the isolated test config.

- **Check the persistence rule.** Run `python -m unittest tests.test_config.TestConfigFileOperations.test_slap_count_update_preserves_completed_external_edit -v`. The test completes an external edit before the production slap-count writer runs and reads the result through a restarted `ConfigManager`.
- **Record the control limit.** `control.py` does not synthesize global operating-system input. Report the visible counter path as unverified until a human presses a key in an owned test instance and sees the count increase by one.

## Gotchas

- `control.py` does not start global input listeners because they could capture the operator's real keyboard and mouse.
- Direct INI changes load after restart. Bongo Cat does not hot-reload them.
- Finish the editor write before the next slap. An external editor does not share a lock with Bongo Cat.
