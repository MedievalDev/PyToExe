#!/usr/bin/env python3
"""
Python to EXE Converter
Einfaches GUI Tool zum Konvertieren von Python Scripts zu EXE Dateien.
"""

import sys
import os
import subprocess
import threading

# Abhängigkeiten prüfen
def check_dependencies():
    missing = []
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")
    
    if missing:
        print(f"Installiere fehlende Pakete: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("Installation abgeschlossen. Bitte Programm neu starten.")
        sys.exit(0)

check_dependencies()

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QLineEdit, QTextEdit,
    QProgressBar, QCheckBox, QGroupBox, QGridLayout, QMessageBox,
    QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QProcess
from PyQt6.QtGui import QFont, QColor, QTextCursor


DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #4ec9b0;
}
QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 8px;
    color: #d4d4d4;
}
QLineEdit:focus {
    border-color: #0e639c;
}
QLineEdit:read-only {
    background-color: #2d2d2d;
    color: #909090;
}
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1177bb;
}
QPushButton:pressed {
    background-color: #094771;
}
QPushButton:disabled {
    background-color: #3d3d3d;
    color: #6d6d6d;
}
QPushButton#browse_btn {
    background-color: #3d3d3d;
    min-width: 40px;
    max-width: 40px;
}
QPushButton#browse_btn:hover {
    background-color: #4d4d4d;
}
QPushButton#build_btn {
    background-color: #2ea043;
    font-size: 12pt;
    padding: 12px 24px;
}
QPushButton#build_btn:hover {
    background-color: #3fb950;
}
QPushButton#cancel_btn {
    background-color: #b34040;
}
QPushButton#cancel_btn:hover {
    background-color: #d44040;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #5a5a5a;
    background-color: #2d2d2d;
}
QCheckBox::indicator:checked {
    background-color: #2ea043;
    border-color: #2ea043;
}
QCheckBox::indicator:unchecked {
    background-color: #2d2d2d;
    border-color: #5a5a5a;
}
QCheckBox::indicator:unchecked:hover {
    border-color: #0e639c;
}
QCheckBox::indicator:checked:hover {
    background-color: #3fb950;
    border-color: #3fb950;
}
QTextEdit {
    background-color: #1a1a1a;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    color: #d4d4d4;
}
QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    text-align: center;
    background-color: #252526;
    height: 25px;
}
QProgressBar::chunk {
    background-color: #0e639c;
    border-radius: 3px;
}
QLabel#status_label {
    color: #4ec9b0;
    font-weight: bold;
}
QLabel#title_label {
    font-size: 18pt;
    font-weight: bold;
    color: #4ec9b0;
}
QLabel#subtitle_label {
    color: #808080;
    font-size: 9pt;
}
QFrame#separator {
    background-color: #3d3d3d;
    max-height: 1px;
}
"""


class BuildWorker(QThread):
    """Worker Thread für den Build-Prozess"""
    output = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, script_path, output_dir, exe_name, options):
        super().__init__()
        self.script_path = script_path
        self.output_dir = output_dir
        self.exe_name = exe_name
        self.options = options
        self.process = None
        self._cancelled = False
    
    def run(self):
        try:
            # PyInstaller Befehl zusammenbauen
            cmd = [sys.executable, "-m", "PyInstaller"]
            
            # Optionen
            if self.options.get("onefile"):
                cmd.append("--onefile")
            
            if self.options.get("windowed"):
                cmd.append("--windowed")
            
            if self.options.get("clean"):
                cmd.append("--clean")
            
            if self.exe_name:
                cmd.extend(["--name", self.exe_name])
            
            if self.output_dir:
                cmd.extend(["--distpath", self.output_dir])
            
            # Icon falls angegeben
            if self.options.get("icon"):
                cmd.extend(["--icon", self.options["icon"]])
            
            # Zusätzliche Optionen
            if self.options.get("noconsole"):
                cmd.append("--noconsole")
            
            # Script
            cmd.append(self.script_path)
            
            self.output.emit(f"Starte Build...\n")
            self.output.emit(f"Befehl: {' '.join(cmd)}\n")
            self.output.emit("-" * 50 + "\n")
            
            # Prozess starten
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Output lesen
            for line in self.process.stdout:
                if self._cancelled:
                    self.process.terminate()
                    self.finished.emit(False, "Abgebrochen")
                    return
                self.output.emit(line)
            
            self.process.wait()
            
            if self.process.returncode == 0:
                exe_path = os.path.join(
                    self.output_dir or "dist",
                    (self.exe_name or os.path.splitext(os.path.basename(self.script_path))[0]) + ".exe"
                )
                self.finished.emit(True, exe_path)
            else:
                self.finished.emit(False, f"Build fehlgeschlagen (Code: {self.process.returncode})")
                
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def cancel(self):
        self._cancelled = True
        if self.process:
            self.process.terminate()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Python to EXE Converter")
        self.setMinimumSize(700, 650)
        self.setStyleSheet(DARK_STYLE)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("🐍 Python to EXE Converter")
        title.setObjectName("title_label")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Konvertiere Python Scripts zu Windows Executables mit PyInstaller")
        subtitle.setObjectName("subtitle_label")
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)
        
        # Input Gruppe
        input_group = QGroupBox("Eingabe")
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(10)
        
        # Python Script
        input_layout.addWidget(QLabel("Python Script:"), 0, 0)
        self.script_input = QLineEdit()
        self.script_input.setPlaceholderText("Wähle ein .py Script...")
        self.script_input.textChanged.connect(self.on_script_changed)
        input_layout.addWidget(self.script_input, 0, 1)
        
        script_btn = QPushButton("📁")
        script_btn.setObjectName("browse_btn")
        script_btn.clicked.connect(self.browse_script)
        input_layout.addWidget(script_btn, 0, 2)
        
        # Icon (optional)
        input_layout.addWidget(QLabel("Icon (optional):"), 1, 0)
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Optional: .ico Datei für das EXE Icon")
        input_layout.addWidget(self.icon_input, 1, 1)
        
        icon_btn = QPushButton("📁")
        icon_btn.setObjectName("browse_btn")
        icon_btn.clicked.connect(self.browse_icon)
        input_layout.addWidget(icon_btn, 1, 2)
        
        layout.addWidget(input_group)
        
        # Output Gruppe
        output_group = QGroupBox("Ausgabe")
        output_layout = QGridLayout(output_group)
        output_layout.setSpacing(10)
        
        # Output Ordner
        output_layout.addWidget(QLabel("Ausgabe Ordner:"), 0, 0)
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Ordner für die EXE Datei...")
        output_layout.addWidget(self.output_input, 0, 1)
        
        output_btn = QPushButton("📁")
        output_btn.setObjectName("browse_btn")
        output_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(output_btn, 0, 2)
        
        # EXE Name
        output_layout.addWidget(QLabel("EXE Name:"), 1, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name der EXE (ohne .exe)")
        output_layout.addWidget(self.name_input, 1, 1, 1, 2)
        
        layout.addWidget(output_group)
        
        # Optionen Gruppe
        options_group = QGroupBox("Optionen")
        options_layout = QVBoxLayout(options_group)
        
        # Checkboxen in zwei Spalten
        checks_layout = QHBoxLayout()
        
        left_checks = QVBoxLayout()
        self.onefile_check = QCheckBox("  Eine Datei (--onefile)")
        self.onefile_check.setChecked(True)
        self.onefile_check.setToolTip("Alles in eine einzige EXE packen")
        self.onefile_check.stateChanged.connect(lambda: self.update_checkbox_style(self.onefile_check))
        self.update_checkbox_style(self.onefile_check)
        left_checks.addWidget(self.onefile_check)
        
        self.windowed_check = QCheckBox("  Kein Konsolenfenster (--windowed)")
        self.windowed_check.setChecked(True)
        self.windowed_check.setToolTip("Versteckt das schwarze Konsolenfenster bei GUI Apps")
        self.windowed_check.stateChanged.connect(lambda: self.update_checkbox_style(self.windowed_check))
        self.update_checkbox_style(self.windowed_check)
        left_checks.addWidget(self.windowed_check)
        
        checks_layout.addLayout(left_checks)
        
        right_checks = QVBoxLayout()
        self.clean_check = QCheckBox("  Clean Build (--clean)")
        self.clean_check.setChecked(True)
        self.clean_check.setToolTip("Löscht temporäre Dateien vor dem Build")
        self.clean_check.stateChanged.connect(lambda: self.update_checkbox_style(self.clean_check))
        self.update_checkbox_style(self.clean_check)
        right_checks.addWidget(self.clean_check)
        
        self.open_folder_check = QCheckBox("  Ordner nach Build öffnen")
        self.open_folder_check.setChecked(True)
        self.open_folder_check.stateChanged.connect(lambda: self.update_checkbox_style(self.open_folder_check))
        self.update_checkbox_style(self.open_folder_check)
        right_checks.addWidget(self.open_folder_check)
        
        checks_layout.addLayout(right_checks)
        options_layout.addLayout(checks_layout)
        
        # Zweite Reihe Optionen
        checks_layout2 = QHBoxLayout()
        
        left_checks2 = QVBoxLayout()
        self.organize_check = QCheckBox("  Projekt organisieren (py_file Ordner)")
        self.organize_check.setChecked(True)
        self.organize_check.setToolTip("Erstellt Unterordner und räumt auf: EXE im Hauptordner, .py in py_file/")
        self.organize_check.stateChanged.connect(lambda: self.update_checkbox_style(self.organize_check))
        self.update_checkbox_style(self.organize_check)
        left_checks2.addWidget(self.organize_check)
        
        checks_layout2.addLayout(left_checks2)
        
        right_checks2 = QVBoxLayout()
        self.shortcut_check = QCheckBox("  Desktop-Verknüpfung erstellen")
        self.shortcut_check.setChecked(True)
        self.shortcut_check.setToolTip("Erstellt eine Verknüpfung auf dem Desktop")
        self.shortcut_check.stateChanged.connect(lambda: self.update_checkbox_style(self.shortcut_check))
        self.update_checkbox_style(self.shortcut_check)
        right_checks2.addWidget(self.shortcut_check)
        
        checks_layout2.addLayout(right_checks2)
        options_layout.addLayout(checks_layout2)
        
        layout.addWidget(options_group)
        
        # Build Button
        btn_layout = QHBoxLayout()
        
        self.build_btn = QPushButton("🔨  Build EXE")
        self.build_btn.setObjectName("build_btn")
        self.build_btn.clicked.connect(self.start_build)
        self.build_btn.setEnabled(False)
        btn_layout.addWidget(self.build_btn)
        
        self.cancel_btn = QPushButton("✖  Abbrechen")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.cancel_build)
        self.cancel_btn.setVisible(False)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Status
        self.status_label = QLabel("Bereit")
        self.status_label.setObjectName("status_label")
        layout.addWidget(self.status_label)
        
        # Log Output
        log_group = QGroupBox("Build Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(150)
        log_layout.addWidget(self.log_output)
        
        clear_log_btn = QPushButton("Log leeren")
        clear_log_btn.clicked.connect(self.log_output.clear)
        log_layout.addWidget(clear_log_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(log_group)
    
    def update_checkbox_style(self, checkbox):
        """Aktualisiert Checkbox-Text mit Häkchen oder X"""
        text = checkbox.text()
        # Entferne alte Symbole
        text = text.replace("✓ ", "").replace("✗ ", "").strip()
        
        if checkbox.isChecked():
            checkbox.setText(f"✓  {text}")
            checkbox.setStyleSheet("color: #4caf50; font-weight: bold;")
        else:
            checkbox.setText(f"✗  {text}")
            checkbox.setStyleSheet("color: #808080;")
    
    def organize_project(self, exe_path, script_path, output_dir):
        """Organisiert das Projekt: Erstellt Ordner mit EXE-Namen, EXE rein, .py in py_file/"""
        try:
            import shutil
            
            exe_name = os.path.basename(exe_path)
            base_name = os.path.splitext(exe_name)[0]
            script_name = os.path.basename(script_path)
            
            # Hauptordner mit EXE-Namen erstellen
            project_folder = os.path.join(output_dir, base_name)
            os.makedirs(project_folder, exist_ok=True)
            
            # py_file Unterordner erstellen
            py_folder = os.path.join(project_folder, "py_file")
            os.makedirs(py_folder, exist_ok=True)
            
            # EXE in den Projektordner verschieben
            new_exe_path = os.path.join(project_folder, exe_name)
            if os.path.exists(exe_path) and os.path.abspath(exe_path) != os.path.abspath(new_exe_path):
                shutil.move(exe_path, new_exe_path)
                self.log_output.append(f"📦 EXE verschoben nach: {new_exe_path}\n")
            
            # Python-Datei kopieren
            dest_py = os.path.join(py_folder, script_name)
            if os.path.abspath(script_path) != os.path.abspath(dest_py):
                shutil.copy2(script_path, dest_py)
                self.log_output.append(f"📁 Python-Datei kopiert nach: {dest_py}\n")
            
            # Build-Ordner löschen
            build_folder = os.path.join(os.getcwd(), "build")
            if os.path.exists(build_folder):
                shutil.rmtree(build_folder)
                self.log_output.append(f"🗑️ Build-Ordner gelöscht\n")
            
            # .spec Datei löschen
            spec_file = os.path.join(os.getcwd(), f"{base_name}.spec")
            if os.path.exists(spec_file):
                os.remove(spec_file)
                self.log_output.append(f"🗑️ Spec-Datei gelöscht\n")
            
            # Auch im Output-Ordner aufräumen falls dort
            build_folder2 = os.path.join(output_dir, "build")
            if os.path.exists(build_folder2):
                shutil.rmtree(build_folder2)
            
            spec_file2 = os.path.join(output_dir, f"{base_name}.spec")
            if os.path.exists(spec_file2):
                os.remove(spec_file2)
            
            self.log_output.append(f"✅ Projekt organisiert in: {project_folder}\n")
            
            # Neuen EXE-Pfad zurückgeben für Verknüpfung
            return new_exe_path
            
        except Exception as e:
            self.log_output.append(f"⚠️ Fehler beim Organisieren: {e}\n")
            return exe_path
    
    def create_desktop_shortcut(self, exe_path):
        """Erstellt eine Desktop-Verknüpfung zur EXE"""
        try:
            import winreg
            
            # Desktop-Pfad ermitteln
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            desktop = winreg.QueryValueEx(key, "Desktop")[0]
            winreg.CloseKey(key)
            
            exe_name = os.path.splitext(os.path.basename(exe_path))[0]
            shortcut_path = os.path.join(desktop, f"{exe_name}.lnk")
            
            # PowerShell verwenden um Verknüpfung zu erstellen
            ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{exe_path}"
$Shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
$Shortcut.Save()
'''
            
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                check=True
            )
            
            self.log_output.append(f"🔗 Desktop-Verknüpfung erstellt: {shortcut_path}\n")
            
        except Exception as e:
            self.log_output.append(f"⚠️ Fehler bei Verknüpfung: {e}\n")

    def browse_script(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Python Script wählen",
            "",
            "Python Scripts (*.py);;Alle Dateien (*.*)"
        )
        if path:
            self.script_input.setText(path)
            
            # Auto-fill output und name
            if not self.output_input.text():
                self.output_input.setText(os.path.dirname(path))
            if not self.name_input.text():
                base_name = os.path.splitext(os.path.basename(path))[0]
                self.name_input.setText(base_name)
    
    def browse_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Icon wählen",
            "",
            "Bilder (*.ico *.png *.jpg *.jpeg *.bmp);;Icon Dateien (*.ico);;Alle Dateien (*.*)"
        )
        if path:
            self.icon_input.setText(path)
    
    def convert_to_ico(self, image_path):
        """Konvertiert PNG/JPG/BMP zu ICO falls nötig"""
        if image_path.lower().endswith('.ico'):
            return image_path
        
        try:
            from PIL import Image
            
            self.log_output.append(f"Konvertiere {os.path.basename(image_path)} zu ICO...\n")
            
            img = Image.open(image_path)
            
            # RGBA für Transparenz
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Verschiedene Größen für ICO (Windows erwartet mehrere)
            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            
            # Temporäre ICO Datei erstellen
            ico_path = os.path.join(
                os.path.dirname(image_path),
                os.path.splitext(os.path.basename(image_path))[0] + "_converted.ico"
            )
            
            # Beste Qualität beim Resizen
            icons = []
            for size in sizes:
                resized = img.resize(size, Image.LANCZOS)
                icons.append(resized)
            
            # Als ICO speichern
            icons[0].save(
                ico_path,
                format='ICO',
                sizes=[(s, s) for s, _ in sizes]
            )
            
            self.log_output.append(f"✅ Icon erstellt: {ico_path}\n")
            return ico_path
            
        except ImportError:
            self.log_output.append("⚠️ Pillow nicht installiert, installiere...\n")
            subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"])
            return self.convert_to_ico(image_path)
        except Exception as e:
            self.log_output.append(f"⚠️ Icon-Konvertierung fehlgeschlagen: {e}\n")
            return None
    
    def browse_output(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Ausgabe Ordner wählen"
        )
        if path:
            self.output_input.setText(path)
    
    def on_script_changed(self, text):
        self.build_btn.setEnabled(bool(text and os.path.isfile(text)))
    
    def start_build(self):
        script = self.script_input.text()
        
        if not script or not os.path.isfile(script):
            QMessageBox.warning(self, "Fehler", "Bitte wähle ein gültiges Python Script.")
            return
        
        # PyInstaller prüfen
        try:
            subprocess.run(
                [sys.executable, "-m", "PyInstaller", "--version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            reply = QMessageBox.question(
                self,
                "PyInstaller nicht gefunden",
                "PyInstaller ist nicht installiert.\n\nJetzt installieren?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.log_output.append("Installiere PyInstaller...\n")
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
                self.log_output.append("PyInstaller installiert!\n\n")
            else:
                return
        
        # Icon konvertieren falls nötig
        icon_path = self.icon_input.text() if self.icon_input.text() else None
        if icon_path and not icon_path.lower().endswith('.ico'):
            icon_path = self.convert_to_ico(icon_path)
        
        # Optionen sammeln
        options = {
            "onefile": self.onefile_check.isChecked(),
            "windowed": self.windowed_check.isChecked(),
            "clean": self.clean_check.isChecked(),
            "icon": icon_path
        }
        
        # UI anpassen
        self.build_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.progress.setVisible(True)
        self.status_label.setText("Build läuft...")
        self.log_output.clear()
        
        # Worker starten
        self.worker = BuildWorker(
            script,
            self.output_input.text(),
            self.name_input.text(),
            options
        )
        self.worker.output.connect(self.on_build_output)
        self.worker.finished.connect(self.on_build_finished)
        self.worker.start()
    
    def cancel_build(self):
        if self.worker:
            self.worker.cancel()
            self.status_label.setText("Abbrechen...")
    
    def on_build_output(self, text):
        self.log_output.insertPlainText(text)
        # Auto-scroll
        cursor = self.log_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_output.setTextCursor(cursor)
    
    def on_build_finished(self, success, message):
        self.build_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.progress.setVisible(False)
        
        if success:
            exe_path = message
            
            # Projekt organisieren
            if self.organize_check.isChecked():
                exe_path = self.organize_project(
                    exe_path,
                    self.script_input.text(),
                    self.output_input.text() or os.path.dirname(self.script_input.text())
                )
            
            # Desktop-Verknüpfung erstellen
            if self.shortcut_check.isChecked():
                self.create_desktop_shortcut(exe_path)
            
            self.status_label.setText(f"✅ Erfolgreich: {os.path.basename(exe_path)}")
            self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            
            self.log_output.append("\n" + "=" * 50)
            self.log_output.append(f"✅ BUILD ERFOLGREICH!")
            self.log_output.append(f"📁 EXE Datei: {exe_path}")
            self.log_output.append("=" * 50 + "\n")
            
            # Ordner öffnen
            if self.open_folder_check.isChecked():
                folder = os.path.dirname(exe_path)
                if os.path.exists(folder):
                    os.startfile(folder)
        else:
            self.status_label.setText(f"❌ Fehler: {message}")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            
            self.log_output.append("\n" + "=" * 50)
            self.log_output.append(f"❌ BUILD FEHLGESCHLAGEN: {message}")
            self.log_output.append("=" * 50 + "\n")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
