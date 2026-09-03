# Skins

Skins lets a user choose one of the bundled cat appearances even when Bongo Cat starts outside the repository directory.

## Sub-features

- `skins-discover` finds `default`, `neon`, and `retro` from the application resource directory.
- `skins-select` stores a string skin ID in the config.
- `skins-custom` keeps an explicitly supplied skin directory authoritative.

## How to get to it (user POV)

- Open Settings and use the **Cat Skin** selector.
- Restart Bongo Cat after adding a custom skin directory under the application `skins` directory.

## Driving it with control.py

Preconditions:

- The repository contains the three bundled skin directories and their image files.
- `python .codex/skills/verify-bongocat/scripts/control.py doctor` reports `skin_count` as `3` from an unrelated working directory.

- **Inspect discovery.** Run `python .codex/skills/verify-bongocat/scripts/control.py doctor`. Require `skin_ids` to contain `default`, `neon`, and `retro`.
- **Capture selection.** Run `python .codex/skills/verify-bongocat/scripts/control.py settings-apply --evidence-dir <absolute-path>`. `settings-before.png` shows a non-empty selector.
- **Confirm the boundary.** Read `result.json`. `selected_skin_type` is `str`, `selected_skin_id` is `default`, and `resolved_skins_dir` is an absolute application resource path.
- **Check custom injection.** Run `python -m unittest tests.test_skin_manager.TestSkinManagerPaths.test_explicit_relative_skin_directory_stays_authoritative -v`. The supplied relative path remains unchanged.

## Gotchas

- The process working directory is not the application resource directory.
- A fallback cat image can render while the skin selector is empty. Inspect the selector and the recorded IDs.
- Custom skin injection is a source API check. The control helper uses bundled skins.
