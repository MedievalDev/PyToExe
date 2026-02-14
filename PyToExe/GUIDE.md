# 📘 Python to EXE Converter — User Guide

Step-by-step guide for converting your Python scripts to standalone Windows executables.

---

## Getting Started

### 1. Install Python

If you don't have Python installed:
1. Download from [python.org](https://www.python.org/downloads/) (3.10 or higher)
2. During installation, check **"Add Python to PATH"** — this is important
3. Verify: open a terminal and run `python --version`

### 2. Download the Converter

Download or clone the repository, then run:
```bash
python py2exe_converter.py
```

On first launch, the tool will install PyQt6 automatically if it's missing. Once installed, the GUI opens.

---

## Your First Build

### Step 1 — Select Your Script

Click the 📁 button next to **Python Script** and navigate to your `.py` file. The output folder and EXE name are auto-filled based on your selection.

### Step 2 — Review the Settings

- **Output Folder** — where the EXE will be created. Change it if you want the result somewhere else.
- **EXE Name** — the filename of your executable (without `.exe`). Change it if you want a different name than the script.
- **Icon** *(optional)* — pick any image file. PNG, JPG, and BMP are converted to ICO automatically.

### Step 3 — Set Options

All options are enabled by default. For a first build, the defaults work well. See the next section for details on each option.

### Step 4 — Build

Click **🔨 Build EXE**. The build log shows PyInstaller's live output. A typical build takes 30 seconds to a few minutes depending on your script's dependencies.

When finished, you'll see either:
- ✅ **BUILD SUCCESSFUL** — your EXE is ready
- ❌ **BUILD FAILED** — check the log for error details

---

## Options Explained

### One File (`--onefile`)
Packs everything — your script, all imported libraries, and the Python runtime — into a single `.exe` file. This is the most convenient option for distribution. Without it, PyInstaller creates a folder with the EXE plus many supporting DLLs and files.

**When to disable:** If your app is very large or startup time matters (onefile EXEs need to unpack on every launch).

### No Console (`--windowed`)
Hides the black console window that normally appears behind your app.

**When to disable:** If your script is a command-line tool, or if you're debugging — the console shows error messages that would otherwise be invisible.

### Clean Build (`--clean`)
Deletes PyInstaller's cache and temp files before building. This ensures a fresh build every time.

**When to disable:** Rarely. Turning this off can speed up repeated builds slightly, but stale cache can cause issues.

### Open Folder
Opens the output folder in Windows Explorer after a successful build so you can find your EXE immediately.

### Organize Project
Creates a clean project structure after the build:

```
YourOutputFolder/
└── MyApp/
    ├── MyApp.exe          ← your executable
    └── py_file/
        └── my_app.py      ← copy of your source script
```

It also removes build artifacts (the `build/` folder and `.spec` file) automatically.

**When to disable:** If you want the raw PyInstaller output without reorganization.

### Desktop Shortcut
Creates a `.lnk` shortcut on your Windows desktop pointing to the built EXE. Uses PowerShell internally.

**When to disable:** If you don't need quick access from the desktop.

---

## Icon Conversion

The tool accepts these image formats for your EXE icon:
- `.ico` — used directly
- `.png`, `.jpg`, `.jpeg`, `.bmp` — auto-converted to `.ico` using Pillow

The converter generates a multi-size ICO containing 16×16, 32×32, 48×48, 64×64, 128×128, and 256×256 pixel versions. This ensures your icon looks crisp in the taskbar, file explorer, and desktop.

> **Tip:** For best results, use a square PNG with a transparent background at 256×256 or larger.

If Pillow is not installed, the tool installs it automatically before converting.

---

## Troubleshooting

### PyInstaller Not Found
When you click Build for the first time, the tool checks for PyInstaller. If it's missing, a dialog asks whether to install it. Click **Yes** and it will be installed via pip. If that fails, run manually:
```bash
pip install pyinstaller
```

### Antivirus Blocks the EXE
This is the most common issue. PyInstaller-built executables are frequently flagged as false positives by antivirus software because they contain an embedded Python runtime. Solutions:
- Add the output folder to your antivirus exclusions
- Submit the file as a false positive to your AV vendor
- This is a known industry-wide issue, not specific to this tool

### Build Fails with ModuleNotFoundError
PyInstaller sometimes can't detect all imports automatically, especially for packages that use dynamic imports. Check the build log for which module is missing, then either:
- Add `--hidden-import=modulename` to your PyInstaller command manually
- Create a `.spec` file with the required hidden imports

### EXE Is Very Large
PyInstaller bundles your entire Python environment. If you have many packages installed globally, they may all end up in the EXE. Solution:
1. Create a virtual environment: `python -m venv myenv`
2. Activate it: `myenv\Scripts\activate`
3. Install only what your script needs: `pip install <packages>`
4. Run the converter from within the virtual environment

### EXE Crashes Immediately / Console Flashes
Your script is likely throwing an error at startup. To see it:
1. Disable **No Console** (`--windowed`) in the options
2. Rebuild
3. Run the EXE from a terminal: `cmd → cd to folder → MyApp.exe`
4. The error message will be visible in the console

### "Failed to execute script" Error
Common causes:
- Missing data files that your script expects at runtime
- Path issues — use `sys._MEIPASS` for bundled resources in onefile mode
- Missing DLLs for compiled extensions

---

## Tips & Best Practices

1. **Always test from a virtual environment** — keeps your EXE small and avoids bundling unrelated packages.

2. **Use `--windowed` only for GUI apps** — console apps need the terminal window for input/output.

3. **Keep your icon square** — non-square images get stretched during ICO conversion.

4. **Check the build log** — even successful builds can have warnings about missing modules that might cause runtime issues.

5. **Version your builds** — use the EXE Name field to include version numbers (e.g. `MyApp_v1.2`) so you don't overwrite previous builds.

6. **Test the EXE on a clean machine** — or at least on a machine without Python installed — to verify all dependencies are properly bundled.
