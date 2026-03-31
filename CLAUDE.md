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
Output: `dist/ASTLIBRA_MOD_TOOL.exe`

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
astlibra_mod_tool/
├── main.py                    # Entry point - creates pywebview window
├── config.py                  # Path management and game directory detection
├── web/                       # Vue 3 frontend
│   ├── index.html
│   └── js/
│       ├── app.js            # Vue app initialization and routing
│       └── pages/            # Page components (home, dialogue, mod)
├── frontend/api.py            # pywebview JS API bridge
├── backend/services/          # Business logic
│   ├── game_manager.py       # Game directory detection
│   ├── text_extractor.py     # Text extraction pipeline
│   ├── text_importer.py      # Text import pipeline
│   └── mod_manager.py        # MOD activation/deactivation
└── core/                      # Binary processing tools
    ├── _ALOC.py              # ALOC format packer/unpacker
    ├── patch_exe.py          # Game EXE patcher
    ├── text_classifier.py    # Text classification
    └── ASTLIBRA_Dec.exe      # DAT.dxa unpacker
```

## Key Workflows

### Text Extraction Pipeline (First Run)
1. Unpack `DAT.dxa` using `ASTLIBRA_Dec.exe` → `DAT/` folder
2. Patch game EXE (byte replacement to enable text reading)
3. Extract text from `LOCALIZE_.DAT` using `_ALOC.py` → CSV
4. Repack as DAT format

### Text Editing Flow
1. Web UI fetches data from Python backend via JS API
2. User edits text in Vue components
3. Changes sent to Python API → saved to CSV
4. Import pipeline repacks CSV → `LOCALIZE_.DAT` → game files

### MOD System
- File-based override system in `MODS/` directory
- Each MOD is a folder containing `mod_info.json` + replacement files
- On activation: copies files to game directory, backs up originals with `.original` suffix
- On restore: deletes game folders (DAT, Image, Image2K, Sound, Image4K, Image720p) and re-extracts from `DAT_BACK.dxa`
- Features: scan/display, activate, restore

## Path Management

The `Config` class centralizes all path logic:
- Auto-detects game directory by searching for `ASTLIBRA.exe` + `DATA/`
- Tool must be placed in a subdirectory of the game folder
- All paths resolve relative to detected game root

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
- `_ALOC.py` handles custom ALOC binary format (struct-based parsing)
- Text encoding: UTF-8 with special markers `[n_rn]` (CRLF) and `[n_nr]` (LF)
- 6 language columns: JPN, US, ZH_CN, ZH_TW, KO, ES

### Threading Model
- Long-running operations (extraction, import) run in background threads
- Python API methods start threads and return immediately
- Frontend polls status via API calls (e.g., `get_extraction_status()`)
- Never blocks UI thread directly

### File Operations
- Tool modifies game files - always creates backups (`DAT_BACK.dxa`, EXE `.backup`)
- First run triggers automatic extraction pipeline
- CSV is the source of truth for text editing
- MOD system uses JSON manifests (`mod_info.json`) for metadata
- Vue.js bundled locally (`web/js/vue.global.prod.js`) to eliminate CDN load delays

## Key Files

- [main.py](main.py) - Application entry point, creates pywebview window
- [frontend/api.py](frontend/api.py) - Python API exposed to JavaScript
- [web/js/app.js](web/js/app.js) - Vue 3 app initialization and routing
- [config.py](config.py) - Path management and game directory detection
- [core/_ALOC.py](core/_ALOC.py) - Binary format parser for game text files
- [backend/services/mod_manager.py](backend/services/mod_manager.py) - MOD activation/restore logic
- [ASTLIBRA_MOD_TOOL.spec](ASTLIBRA_MOD_TOOL.spec) - PyInstaller build configuration
