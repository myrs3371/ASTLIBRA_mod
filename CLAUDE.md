# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ASTLIBRA MOD Tool - A text extraction, editing, and import tool for the ASTLIBRA game. Supports localization and MOD creation, handling 12,000+ multilingual text entries.

**Tech Stack**: Python 3.11+, Vue 3 (Web UI), pywebview (native window), Pandas (data processing), PyInstaller (packaging)

## Development Commands

### Run Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py
```

### Build Executable
```bash
# Build with PyInstaller
pip install pyinstaller
pyinstaller ASTLIBRA_MOD_TOOL.spec
```
Output: `dist/ASTLIBRA_MOD_TOOL.exe` (console=False, edgechromium GUI)

### Debug Mode
To enable console output for debugging, modify `ASTLIBRA_MOD_TOOL.spec:32` to set `console=True` before building.

## Architecture

### Hybrid Desktop Application
Native window (pywebview) + Web UI (Vue 3) + Python backend

**Layered Structure**:
- **Frontend Layer**: Vue 3 SPA with reactive UI components
- **Bridge Layer**: pywebview provides `window.pywebview.api.*` for JS ↔ Python communication
- **API Layer**: [frontend/api.py](frontend/api.py) exposes Python methods to JavaScript
- **Service Layer**: [backend/services/](backend/services/) handles business logic
- **Core Layer**: [core/](core/) handles binary file operations

### Key Directory Structure
```
ASTLIBRA_MOD_TOOL.spec    # PyInstaller build config
main.py                   # Entry point - creates pywebview window
config.py                 # Path management and game directory detection
requirements.txt          # Python dependencies
web/                      # Vue 3 frontend (served via pywebview)
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── app.js       # Vue app initialization and routing
│       └── pages/      # Page components as .js files
│           ├── home.js
│           ├── dialogue.js
│           └── mod.js
frontend/api.py           # pywebview JS API bridge (Api class)
backend/services/         # Business logic
│   ├── game_manager.py  # Game directory detection
│   ├── text_extractor.py # 5-step extraction pipeline
│   ├── text_importer.py # Text import pipeline
│   └── mod_manager.py   # MOD activation/restore
core/                     # Binary processing tools
│   ├── _ALOC.py         # ALOC format packer/unpacker (-e export, -p pack)
│   ├── patch_exe.py     # Game EXE patcher
│   ├── text_classifier.py
│   ├── ASTLIBRA_Dec.exe # DAT.dxa unpacker
│   └── TOOLS/           # Standalone image conversion scripts
│       ├── dig_decoder.py  # .dig → PNG (game image format, zlib+PNG filter)
│       └── dig_encoder.py  # PNG → .dig (accepts *.dig.png files)
```

## Key Workflows

### Text Extraction Pipeline (Manual Trigger)
Triggered when user clicks "开始提取文本" on the dialogue page (`dialoguePage.triggerExtraction()` → `pywebview.api.start_extraction()`). Runs in a background thread; frontend polls `get_extraction_status()` every 500ms.

1. Unpack `DAT.dxa` using `ASTLIBRA_Dec.exe` → `DAT/` folder
2. Rename original `DAT.dxa` → `DAT_BACK.dxa` (backup)
3. Patch game EXE (byte replacement to enable text reading)
4. Extract text from `LOCALIZE_.DAT_dec` template using `_ALOC.py -e` → CSV
5. Repack CSV → `LOCALIZE_.DAT` using `_ALOC.py -p`

### Text Import Pipeline
1. User edits text in Web UI → saved to `_extracted_texts.csv`
2. `TextImporter.apply_changes()` copies CSV to `core/`
3. `_ALOC.py -p` repacks CSV → `LOCALIZE_.DAT`
4. `LOCALIZE_.DAT` copied to game `DAT/` folder

### Text Editing Flow
1. Web UI fetches data from Python backend via JS API
2. User edits text in Vue components
3. Changes sent to Python API → saved to CSV
4. Import pipeline repacks CSV → `LOCALIZE_.DAT` → game files

### MOD System
- File-based override system in `MODS/` directory
- MOD folder structure: `MODS/MyMod/Image/xxx.png`, `MODS/MyMod/Sound/xxx.ogg`, etc.
- Each MOD folder contains `mod_info.json` (optional) + data subfolders (Image, Sound, DAT, etc.)
- Active MODs tracked in `MODS/active_mods.json`: `{"mods": [{"name": "...", "folder_name": "...", ...}]}`
- On activation (7-step pipeline): patch EXE → rename backups to originals → delete game data folders → re-extract all `.dxa` files → copy MOD files over extracted data → rename originals back to backups → repack `LOCALIZE_.DAT`
- Supports batch activation (multiple MODs at once)
- On restore (`restore_all_mods`): delete all game data folders, rename `*_BACK.dxa` → `*.dxa`, clear `active_mods.json`
- `restore_all_files()`: restores EXE from `ASTLIBRA_back.exe` backup then **deletes** the backup; `.dxa` backups are consumed by rename so they also disappear

## Path Management

The `Config` class centralizes all path logic:
- Auto-detects game directory by checking for `ASTLIBRA.exe` + `DATA/` in the same folder as the tool (or EXE when frozen)
- When compiled: tool EXE must be placed **in the game root** (same folder as `ASTLIBRA.exe`)
- When running from source: `PROJECT_ROOT` (repo root) must be the game folder
- All paths resolve relative to detected game root
- `Config.DATA_LIST = ['Image', 'Image2K', 'Image4K', 'Image720p', 'Sound', 'DAT']` - defines game data folders used by MOD system
- Three parallel lists used by MOD activation pipeline:
  | DATA_LIST | DATA_BACK_LIST | DATA_GAME_LIST |
  |-----------|----------------|----------------|
  | DAT | DAT_BACK.dxa | DAT.dxa |
  | Image | Image_BACK.dxa | Image.dxa |
  | Image2K | Image2K_BACK.dxa | Image2K.dxa |
  | Image4K | Image4K_BACK.dxa | Image4K.dxa |
  | Image720p | Image720p_BACK.dxa | Image720p.dxa |
  | Sound | Sound_BACK.dxa | Sound.dxa |

## Data Flow

```
DAT.dxa (binary)
  → ASTLIBRA_Dec.exe → DAT/LOCALIZE_.DAT
  → _ALOC.py (export) → _extracted_texts.csv
  → Web UI (Vue) ↔ Python API (api.py) ↔ CSV
  → _ALOC.py (import) → LOCALIZE_.DAT
  → Game files
```

## Important Constraints

### Binary Format Details
- `_ALOC.py` handles custom ALOC binary format (struct-based parsing via Python `struct` module)
  - `-e` flag: export `LOCALIZE_.DAT_dec` → CSV
  - `-p` flag: pack CSV → `LOCALIZE_.DAT`
- `LOCALIZE_.DAT_dec` in `core/` is the template file used for text extraction
- Text encoding: UTF-8 with special markers `[n_rn]` (CRLF) and `[n_nr]` (LF)
- 6 language columns: JPN, US, ZH_CN, ZH_TW, KO, ES
- `DAT_BACK.dxa` is created as backup when first extraction runs

### Threading Model
- Long-running operations (extraction, import) run in background threads
- Python API methods start threads and return immediately
- Frontend polls status via `get_extraction_status()` which returns `{step, done, success, error}`
- Never blocks UI thread directly

### File Operations
- Tool modifies game files - creates backups (`DAT_BACK.dxa`, `ASTLIBRA_back.exe`); both are deleted automatically when `restore_all_files()` completes
- Extraction is manually triggered; startup only checks `has_csv` to show/hide the extraction prompt
- CSV is the source of truth for text editing
- MOD system uses JSON manifests (`mod_info.json`) for metadata
- Vue.js bundled locally (`web/js/vue.global.prod.js`) to eliminate CDN load delays
- pywebview uses `edgechromium` backend (see [main.py:38](main.py#L38))

### Platform Constraint
- **Windows-only**: All `subprocess.run()` calls pass `creationflags=subprocess.CREATE_NO_WINDOW`, which is a Windows-only flag. The app is not cross-platform.

### Error Handling
- All long-running operations use background threads to prevent UI blocking
- Status polling pattern: frontend calls `get_extraction_status()` to check progress
- Errors are captured in status dict with `{step, done, success, error}` structure
- File operations include existence checks before processing

## Key Files

- [main.py](main.py) - Application entry point, creates pywebview window with centered positioning
- [frontend/api.py](frontend/api.py) - Python API exposed to JavaScript via `window.pywebview.api.*`
- [web/js/app.js](web/js/app.js) - Vue 3 app initialization and routing
- [config.py](config.py) - Path management and game directory detection (auto-detects by searching for `ASTLIBRA.exe`)
- [core/_ALOC.py](core/_ALOC.py) - Binary format parser for game text files (`-e` export, `-p` pack)
- [core/text_classifier.py](core/text_classifier.py) - Text classification by keyword rules (dialogue, UI, item, etc.)
- [core/read_csv.py](core/read_csv.py) - CSV reader used by `get_texts()`, applies classification
- [backend/services/text_extractor.py](backend/services/text_extractor.py) - 5-step extraction pipeline
- [backend/services/text_importer.py](backend/services/text_importer.py) - Text import/revert logic
- [backend/services/mod_manager.py](backend/services/mod_manager.py) - MOD activation (7-step) / restore logic
- [ASTLIBRA_MOD_TOOL.spec](ASTLIBRA_MOD_TOOL.spec) - PyInstaller build configuration (root level, not inside a subdirectory)
- [core/TOOLS/dig_decoder.py](core/TOOLS/dig_decoder.py) - Standalone: `python dig_decoder.py <file.dig>` → `<file.dig>.png`. Supports 1/2/3/4-channel DIG files (zlib-compressed, PNG-filtered, little-endian BGRA).
- [core/TOOLS/dig_encoder.py](core/TOOLS/dig_encoder.py) - Standalone: `python dig_encoder.py <file.dig.png>` → overwrites `<file.dig>` in-place (creates `.bak` backup automatically).

## Development Notes

### Python-JavaScript Communication
- All Python methods in `Api` class are automatically exposed to JavaScript
- Methods must be synchronous or use threading for async operations
- Return values are automatically serialized to JSON
- Frontend accesses via `window.pywebview.api.method_name()`

Key API methods in [frontend/api.py](frontend/api.py):
- `get_game_info()` → `{detected, game_path, has_csv}`
- `start_extraction()` / `get_extraction_status()` — async extraction with polling
- `get_texts(page, page_size, search, category)` → paginated text list
- `update_text(offset, new_text)` — updates ZH_CN column in CSV only
- `apply_changes()` — repacks CSV → LOCALIZE_.DAT → game
- `restore_original()` — re-exports from template, overwrites CSV and DAT
- `export_localize_dat()` — opens Save dialog to export current LOCALIZE_.DAT
- `activate_mods(folder_names)` / `get_mod_status()` — async MOD activation with polling
- `restore_all_mods()` — deletes game folders, renames backups back
- `restore_all_files()` — restores EXE from backup + calls `restore_all_mods()`
- `delete_mod(folder_name)` — removes MOD folder from MODS/

### CSV Data Structure
- 6 language columns: JPN, US, ZH_CN, ZH_TW, KO, ES
- Special line break markers: `[n_rn]` (CRLF), `[n_nr]` (LF)
- Text classification column added by `text_classifier.py`
- Pandas DataFrame used for all CSV operations
