<p align="right">
  <a href="README.ru.md">🇷🇺 Русский</a> | 
  <b>🇬🇧 English</b>
</p>

# TeleDump Viewer

**TeleDump Viewer** is a lightweight desktop viewer for exported Telegram chat history (HTML exports). It recreates the authentic look, feel, and user experience of the official **Telegram Desktop** client, functioning entirely offline.

Default Telegram export HTML files open in browsers as flat, static text pages missing core messenger functionality. **TeleDump Viewer** transforms local export folders into a fully interactive client featuring dark theme styling, embedded media playback, native quotes/replies, and instant message search.

---

## 🚀 Key Features

### 🎨 Authentic Telegram Desktop Interface
* **Native Dark Theme:** Colors, fonts, message bubble border-radii, and shadows are precisely matched to official TDesktop styles.
* **Smart Alignment:** Incoming messages appear on the left, outgoing on the right, complete with double checkmark indicators.
* **Compact Spacing:** Tight gaps between replies and proper avatar alignment next to conversation series.
* **Dynamic Avatars:** Generates initials and official Telegram color gradients for users without profile pictures.

### 🔊 Embedded Media Playback (Audio & Video)
* **Interactive Voice Messages:** Decodes `.ogg` audio files directly within the feed, rendering audio waveforms, playback duration timers, and responsive play/pause buttons.
* **Round Video Messages:** Identifies round video messages and displays authentic circular previews with native click-to-play support.
* **Native Video Player Dialog:** Plays heavy `.mp4`, `.mov`, HEVC, and H.264 video files using the hardware-accelerated Windows Media Foundation / FFmpeg backend:
  * Interactive seekbar / timeline scrubbing
  * Playback position and total duration indicators
  * Dedicated volume slider control

### 💬 Interactive Replies & Quotes
* **Native Reply Bubbles:** Replaces plain *"In reply to this message"* text with an authentic preview card showing author name, vertical accent bar, and quoted content (text or media type).
* **Smooth Jump & Flash Highlight:** Clicking a reply smoothly scrolls directly to the target message, illuminating the entire row with a fading highlight effect.

### 🧭 Navigation & History Management
* **Global Chat Search:** Quickly filters dialogue lists in the left sidebar.
* **In-Chat Keyword Search:** Instant, on-the-fly text searching across loaded conversations without full-page reloads.
* **Date Filter:** Calendar picker to instantly jump to messages from specific dates.
* **Auto-Scroll Position Memory:** Periodically saves reading progress for each chat and automatically restores the scroll position upon return.

---

## 🛠 Tech Stack

* **Language:** Python 3.10+
* **GUI Framework:** PyQt6, PyQt6-WebEngine
* **Media Engine:** PyQt6.QtMultimedia (Hardware-accelerated via FFmpeg / Windows Media Foundation)
* **Parsing:** BeautifulSoup4
* **UI Engine:** HTML5 / CSS3 / JavaScript (Dynamic client-side DOM injection & style overrides)

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AmilicK/Telegram_exported_chathistory_viewer.git](https://github.com/AmilicK/Telegram_exported_chathistory_viewer.git)
   cd TeleDump-Viewer