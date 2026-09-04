import os
import sys

from pathlib import Path
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl, Qt, QTimer
from gui import MainWindow, SettingsDialog, NativeVideoPlayerDialog
from config import WINDOW_TITLE, WINDOW_SIZE, load_settings, save_settings, get_override_css

class TelegramViewerController:
    def __init__(self, view: MainWindow):
        self.view = view
        self.settings = load_settings()
        self.current_html_path = None
        self.active_player_dialog = None

        self.view.filter_applied.connect(self.on_filter)
        self.view.chat_list.currentRowChanged.connect(self.on_row_changed)
        self.view.chat_list.itemClicked.connect(self.on_item_clicked)
        self.view.web_view.loadFinished.connect(self.on_page_loaded)
        self.view.folder_selected.connect(self.set_export_directory)
        self.view.settings_requested.connect(self.open_settings)
        self.view.global_search.textChanged.connect(self.filter_chat_list)
        self.view.native_video_open.connect(self.open_native_video_player)

        # Автосохранение скролла раз в секунду
        self.scroll_timer = QTimer()
        self.scroll_timer.setInterval(1000)
        self.scroll_timer.timeout.connect(self._sync_scroll_position)
        self.scroll_timer.start()

        saved_dir = self.settings.get("export_folder", "")
        if saved_dir and Path(saved_dir).exists():
            self.scan_export_directory(Path(saved_dir))

    def open_native_video_player(self, file_url_str: str, is_round: bool):
        if self.active_player_dialog:
            self.active_player_dialog.close()
        
        self.active_player_dialog = NativeVideoPlayerDialog(file_url_str, is_round=is_round, parent=self.view)
        self.active_player_dialog.show()

    def _sync_scroll_position(self):
        if not self.current_html_path:
            return
        self.view.web_view.page().runJavaScript("window.scrollY;", self._on_scroll_received)

    def _on_scroll_received(self, scroll_y):
        if scroll_y is not None and self.current_html_path:
            if "chat_positions" not in self.settings:
                self.settings["chat_positions"] = {}
            current_saved = self.settings["chat_positions"].get(self.current_html_path, -1)
            if int(scroll_y) != current_saved:
                self.settings["chat_positions"][self.current_html_path] = int(scroll_y)
                save_settings(self.settings)

    def set_export_directory(self, folder_path: str):
        self.settings["export_folder"] = folder_path
        save_settings(self.settings)
        self.scan_export_directory(Path(folder_path))

    def open_settings(self):
        dlg = SettingsDialog(self.settings, self.view)
        dlg.settings_saved.connect(self.apply_new_settings)
        dlg.exec()

    def apply_new_settings(self, new_settings: dict):
        old_folder = self.settings.get("export_folder")
        self.settings = new_settings
        save_settings(self.settings)

        if new_settings.get("export_folder") != old_folder:
            path = Path(new_settings["export_folder"])
            if path.exists():
                self.scan_export_directory(path)

        self.apply_current_view_state()

    def scan_export_directory(self, target_path: Path):
        html_files = list(target_path.glob("**/messages*.html")) if target_path.is_dir() else [target_path]
        
        self.view.chat_list.blockSignals(True)
        self.view.chat_list.clear()

        for f in html_files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    soup = BeautifulSoup(fp.read(4096), "html.parser")
                    header = soup.find("div", class_="text bold")
                    chat_name = header.text.strip() if header else f.parent.name
            except Exception:
                chat_name = f.parent.name

            self.view.add_chat_item(chat_name, str(f.resolve()))

        self.view.chat_list.blockSignals(False)

        if self.view.chat_list.count() > 0:
            self.view.chat_list.setCurrentRow(0)

    def filter_chat_list(self, query: str):
        q = query.strip().lower()
        for idx in range(self.view.chat_list.count()):
            item = self.view.chat_list.item(idx)
            widget = self.view.chat_list.itemWidget(item)
            if widget:
                matches = q in widget.title.lower() if q else True
                item.setHidden(not matches)

    def on_item_clicked(self, item):
        if not item:
            return
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self._load_chat_file(file_path)

    def on_row_changed(self, row: int):
        if row < 0:
            return
        item = self.view.chat_list.item(row)
        if item:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path:
                self._load_chat_file(file_path)

    def _load_chat_file(self, file_path: str):
        path_obj = Path(file_path).resolve()
        if not path_obj.exists():
            return
        if self.current_html_path == str(path_obj):
            return
        self.current_html_path = str(path_obj)
        self.view.web_view.load(QUrl.fromLocalFile(str(path_obj)))

    def on_page_loaded(self, ok: bool):
        if ok:
            self.view.chat_search.blockSignals(True)
            self.view.chat_search.clear()
            self.view.chat_search.blockSignals(False)
            
            saved_positions = self.settings.get("chat_positions", {})
            target_scroll = saved_positions.get(self.current_html_path, -1)
            self.apply_current_view_state(target_scroll=target_scroll)

    def apply_current_view_state(self, query: str = "", date_filter: str = "", target_scroll: int = -1):
        font_size = self.settings.get("bubble_font_size", 13)
        show_service = self.settings.get("show_service_messages", True)
        css = get_override_css(font_size=font_size)
        self.view.inject_styles_and_filter(css, query, date_filter, show_service, target_scroll=target_scroll)

    def on_filter(self, query: str, date_filter: str):
        self.apply_current_view_state(query, date_filter)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle(WINDOW_TITLE)
    window.resize(*WINDOW_SIZE)

    controller = TelegramViewerController(window)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()