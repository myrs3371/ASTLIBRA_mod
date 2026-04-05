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
│   └── ASTLIBRA_Dec.exe # DAT.dxa unpacker
```

## Key Workflows

### Text Extraction Pipeline (First Run)
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
- On activation: iterates through `Config.DATA_LIST` folders, copies matching subfolders from MOD to game directory using `shutil.copytree(..., dirs_exist_ok=True)`
- Supports batch activation (multiple MODs at once)
- On restore: deletes game folders from `Config.DATA_LIST` and re-extracts from `DAT_BACK.dxa`

## Path Management

The `Config` class centralizes all path logic:
- Auto-detects game directory by searching for `ASTLIBRA.exe` + `DATA/`
- Tool must be placed in a subdirectory of the game folder
- All paths resolve relative to detected game root
- `Config.DATA_LIST = ['Image', 'Image2K', 'Image4K', 'Image720p', 'Sound', 'DAT']` - defines game data folders used by MOD system

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
- Tool modifies game files - always creates backups (`DAT_BACK.dxa`, EXE `.backup`)
- First run triggers automatic extraction pipeline
- CSV is the source of truth for text editing
- MOD system uses JSON manifests (`mod_info.json`) for metadata
- Vue.js bundled locally (`web/js/vue.global.prod.js`) to eliminate CDN load delays
- pywebview uses `edgechromium` backend (see [main.py:38](main.py#L38))

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
- [backend/services/text_extractor.py](backend/services/text_extractor.py) - 5-step extraction pipeline
- [backend/services/text_importer.py](backend/services/text_importer.py) - Text import/revert logic
- [backend/services/mod_manager.py](backend/services/mod_manager.py) - MOD activation/restore logic
- [ASTLIBRA_MOD_TOOL.spec](ASTLIBRA_MOD_TOOL.spec) - PyInstaller build configuration (root level, not inside a subdirectory)

## Development Notes

### Python-JavaScript Communication
- All Python methods in `Api` class are automatically exposed to JavaScript
- Methods must be synchronous or use threading for async operations
- Return values are automatically serialized to JSON
- Frontend accesses via `window.pywebview.api.method_name()`

### CSV Data Structure
- 6 language columns: JPN, US, ZH_CN, ZH_TW, KO, ES
- Special line break markers: `[n_rn]` (CRLF), `[n_nr]` (LF)
- Text classification column added by `text_classifier.py`
- Pandas DataFrame used for all CSV operations
