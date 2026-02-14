# 🐍 Python to EXE Converter

Simple GUI tool for converting Python scripts to Windows executables using PyInstaller.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## Overview

Python to EXE Converter provides a clean, dark-themed GUI for building Windows executables from Python scripts. It wraps PyInstaller with a user-friendly interface, handles icon conversion automatically, organizes your output into a clean project folder, and can create a desktop shortcut — all in one click.

**Key Features:**
- 🔨 **One-Click Build** — select a `.py` file, click Build, done
- 📦 **Single EXE** — packages everything into one standalone executable (`--onefile`)
- 🎨 **Icon Conversion** — accepts PNG, JPG, BMP and auto-converts to multi-size ICO
- 📁 **Project Organization** — creates a clean folder structure with EXE + source backup
- 🔗 **Desktop Shortcut** — optional shortcut creation via PowerShell
- 📋 **Real-Time Build Log** — live PyInstaller output with auto-scroll
- ⚡ **Auto-Install** — installs PyQt6 and PyInstaller automatically if missing
- 🌙 **Dark Theme** — VS Code-inspired dark UI

---

## Screenshot

*Coming soon*

---

## Installation

### Requirements
- Python 3.10 or higher
- Windows (for PyInstaller EXE output, shortcuts, and DPI awareness)

### Setup

1. Download or clone this repository
2. Run:
```bash
python py2exe_converter.py
```

On first launch, the tool checks for PyQt6 and installs it automatically if missing. PyInstaller is checked when you start your first build.

---

## Usage

1. **Select Script** — click 📁 to choose your `.py` file
2. **Set Output** — choose an output folder (defaults to script location)
3. **Name** — set the EXE name (auto-filled from script name)
4. **Icon** *(optional)* — select any image file (PNG, JPG, BMP, ICO)
5. **Options** — toggle checkboxes as needed
6. **Build** — click 🔨 Build EXE and watch the log

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| One File (`--onefile`) | ✅ On | Packs everything into a single EXE |
| No Console (`--windowed`) | ✅ On | Hides the console window — use for GUI apps only |
| Clean Build (`--clean`) | ✅ On | Removes temp files before building |
| Open Folder | ✅ On | Opens the output folder after a successful build |
| Organize Project | ✅ On | Creates a named folder with EXE + `py_file/` subfolder for source |
| Desktop Shortcut | ✅ On | Creates a `.lnk` shortcut on your desktop |

---

## Icon Conversion

You don't need to convert your icon to `.ico` manually. The tool accepts PNG, JPG, JPEG, and BMP files and converts them automatically using Pillow. The generated ICO includes all standard Windows sizes (16×16 through 256×256) for crisp display at any resolution.

> Pillow is installed automatically if needed.

---

## Project Structure

With **Organize Project** enabled, the output looks like this:

```
YourOutputFolder/
└── MyApp/
    ├── MyApp.exe
    └── py_file/
        └── my_app.py
```

Build artifacts (`build/` folder, `.spec` file) are cleaned up automatically.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| PyInstaller not found | Click **Yes** when prompted to install, or run `pip install pyinstaller` |
| Antivirus blocks EXE | Add the output folder to your AV exclusions — false positives are common with PyInstaller |
| Build fails with import errors | Some packages need `--hidden-import` flags — check the build log for details |
| EXE is very large | PyInstaller bundles your entire Python environment; use a virtual env with only required packages |
| Console flashes and closes | Your script probably crashes — remove `--windowed` to see the error output |

---

## Credits

**Development**
- **MedievalDev** — Python to EXE Converter
- **Claude (Anthropic)** — Development assistance

**Built with**
- [PyInstaller](https://pyinstaller.org/) — EXE packaging
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — GUI framework
- [Pillow](https://python-pillow.org/) — Icon conversion

---

## License

MIT License — see [LICENSE](LICENSE) for details.
