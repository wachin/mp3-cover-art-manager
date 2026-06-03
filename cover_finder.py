#!/usr/bin/env python3
"""
MP3 Cover Art Manager - PyQt6 GUI

Busca y agrega portadas a archivos MP3 usando iTunes y Deezer APIs.
Basado en agregar_caratulas.py y recuperar_portadas.py.
"""

import re
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus

import requests
from PyQt6.QtCore import Qt, QCoreApplication, QThread, pyqtSignal, QTranslator, QLocale
from PyQt6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
    QCheckBox,
    QProgressBar,
    QDialog,
)

try:
    from PyQt6.QtSvg import QSvgWidget
    SVG_SUPPORT = True
except ImportError:
    SVG_SUPPORT = False
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from mutagen.mp3 import MP3

APP_NAME = "MP3 Cover Art Manager"
APP_VERSION = "1.0.0"
DEVELOPER = "Washington Indacochea Delgado"
DEVELOPER_EMAIL = "linuxfrontier@proton.me"
COPYRIGHT = "© 2026 Washington Indacochea Delgado"
LICENSE = "GPL3"


def tr(text, disambiguation=None):
    return QCoreApplication.translate("CoverArtApp", text, disambiguation)


# -----------------------------------------------------------------------------
# Cover search logic (from recuperar_portadas.py)
# -----------------------------------------------------------------------------

def norm(text):
    text = (text or "").lower()
    repl = str.maketrans("áéíóúüñ", "aeiouun")
    text = text.translate(repl)
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def tokens(text):
    return set(norm(text).split())


def split_filename(path):
    stem = path.stem
    stem = re.sub(r"\s+", " ", stem).strip()
    if " - " in stem:
        a, b = stem.rsplit(" - ", 1)
        return a.strip(), b.strip()
    m = re.match(r"(.+?)\(([^)]+)\)(.*)", stem)
    if m:
        title = (m.group(1) + " " + m.group(3)).strip()
        return title, m.group(2).strip()
    return stem, ""


def read_tags(path):
    audio = MP3(path)
    tags = audio.tags or {}
    title = str(tags.get("TIT2", "")).strip()
    artist = str(tags.get("TPE1", "")).strip()
    album = str(tags.get("TALB", "")).strip()
    if not title or not artist:
        f_title, f_artist = split_filename(path)
        title = title or f_title
        artist = artist or f_artist
    return title, artist, album


def score_candidate(want_title, want_artist, cand_title, cand_artist):
    title_tokens = tokens(want_title)
    artist_tokens = tokens(want_artist)
    cand_title_tokens = tokens(cand_title)
    cand_artist_tokens = tokens(cand_artist)

    if not title_tokens:
        return 0

    title_score = len(title_tokens & cand_title_tokens) / len(title_tokens)
    if artist_tokens:
        artist_score = len(artist_tokens & cand_artist_tokens) / len(artist_tokens)
    else:
        artist_score = 0.45

    bonus = 0.0
    if norm(want_title) and norm(want_title) in norm(cand_title):
        bonus += 0.15
    if norm(want_artist) and norm(want_artist) in norm(cand_artist):
        bonus += 0.15

    return min(1.0, title_score * 0.65 + artist_score * 0.35 + bonus)


def request_json(session, url, sleep=0.2):
    time.sleep(sleep)
    r = session.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def itunes_candidates(session, title, artist):
    query = quote_plus(f"{title} {artist}".strip())
    url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=8"
    data = request_json(session, url)
    out = []
    for item in data.get("results", []):
        artwork = item.get("artworkUrl100")
        if not artwork:
            continue
        artwork = re.sub(r"/100x100bb\.", "/600x600bb.", artwork)
        out.append(
            {
                "source": "itunes",
                "title": item.get("trackName", ""),
                "artist": item.get("artistName", ""),
                "album": item.get("collectionName", ""),
                "url": artwork,
            }
        )
    return out


def deezer_candidates(session, title, artist):
    query = quote_plus(f'artist:"{artist}" track:"{title}"')
    url = f"https://api.deezer.com/search?q={query}&limit=8"
    data = request_json(session, url)
    out = []
    for item in data.get("data", []):
        album = item.get("album") or {}
        artwork = album.get("cover_big") or album.get("cover_xl") or album.get("cover_medium")
        if not artwork:
            continue
        out.append(
            {
                "source": "deezer",
                "title": item.get("title", ""),
                "artist": (item.get("artist") or {}).get("name", ""),
                "album": album.get("title", ""),
                "url": artwork,
            }
        )
    return out


def best_candidate(session, title, artist):
    candidates = []
    for getter in (itunes_candidates, deezer_candidates):
        try:
            candidates.extend(getter(session, title, artist))
        except Exception as exc:
            candidates.append({"source": getter.__name__, "error": str(exc), "score": 0})

    best = None
    for cand in candidates:
        if "error" in cand:
            continue
        cand["score"] = round(score_candidate(title, artist, cand["title"], cand["artist"]), 3)
        if best is None or cand["score"] > best["score"]:
            best = cand
    return best, candidates


def has_cover(path):
    try:
        tags = ID3(path)
    except ID3NoHeaderError:
        return False
    return any(key.startswith("APIC") for key in tags.keys())


def extract_cover(path):
    """Extrae la carátula existente de un MP3"""
    try:
        tags = ID3(path)
        for key in tags.keys():
            if key.startswith("APIC"):
                apic = tags[key]
                return apic.data, apic.mime
    except (ID3NoHeaderError, Exception):
        pass
    return None, None


def embed_cover(mp3_path, image_data, mime="image/jpeg"):
    try:
        tags = ID3(mp3_path)
    except ID3NoHeaderError:
        tags = ID3()
    tags.delall("APIC")
    tags.add(
        APIC(
            encoding=3,
            mime=mime,
            type=3,
            desc="Cover",
            data=image_data,
        )
    )
    tags.save(mp3_path, v2_version=3)


# -----------------------------------------------------------------------------
# Thread for cover search
# -----------------------------------------------------------------------------

class CoverSearchThread(QThread):
    progress = pyqtSignal(int, int, str)  # current, total, filename
    cover_found = pyqtSignal(int, dict, bytes)  # row, cover_info, image_data
    finished = pyqtSignal()

    def __init__(self, mp3_files, parent=None):
        super().__init__(parent)
        self.mp3_files = mp3_files
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "cover-manager/1.0 (local personal music library)"})

    def run(self):
        for i, mp3_path in enumerate(self.mp3_files):
            self.progress.emit(i + 1, len(self.mp3_files), mp3_path.name)
            
            try:
                title, artist, album = read_tags(mp3_path)
                best, candidates = best_candidate(self.session, title, artist)
                
                if best and best.get("score", 0) >= 0.5:
                    try:
                        r = self.session.get(best["url"], timeout=30)
                        r.raise_for_status()
                        image_data = r.content
                        self.cover_found.emit(i, best, image_data)
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        
        self.finished.emit()


# -----------------------------------------------------------------------------
# GUI widgets
# -----------------------------------------------------------------------------

class DropZoneWidget(QFrame):
    def __init__(self, on_upload_clicked, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)
        self._build_ui(on_upload_clicked)

    def _build_ui(self, on_upload_clicked):
        self.setObjectName("dropZone")
        self.setStyleSheet("""
            QFrame#dropZone {
                border: 2px dashed #b0b8c1;
                border-radius: 10px;
                background-color: #fafafa;
            }
        """)
        self.setMinimumHeight(130)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        self.lbl_drag = QLabel(tr("Drag and drop MP3 files"))
        self.lbl_drag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_drag.setStyleSheet("font-size: 15px; font-weight: bold; color: #222; border: none;")

        self.lbl_or = QLabel(tr("or"))
        self.lbl_or.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_or.setStyleSheet("font-size: 13px; color: #666; border: none;")

        self.btn_upload = QPushButton(tr("⬆  Add MP3 files"))
        self.btn_upload.setFixedSize(180, 36)
        self.btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_upload.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2bbfa4, stop:1 #1a9e87);
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 16px;
            }
            QPushButton:hover { background: #158a74; }
            QPushButton:pressed { background: #117a63; }
        """)
        self.btn_upload.clicked.connect(on_upload_clicked)

        layout.addWidget(self.lbl_drag)
        layout.addWidget(self.lbl_or)
        layout.addWidget(self.btn_upload, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)


class CoverArtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)

        icon_path = Path(__file__).parent / "cover_finder.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.showMaximized()
        self.setAcceptDrops(True)
        self.files = []
        self.cover_data = {}  # row -> (cover_info, image_data)
        self.search_thread = None
        self.init_ui()

    def center_window(self):
        frame = self.frameGeometry()
        screen = QApplication.primaryScreen()
        center = screen.availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        self.drop_zone = DropZoneWidget(self.open_file_dialog)
        layout.addWidget(self.drop_zone)

        top_row = QHBoxLayout()
        self.count_label = QLabel(tr("Added files: 0"))
        self.count_label.setStyleSheet("font-weight: bold;")
        top_row.addWidget(self.count_label)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Table with columns: Checkbox, File, Artist, Title, Cover Preview
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            tr("Save"), tr("File"), tr("Artist"), tr("Title"), tr("Cover Preview")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(4, 200)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        button_row = QHBoxLayout()
        
        self.btn_search = QPushButton(tr("🔍 Search Covers"))
        self.btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                padding: 9px 18px;
            }
            QPushButton:hover { background-color: #357abd; }
            QPushButton:pressed { background-color: #2a629d; }
        """)
        self.btn_search.clicked.connect(self.search_covers)
        button_row.addWidget(self.btn_search)

        self.btn_select_all = QPushButton(tr("Select all"))
        self.btn_select_all.clicked.connect(self.select_all)
        button_row.addWidget(self.btn_select_all)

        self.btn_unselect_all = QPushButton(tr("Unselect all"))
        self.btn_unselect_all.clicked.connect(self.unselect_all)
        button_row.addWidget(self.btn_unselect_all)

        self.btn_clear = QPushButton(tr("Clear list"))
        self.btn_clear.clicked.connect(self.clear_list)
        button_row.addWidget(self.btn_clear)

        self.btn_about = QPushButton(tr("About..."))
        self.btn_about.clicked.connect(self.show_about)
        button_row.addWidget(self.btn_about)

        button_row.addStretch()

        self.btn_save = QPushButton(tr("💾 Save Selected Covers"))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #1a9e87;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                padding: 9px 18px;
            }
            QPushButton:hover { background-color: #158a74; }
            QPushButton:pressed { background-color: #117a63; }
        """)
        self.btn_save.clicked.connect(self.save_selected_covers)
        button_row.addWidget(self.btn_save)
        layout.addLayout(button_row)

        self.result_label = QLabel(tr("Add MP3 files to search and add cover art."))
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            tr("Select MP3 files"),
            "",
            tr("MP3 files (*.mp3 *.MP3);;All files (*)"),
            options=QFileDialog.Option(0),
        )
        if file_paths:
            self.add_files(file_paths)

    def show_about(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle(tr("About"))
        about_dialog.setMinimumSize(600, 400)
        
        layout = QHBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Left side: Icon
        icon_layout = QVBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_path = Path(__file__).parent / "cover_finder.svg"
        if icon_path.exists():
            if SVG_SUPPORT:
                try:
                    svg_widget = QSvgWidget(str(icon_path))
                    svg_widget.setFixedSize(200, 200)
                    icon_layout.addWidget(svg_widget)
                except Exception:
                    # Fallback if SVG widget fails
                    icon_label = QLabel()
                    icon_label.setText("🎵")
                    icon_label.setStyleSheet("font-size: 100px;")
                    icon_layout.addWidget(icon_label)
            else:
                # Fallback if SVG support is not available
                icon_label = QLabel()
                icon_label.setText("🎵")
                icon_label.setStyleSheet("font-size: 100px;")
                icon_layout.addWidget(icon_label)
        else:
            # Fallback if icon doesn't exist
            icon_label = QLabel()
            icon_label.setText("🎵")
            icon_label.setStyleSheet("font-size: 100px;")
            icon_layout.addWidget(icon_label)
        
        layout.addLayout(icon_layout)
        
        # Right side: Text information
        text_layout = QVBoxLayout()
        text_layout.setSpacing(15)
        
        # Title
        title_label = QLabel(f"<b>{APP_NAME}</b> {APP_VERSION}")
        title_label.setStyleSheet("font-size: 20px;")
        text_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            tr("Una aplicación gráfica para buscar y agregar carátulas (album art) "
               "a archivos MP3. Utiliza las APIs de iTunes y Deezer para encontrar "
               "automáticamente las portadas de tus canciones.")
        )
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        text_layout.addSpacing(20)
        
        # Developer info
        info_text = f"""
        <b>{tr('Correo')}:</b> <a href='mailto:{DEVELOPER_EMAIL}'>{DEVELOPER_EMAIL}</a><br>
        <b>{tr('Copyright')}:</b> {COPYRIGHT}<br>
        <b>{tr('Licencia')}:</b> {LICENSE}
        """
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setOpenExternalLinks(True)
        text_layout.addWidget(info_label)
        
        text_layout.addSpacing(20)
        
        # Technologies
        tech_label = QLabel(f"<b>{tr('Tecnologías usadas')}:</b>")
        text_layout.addWidget(tech_label)
        
        tech_list = QLabel("Python 3, PyQt6, requests, mutagen")
        text_layout.addWidget(tech_list)
        
        text_layout.addStretch()
        
        layout.addLayout(text_layout)
        
        about_dialog.setLayout(layout)
        about_dialog.exec()

    def add_files(self, paths):
        added = 0
        existing = {str(p) for p in self.files}
        for raw in paths:
            path = Path(raw)
            if not path.exists() or not path.is_file():
                continue
            if path.suffix.lower() not in [".mp3"]:
                continue
            if str(path) in existing:
                continue
            self.files.append(path)
            existing.add(str(path))
            added += 1
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Check if file already has cover
            has_existing_cover = has_cover(path)
            
            # Checkbox (checked by default, unchecked if file already has cover)
            checkbox = QCheckBox()
            checkbox.setChecked(not has_existing_cover)
            checkbox.setStyleSheet("margin-left: 14px;")
            self.table.setCellWidget(row, 0, checkbox)

            # File name
            self.table.setItem(row, 1, QTableWidgetItem(path.name))

            # Artist and title from tags or filename
            try:
                title, artist, album = read_tags(path)
                self.table.setItem(row, 2, QTableWidgetItem(artist))
                self.table.setItem(row, 3, QTableWidgetItem(title))
            except:
                f_title, f_artist = split_filename(path)
                self.table.setItem(row, 2, QTableWidgetItem(f_artist))
                self.table.setItem(row, 3, QTableWidgetItem(f_title))

            # Cover preview (show existing cover if available)
            preview_label = QLabel()
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.setScaledContents(False)
            
            if has_existing_cover:
                cover_data, mime = extract_cover(path)
                if cover_data:
                    pixmap = QPixmap()
                    pixmap.loadFromData(cover_data)
                    if not pixmap.isNull():
                        # Scale image to fit within reasonable bounds but keep aspect ratio
                        max_width = 200
                        max_height = 300
                        scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        preview_label.setPixmap(scaled_pixmap)
                        preview_label.setStyleSheet("background-color: #e8f5e9; border: 2px solid #4caf50;")
                    else:
                        preview_label.setText("Error")
                        preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
                else:
                    preview_label.setText("Error")
                    preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
            else:
                preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
                preview_label.setText("No cover")
            
            self.table.setCellWidget(row, 4, preview_label)
            self.table.resizeRowToContents(row)

        self.update_count()
        if added:
            self.result_label.setText(tr("Files added. Click 'Search Covers' to find album art."))
        else:
            self.result_label.setText(tr("No new MP3 files were added."))

    def update_count(self):
        self.count_label.setText(tr("Added files:") + f" {len(self.files)}")

    def select_all(self):
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox):
                widget.setChecked(True)

    def unselect_all(self):
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)

    def clear_list(self):
        self.files.clear()
        self.cover_data.clear()
        self.table.setRowCount(0)
        self.update_count()
        self.result_label.setText(tr("List cleared."))

    def search_covers(self):
        if not self.files:
            QMessageBox.warning(self, tr("No files"), tr("Please add MP3 files first."))
            return

        self.cover_data.clear()
        self.btn_search.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.result_label.setText(tr("Searching for covers..."))

        self.search_thread = CoverSearchThread(self.files)
        self.search_thread.progress.connect(self.on_search_progress)
        self.search_thread.cover_found.connect(self.on_cover_found)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.start()

    def on_search_progress(self, current, total, filename):
        self.progress_bar.setValue(int((current / total) * 100))
        self.result_label.setText(tr("Searching:") + f" {current}/{total} - {filename}")

    def on_cover_found(self, row, cover_info, image_data):
        self.cover_data[row] = (cover_info, image_data)
        
        # Update preview
        preview_label = self.table.cellWidget(row, 4)
        if preview_label:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            if not pixmap.isNull():
                # Scale image to fit within reasonable bounds but keep aspect ratio
                max_width = 200
                max_height = 300
                scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                preview_label.setPixmap(scaled_pixmap)
                preview_label.setText("")
                # Resize row to fit the new image
                self.table.resizeRowToContents(row)
            else:
                preview_label.setText("Error")

    def on_search_finished(self):
        self.btn_search.setEnabled(True)
        self.btn_save.setEnabled(True)
        self.progress_bar.setVisible(False)
        found = len(self.cover_data)
        self.result_label.setText(tr("Search completed. Found covers for") + f" {found}/{len(self.files)} " + tr("files."))

    def save_selected_covers(self):
        if not self.cover_data:
            QMessageBox.warning(self, tr("No covers"), tr("No covers found yet. Please search for covers first."))
            return

        selected = []
        for row, path in enumerate(self.files):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                if row in self.cover_data:
                    selected.append((row, path))

        if not selected:
            QMessageBox.warning(self, tr("No selected files"), tr("Please select at least one file to save the cover."))
            return

        saved = 0
        errors = []
        for row, path in selected:
            try:
                cover_info, image_data = self.cover_data[row]
                embed_cover(path, image_data)
                saved += 1
            except Exception as exc:
                errors.append(f"{path.name}: {exc}")

        if errors:
            QMessageBox.warning(
                self,
                tr("Finished with errors"),
                tr("Some files could not be saved:") + "\n\n" + "\n".join(errors),
            )

        if saved:
            self.result_label.setText(tr("Saved covers to") + f" {saved} " + tr("files."))
            QMessageBox.information(
                self,
                tr("Done"),
                tr("Covers saved successfully to") + f" {saved} " + tr("files."),
            )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.add_files(paths)
            event.acceptProposedAction()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)

    icon_path = Path(__file__).parent / "cover_finder.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Load translation based on system locale
    translator = QTranslator()
    locale = QLocale.system()
    
    # Try to load translation for the current locale
    translation_file = f"cover_art_{locale.name()}.qm"
    translation_path = Path(__file__).parent / "translations" / translation_file
    
    # If the specific locale translation doesn't exist, try the language only
    if not translation_path.exists():
        translation_file = f"cover_art_{locale.language()}.qm"
        translation_path = Path(__file__).parent / "translations" / translation_file
    
    # Load the translation if found
    if translation_path.exists():
        if translator.load(str(translation_path)):
            app.installTranslator(translator)
    
    window = CoverArtApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
