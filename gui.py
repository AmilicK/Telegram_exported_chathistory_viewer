import urllib.parse
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget,
    QDateEdit, QLabel, QSplitter, QListWidgetItem, QPushButton,
    QDialog, QSpinBox, QCheckBox, QFileDialog, QSlider
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QUrl, QSize
from PyQt6.QtGui import QPainter, QColor, QFont
from config import AVATAR_PALETTE

class InterceptWebPage(QWebEnginePage):
    video_clicked = pyqtSignal(str, bool)

    def acceptNavigationRequest(self, url: QUrl, nav_type, is_main_frame):
        url_str = url.toString()
        lower = url_str.lower()

        if lower.split("?")[0].endswith((".mp4", ".mov", ".mkv", ".webm")):
            is_round = "round=1" in lower or "video_message" in lower
            self.video_clicked.emit(url_str, is_round)
            return False

        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class NativeVideoPlayerDialog(QDialog):
    def __init__(self, file_url_str: str, is_round: bool = False, parent=None):
        super().__init__(parent)
        self.is_round = is_round

        raw_url = file_url_str.split("?")[0]
        parsed_url = QUrl(raw_url)
        local_path = parsed_url.toLocalFile()

        if not local_path:
            clean = raw_url.replace("file:///", "").replace("file://", "")
            local_path = urllib.parse.unquote(clean)

        self.media_path = Path(local_path).resolve()

        if self.is_round:
            self.setWindowTitle("Telegram Round Video")
            self.setFixedSize(380, 420)
            self.setStyleSheet("""
                QDialog {
                    background-color: #0E1621;
                    border: 2px solid #2B5278;
                    border-radius: 16px;
                }
                QPushButton {
                    background-color: #2B5278;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #356694; }
            """)
        else:
            self.setWindowTitle("Telegram Media Player")
            self.resize(800, 520)
            self.setStyleSheet("""
                QDialog { background-color: #0E1621; }
                QLabel { color: #8DA4B8; font-size: 12px; }
                QSlider::groove:horizontal {
                    height: 4px;
                    background: #242F3D;
                    border-radius: 2px;
                }
                QSlider::sub-page:horizontal {
                    background: #5288C1;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #FFFFFF;
                    width: 12px;
                    margin-top: -4px;
                    margin-bottom: -4px;
                    border-radius: 6px;
                }
                QPushButton {
                    background: transparent;
                    color: #FFFFFF;
                    border: none;
                    font-size: 15px;
                }
                QPushButton:hover {
                    color: #5288C1;
                }
            """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget, 1)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        controls_bar = QWidget()
        controls_bar.setFixedHeight(46)
        controls_bar.setStyleSheet("background-color: #17212B; padding: 0 10px;")
        c_layout = QHBoxLayout(controls_bar)
        c_layout.setContentsMargins(10, 0, 10, 0)
        c_layout.setSpacing(10)

        self.btn_play = QPushButton("⏸")
        self.btn_play.setFixedWidth(30)
        self.btn_play.clicked.connect(self.toggle_play)
        c_layout.addWidget(self.btn_play)

        self.lbl_time = QLabel("00:00 / 00:00")
        c_layout.addWidget(self.lbl_time)

        self.slider_pos = QSlider(Qt.Orientation.Horizontal)
        self.slider_pos.setRange(0, 0)
        self.slider_pos.sliderMoved.connect(self.set_position)
        c_layout.addWidget(self.slider_pos, 1)

        c_layout.addWidget(QLabel("🔊"))
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setFixedWidth(80)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(100)
        self.slider_vol.valueChanged.connect(self.set_volume)
        c_layout.addWidget(self.slider_vol)

        layout.addWidget(controls_bar)

        self.player.positionChanged.connect(self.on_pos_changed)
        self.player.durationChanged.connect(self.on_dur_changed)

        if self.is_round:
            self.player.setLoops(QMediaPlayer.Loops.Infinite)

        if self.media_path.exists():
            self.player.setSource(QUrl.fromLocalFile(str(self.media_path)))
            self.player.play()

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        else:
            self.player.play()
            self.btn_play.setText("⏸")

    def set_position(self, pos):
        self.player.setPosition(pos)

    def set_volume(self, val):
        self.audio_output.setVolume(val / 100.0)

    def on_pos_changed(self, pos):
        if not self.slider_pos.isSliderDown():
            self.slider_pos.setValue(pos)
        self._update_time_label(pos, self.player.duration())

    def on_dur_changed(self, dur):
        self.slider_pos.setRange(0, dur)
        self._update_time_label(self.player.position(), dur)

    def _update_time_label(self, pos, dur):
        p_sec = pos // 1000
        d_sec = dur // 1000
        self.lbl_time.setText(f"{p_sec//60:02}:{p_sec%60:02} / {d_sec//60:02}:{d_sec%60:02}")

    def closeEvent(self, event):
        self.player.stop()
        super().closeEvent(event)


class SettingsDialog(QDialog):
    settings_saved = pyqtSignal(dict)

    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self.settings = current_settings.copy()
        self.setWindowTitle("Настройки")
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog { background-color: #17212B; color: #FFFFFF; }
            QLabel { color: #FFFFFF; font-size: 13px; }
            QPushButton {
                background-color: #2B5278;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #356694; }
            QSpinBox {
                background-color: #242F3D;
                border: 1px solid #101921;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 4px;
            }
            QCheckBox { color: #FFFFFF; font-size: 13px; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        dir_box = QHBoxLayout()
        self.folder_lbl = QLabel(self.settings.get("export_folder") or "Папка не выбрана")
        self.folder_lbl.setStyleSheet("color: #7F8C99; font-size: 11px;")
        btn_choose = QPushButton("Обзор...")
        btn_choose.clicked.connect(self._choose_folder)
        dir_box.addWidget(self.folder_lbl, 7)
        dir_box.addWidget(btn_choose, 3)
        layout.addLayout(dir_box)

        font_box = QHBoxLayout()
        font_lbl = QLabel("Размер шрифта сообщений:")
        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 26)
        self.font_spin.setValue(self.settings.get("bubble_font_size", 13))
        font_box.addWidget(font_lbl)
        font_box.addWidget(self.font_spin)
        layout.addLayout(font_box)

        self.service_chk = QCheckBox("Показывать даты и сервисные сообщения")
        self.service_chk.setChecked(self.settings.get("show_service_messages", True))
        layout.addWidget(self.service_chk)

        layout.addStretch()

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выбрать директорию с экспортом Telegram")
        if folder:
            self.settings["export_folder"] = folder
            self.folder_lbl.setText(folder)

    def _save(self):
        self.settings["bubble_font_size"] = self.font_spin.value()
        self.settings["show_service_messages"] = self.service_chk.isChecked()
        self.settings_saved.emit(self.settings)
        self.accept()


class ChatTabWidget(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.title = title
        self.initials = title[:2].strip().upper() if title else "?"
        self.color = list(AVATAR_PALETTE.values())[abs(hash(title)) % len(AVATAR_PALETTE)]

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        info_layout = QVBoxLayout()
        self.title_lbl = QLabel(self.title)
        self.title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #FFFFFF;")
        self.title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.sub_lbl = QLabel("Экспортированная переписка")
        self.sub_lbl.setStyleSheet("font-size: 12px; color: #7F8C99;")
        self.sub_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        info_layout.addWidget(self.title_lbl)
        info_layout.addWidget(self.sub_lbl)

        layout.addSpacing(42)
        layout.addLayout(info_layout)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(10, (self.height() - 42) // 2, 42, 42)

        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.drawText(10, (self.height() - 42) // 2, 42, 42, Qt.AlignmentFlag.AlignCenter, self.initials)


class MainWindow(QWidget):
    filter_applied = pyqtSignal(str, str)
    folder_selected = pyqtSignal(str)
    settings_requested = pyqtSignal()
    native_video_open = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #17212B;
                color: #F5F5F5;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }
            QLineEdit {
                background-color: #242F3D;
                border: 1px solid #17212B;
                border-radius: 16px;
                padding: 6px 14px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #5288C1;
            }
            QDateEdit {
                background-color: #242F3D;
                border-radius: 14px;
                border: none;
                padding: 4px 10px;
                color: #FFFFFF;
            }
            QPushButton#toolBtn {
                background-color: #242F3D;
                border: 1px solid #101921;
                border-radius: 16px;
                color: #FFFFFF;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton#toolBtn:hover {
                background-color: #2B5278;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #0E1621; width: 1px; }")

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        top_ctrl = QHBoxLayout()
        self.btn_open_folder = QPushButton("📁 Папка")
        self.btn_open_folder.setObjectName("toolBtn")
        self.btn_open_folder.clicked.connect(self._select_folder)

        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setObjectName("toolBtn")
        self.btn_settings.setFixedWidth(38)
        self.btn_settings.clicked.connect(self.settings_requested.emit)

        top_ctrl.addWidget(self.btn_open_folder)
        top_ctrl.addWidget(self.btn_settings)
        left_layout.addLayout(top_ctrl)

        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText("🔍 Поиск по чатам...")
        left_layout.addWidget(self.global_search)

        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet("""
            QListWidget { background-color: #17212B; border: none; }
            QListWidget::item { border-bottom: 1px solid #101921; }
            QListWidget::item:hover { background-color: #202B36; }
            QListWidget::item:selected { background-color: #2B5278; }
        """)
        left_layout.addWidget(self.chat_list)
        splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        top_bar = QWidget()
        top_bar.setFixedHeight(54)
        top_bar.setStyleSheet("background-color: #17212B; border-bottom: 1px solid #0E1621;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 0, 16, 0)

        self.chat_search = QLineEdit()
        self.chat_search.setPlaceholderText("🔍 Поиск в переписке...")
        self.chat_search.textChanged.connect(self._emit_filter)

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setSpecialValueText("Все даты")
        self.date_picker.setDate(QDate(1970, 1, 1))
        self.date_picker.dateChanged.connect(self._emit_filter)

        self.btn_reset_date = QPushButton("✖")
        self.btn_reset_date.setObjectName("toolBtn")
        self.btn_reset_date.setToolTip("Сбросить дату")
        self.btn_reset_date.clicked.connect(lambda: self.date_picker.setDate(QDate(1970, 1, 1)))

        top_layout.addWidget(self.chat_search, 7)
        top_layout.addWidget(self.date_picker, 3)
        top_layout.addWidget(self.btn_reset_date)
        right_layout.addWidget(top_bar)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background-color: #0E1621;")

        self.custom_page = InterceptWebPage(self.web_view)
        self.custom_page.video_clicked.connect(self.native_video_open.emit)
        self.web_view.setPage(self.custom_page)

        right_layout.addWidget(self.web_view)

        splitter.addWidget(right_panel)
        splitter.setSizes([340, 940])
        layout.addWidget(splitter)

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выбрать директорию экспорта Telegram")
        if folder:
            self.folder_selected.emit(folder)

    def _emit_filter(self):
        text = self.chat_search.text().strip()
        date_str = ""
        if self.date_picker.date() > QDate(1970, 1, 1):
            date_str = self.date_picker.date().toString("dd.MM.yyyy")
        self.filter_applied.emit(text, date_str)

    def add_chat_item(self, chat_name: str, file_path: str):
        item = QListWidgetItem()
        item.setSizeHint(QSize(280, 64))
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, ChatTabWidget(chat_name))

    def inject_styles_and_filter(self, override_css: str, query: str = "", date_filter: str = "", show_service: bool = True, target_scroll: int = -1):
        show_serv_js = "true" if show_service else "false"
        clean_css = override_css.replace("\n", " ").replace('"', '\\"')
        clean_query = query.lower().replace('"', '\\"')

        js_code = f"""
        (function() {{
            window.CheckLocation = function() {{}};

            let style = document.getElementById('custom-tdesktop-style');
            if (!style) {{
                style = document.createElement('style');
                style.id = 'custom-tdesktop-style';
                document.head.appendChild(style);
            }}
            style.innerHTML = "{clean_css}";

            // 1. Определение входящих/исходящих
            let chatHeader = document.querySelector('.page_header .text');
            let interlocutorName = chatHeader ? chatHeader.innerText.trim() : "";
            let msgs = document.querySelectorAll('.history > .message');
            let lastSender = "";

            msgs.forEach(m => {{
                if (m.classList.contains('service')) return;

                let fromElem = m.querySelector('.from_name');
                if (fromElem) {{
                    lastSender = fromElem.innerText.trim();
                }}

                if (lastSender && interlocutorName && !lastSender.includes(interlocutorName)) {{
                    m.classList.add('is-out');
                }} else {{
                    m.classList.remove('is-out');
                }}
            }});

            // 2. Цитаты: переход и надежная плавная подсветка фона всей строки
            document.querySelectorAll('.reply_to:not(.customized)').forEach(replyDiv => {{
                replyDiv.classList.add('customized');
                let link = replyDiv.querySelector('a');
                let href = link ? (link.getAttribute('href') || '') : '';
                let onclick = link ? (link.getAttribute('onclick') || '') : '';

                let match = href.match(/message\\d+/) || onclick.match(/message\\d+/);
                let targetId = match ? match[0] : "";
                let targetMsg = targetId ? document.getElementById(targetId) : null;

                let authorText = "Сообщение";
                let previewText = "Вложение";

                if (targetMsg) {{
                    let authorElem = targetMsg.querySelector('.from_name');
                    if (authorElem) {{
                        authorText = authorElem.innerText.trim();
                    }}

                    let textElem = targetMsg.querySelector('.text');
                    if (textElem) {{
                        previewText = textElem.innerText.trim().replace(/\\s+/g, ' ');
                    }} else if (targetMsg.querySelector('.media_voice_message')) {{
                        previewText = "🎤 Голосовое сообщение";
                    }} else if (targetMsg.querySelector('.media_video_message')) {{
                        previewText = "📹 Видеосообщение";
                    }} else if (targetMsg.querySelector('.photo_wrap, .media_photo')) {{
                        previewText = "🖼 Фотография";
                    }} else if (targetMsg.querySelector('.video_file_wrap')) {{
                        previewText = "🎬 Видео";
                    }}
                }} else if (targetId) {{
                    authorText = "В ответ на";
                    previewText = "#" + targetId.replace('message', '');
                }}

                let replyBox = document.createElement('div');
                replyBox.className = 'custom-reply-box';
                replyBox.innerHTML = `
                    <div class="custom-reply-author">${{authorText}}</div>
                    <div class="custom-reply-text">${{previewText}}</div>
                `;

                replyBox.onclick = (e) => {{
                    e.preventDefault();
                    e.stopPropagation();

                    if (!targetMsg && targetId) {{
                        targetMsg = document.getElementById(targetId);
                    }}

                    if (targetMsg) {{
                        targetMsg.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

                        // Мгновенная заливка фона строки с последующим плавным угасанием
                        targetMsg.style.transition = 'none';
                        targetMsg.style.backgroundColor = 'rgba(82, 136, 193, 0.45)';
                        targetMsg.style.borderRadius = '8px';

                        setTimeout(() => {{
                            targetMsg.style.transition = 'background-color 2.0s cubic-bezier(0.25, 1, 0.5, 1)';
                            targetMsg.style.backgroundColor = 'transparent';
                        }}, 150);
                    }}
                }};

                replyDiv.parentNode.insertBefore(replyBox, replyDiv);
                replyDiv.style.display = 'none';
            }});

            // 3. Голосовые сообщения (.ogg)
            document.querySelectorAll('a.media_voice_message:not(.customized)').forEach(a => {{
                a.classList.add('customized');
                let audioSrc = a.href || a.getAttribute('href');
                let statusDiv = a.querySelector('.status.details');
                let durText = statusDiv ? statusDiv.innerText : "00:00";

                let barsHtml = "";
                for(let i = 0; i < 32; i++) {{
                    let h = Math.floor(Math.sin(i * 0.4) * 6 + Math.cos(i * 0.8) * 4 + 10);
                    barsHtml += `<div class="wave-bar" style="height: ${{h}}px;" data-idx="${{i}}"></div>`;
                }}

                let playerWrapper = document.createElement('div');
                playerWrapper.className = 'custom-voice-player';
                playerWrapper.innerHTML = `
                    <audio src="${{audioSrc}}" preload="none"></audio>
                    <button class="voice-play-btn">
                        <svg class="play-icon" viewBox="0 0 24 24"><polygon points="6,4 20,12 6,20"/></svg>
                    </button>
                    <div class="voice-content">
                        <div class="voice-waveform">${{barsHtml}}</div>
                        <div class="voice-meta"><span class="cur-time">${{durText}}</span></div>
                    </div>
                `;

                let audio = playerWrapper.querySelector('audio');
                let btn = playerWrapper.querySelector('.voice-play-btn');
                let curTimeSpan = playerWrapper.querySelector('.cur-time');
                let bars = playerWrapper.querySelectorAll('.wave-bar');

                btn.onclick = async (e) => {{
                    e.preventDefault();
                    e.stopPropagation();
                    if (audio.paused) {{
                        document.querySelectorAll('audio').forEach(other => {{ 
                            if (other !== audio && !other.paused) other.pause(); 
                        }});
                        try {{
                            await audio.play();
                        }} catch (err) {{
                            console.warn("Audio error:", err);
                        }}
                    }} else {{
                        audio.pause();
                    }}
                }};

                audio.onplay = () => {{
                    btn.innerHTML = `<svg viewBox="0 0 24 24"><rect x="5" y="4" width="4" height="16"/><rect x="15" y="4" width="4" height="16"/></svg>`;
                }};

                audio.onpause = () => {{
                    btn.innerHTML = `<svg viewBox="0 0 24 24"><polygon points="6,4 20,12 6,20"/></svg>`;
                }};

                audio.ontimeupdate = () => {{
                    if (!audio.duration) return;
                    let progress = audio.currentTime / audio.duration;
                    let playedBars = Math.floor(progress * bars.length);
                    bars.forEach((b, idx) => {{
                        if (idx <= playedBars) b.classList.add('played');
                        else b.classList.remove('played');
                    }});

                    let mins = Math.floor(audio.currentTime / 60);
                    let secs = Math.floor(audio.currentTime % 60);
                    curTimeSpan.innerText = `${{mins < 10 ? '0' : ''}}${{mins}}:${{secs < 10 ? '0' : ''}}${{secs}}`;
                }};

                audio.onended = () => {{
                    btn.innerHTML = `<svg viewBox="0 0 24 24"><polygon points="6,4 20,12 6,20"/></svg>`;
                    curTimeSpan.innerText = durText;
                    bars.forEach(b => b.classList.remove('played'));
                }};

                a.replaceWith(playerWrapper);
            }});

            // 4. Круглые видеосообщения
            document.querySelectorAll('a.media_video_message:not(.customized), a.media_video:not(.customized), a.media:not(.customized)').forEach(a => {{
                let titleElem = a.querySelector('.title.bold');
                let isVideoMsg = titleElem && titleElem.innerText.includes('Video message');
                
                if (isVideoMsg) {{
                    a.classList.add('customized');
                    let parentMsg = a.closest('.message');
                    if (parentMsg) {{
                        parentMsg.classList.add('has-round-video');
                    }}

                    let videoSrc = a.href || a.getAttribute('href');
                    let thumbImg = a.querySelector('img');
                    let thumbSrc = thumbImg ? (thumbImg.src || thumbImg.getAttribute('src')) : '';

                    a.className = 'round-thumb-container';
                    a.href = videoSrc + (videoSrc.includes('?') ? '&round=1' : '?round=1');
                    a.innerHTML = `
                        <img src="${{thumbSrc}}">
                        <div class="round-play-overlay">
                            <svg viewBox="0 0 24 24"><polygon points="6,4 20,12 6,20"/></svg>
                        </div>
                    `;
                }}
            }});

            // 5. Обычные видео
            document.querySelectorAll('a.video_file_wrap:not(.customized)').forEach(a => {{
                a.classList.add('customized');
                let thumbImg = a.querySelector('img.video_file');
                let thumbSrc = thumbImg ? (thumbImg.src || thumbImg.getAttribute('src')) : '';

                a.className = 'native-video-card';
                a.innerHTML = `
                    <img src="${{thumbSrc}}">
                    <div class="video-play-btn-badge">
                        <svg viewBox="0 0 24 24"><polygon points="6,4 20,12 6,20"/></svg>
                    </div>
                `;
            }});

            // 6. Фильтрация
            let q = "{clean_query}";
            let d = "{date_filter}";
            let showService = {show_serv_js};
            
            msgs.forEach(m => {{
                if (m.classList.contains('service')) {{
                    m.style.display = (showService && !q && !d) ? '' : (q || d ? 'none' : '');
                    return;
                }}
                
                if (!q && !d) {{
                    m.style.display = '';
                    return;
                }}

                let textElem = m.querySelector('.text');
                let text = textElem ? textElem.innerText.toLowerCase() : "";
                let dateElem = m.querySelector('.date.details');
                let dateTitle = dateElem ? (dateElem.getAttribute('title') || dateElem.innerText) : "";

                let matchQuery = !q || text.includes(q);
                let matchDate = !d || dateTitle.includes(d);

                m.style.display = (matchQuery && matchDate) ? '' : 'none';
            }});

            // 7. Скролл
            let scrollTarget = {target_scroll};
            if (scrollTarget >= 0) {{
                setTimeout(() => {{
                    window.scrollTo(0, scrollTarget);
                }}, 60);
            }}
        }})();
        """
        self.web_view.page().runJavaScript(js_code)