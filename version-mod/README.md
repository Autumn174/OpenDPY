## OpenDoctoratePy Version Mod

### How-To

1. Run `setup.bat`.
2. Run `run.bat`. Please ignore warnings like: `warning: field names should be lowercase snake_case, got: XXXXXX`.
3. Copy/Move all generated `.dat` files in `mod` folder to ODPY's `mods` folder.
4. Set `"assets"` -> `"enableMods"` in ODPY's `config/config.json` to `true`.

### Warning!

If you don't know what you are doing, I strongly discourage you from modifying any setting in `settings.json`. The generated mod is **only for** game version specified by `"target_version"` in `settings.json`, but **no guarantee** can be given that new versions can be readily supported by simply tweaking this option.

