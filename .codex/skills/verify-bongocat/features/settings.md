# Settings

Settings lets a user change Bongo Cat behavior and persist the selected values with **Apply**.

## Sub-features

- `settings-open` opens the separate settings window.
- `settings-apply` saves the selected values without closing Bongo Cat.
- `settings-restart` loads saved values in a fresh application state.

## How to get to it (user POV)

- Hover over Bongo Cat and choose the settings button in the footer.
- Open Settings from the app's controls, change a value, and choose **Apply**.

## Driving it with control.py

Preconditions:

- `python .codex/skills/verify-bongocat/scripts/control.py doctor` reports `status` as `ok`.
- The evidence path is absolute and belongs to the current task.

- **Open and capture.** Run `python .codex/skills/verify-bongocat/scripts/control.py settings-apply --evidence-dir <absolute-path>`. `settings-before.png` shows the settings window and a populated **Cat Skin** selector.
- **Apply.** The helper unchecks **Enable Sounds** and clicks `applySettingsButton` with `QTest.mouseClick()`. `settings-after.png` shows the unchecked control.
- **Confirm persistence.** Read `result.json`. `apply_error_count` is `0` and `persisted_sound_enabled` is `false`. The copied `bongo.ini` has `sound_enabled = false`.

## Gotchas

- A surviving Qt process is insufficient when Apply did not save the value.
- Source-level offscreen proof does not replace a packaged Windows check.
- The helper owns its isolated config. Do not point it at a user profile.
