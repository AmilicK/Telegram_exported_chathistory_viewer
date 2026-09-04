import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"

AVATAR_PALETTE = {
    "userpic1": "#E17076",
    "userpic2": "#FAA774",
    "userpic3": "#A695E7",
    "userpic4": "#7BC862",
    "userpic5": "#6EC9CB",
    "userpic6": "#65AADD",
    "userpic7": "#EE7AAE",
    "userpic8": "#E5A059",
}

WINDOW_TITLE = "Telegram Desktop Export Viewer"
WINDOW_SIZE = (1280, 820)

DEFAULT_SETTINGS = {
    "export_folder": "",
    "bubble_font_size": 13,
    "show_service_messages": True,
    "chat_positions": {}
}

def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {**DEFAULT_SETTINGS, **data}
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def get_override_css(font_size: int = 13) -> str:
    return f"""
    html, body {{
        background: #0f1621 !important;
        color: #f5f5f5 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
        width: 100% !important;
    }}
    .page_wrap, .page_body, .chat_page {{
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }}
    .page_header {{
        display: none !important;
    }}
    
    .history {{
        box-sizing: border-box !important;
        width: 100% !important;
        max-width: 100% !important;
        padding: 8px 16px 60px 12px !important;
        margin: 0 !important;
        display: flex !important;
        flex-direction: column !important;
    }}

    .pull_left, .pull_right {{
        float: none !important;
        margin: 0 !important;
    }}

    .message.service {{
        display: flex !important;
        justify-content: center !important;
        margin: 8px 0 4px 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }}
    .message.service .body {{
        background: rgba(16, 22, 31, 0.75) !important;
        color: #ffffff !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        border-radius: 14px !important;
        padding: 3px 12px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
    }}

    .message.default {{
        display: flex !important;
        align-items: flex-end !important;
        position: relative !important;
        margin-bottom: 2px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        border-radius: 8px !important;
    }}
    
    .message.default.joined {{
        margin-top: -1px !important;
        margin-bottom: 1px !important;
    }}

    /* ------------------------------------------------------------- */
    /* ПОДСВЕТКА ВСЕЙ СТРОКИ СООБЩЕНИЯ (ФОН TDESKTOP)               */
    /* ------------------------------------------------------------- */
    .message.highlighted {{
        animation: rowFlash 2.5s cubic-bezier(0.2, 0.8, 0.25, 1) forwards !important;
    }}

    @keyframes rowFlash {{
        0% {{
            background-color: rgba(82, 136, 193, 0.35) !important;
        }}
        40% {{
            background-color: rgba(82, 136, 193, 0.25) !important;
        }}
        100% {{
            background-color: transparent !important;
        }}
    }}

    /* Входящие сообщения */
    .message.default:not(.is-out) {{
        justify-content: flex-start !important;
        padding-left: 0 !important;
    }}

    .message.default:not(.is-out) .userpic_wrap {{
        display: inline-flex !important;
        width: 34px !important;
        min-width: 34px !important;
        height: 34px !important;
        margin: 0 4px 0 0 !important;
        padding: 0 !important;
        align-self: flex-end !important;
        flex-shrink: 0 !important;
    }}

    .userpic {{
        width: 34px !important;
        height: 34px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .userpic .initials {{
        line-height: 34px !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    .message.default.joined:not(.is-out) {{
        padding-left: 38px !important;
    }}
    .message.default.joined:not(.is-out) .userpic_wrap {{
        display: none !important;
    }}

    .message.default:not(.is-out) .body {{
        background: #212d3b !important;
        color: #f5f5f5 !important;
        border-radius: 12px 12px 12px 4px !important;
        padding: 5px 10px 5px 12px !important;
        max-width: 520px !important;
        min-width: 70px !important;
        width: fit-content !important;
        position: relative !important;
        margin: 0 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
        font-size: {font_size}px !important;
    }}
    .message.default.joined:not(.is-out) .body {{
        border-bottom-left-radius: 12px !important;
    }}
    .message.default:not(.is-out) .from_name {{
        color: #5bb3f0 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        margin-bottom: 2px !important;
    }}
    .message.default.joined:not(.is-out) .from_name {{
        display: none !important;
    }}

    /* Исходящие сообщения */
    .message.is-out {{
        justify-content: flex-end !important;
        padding-left: 0 !important;
    }}
    .message.is-out .userpic_wrap {{
        display: none !important;
    }}
    .message.is-out .body {{
        background: #5b5478 !important;
        border-radius: 12px 12px 4px 12px !important;
        color: #ffffff !important;
        padding: 5px 10px 5px 12px !important;
        max-width: 520px !important;
        min-width: 70px !important;
        width: fit-content !important;
        margin: 0 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
        font-size: {font_size}px !important;
    }}
    .message.is-out.joined .body {{
        border-bottom-right-radius: 12px !important;
    }}
    .message.is-out .from_name {{
        display: none !important;
    }}

    /* Плашка ответа/цитаты */
    .custom-reply-box {{
        display: flex !important;
        flex-direction: column !important;
        border-left: 2px solid #5bb3f0 !important;
        padding-left: 7px !important;
        margin: 2px 0 4px 0 !important;
        cursor: pointer !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 0 4px 4px 0 !important;
        max-width: 100% !important;
        overflow: hidden !important;
        transition: background 0.15s ease;
    }}
    .custom-reply-box:hover {{
        background: rgba(255, 255, 255, 0.09) !important;
    }}
    .message.is-out .custom-reply-box {{
        border-left-color: #bfaef5 !important;
        background: rgba(255, 255, 255, 0.06) !important;
    }}
    .message.is-out .custom-reply-box:hover {{
        background: rgba(255, 255, 255, 0.12) !important;
    }}
    .custom-reply-author {{
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #5bb3f0 !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    .message.is-out .custom-reply-author {{
        color: #d8cdfa !important;
    }}
    .custom-reply-text {{
        font-size: 12px !important;
        color: #9eb2c5 !important;
        line-height: 1.25 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        margin-top: 1px !important;
    }}
    .message.is-out .custom-reply-text {{
        color: #d1c8fc !important;
    }}

    .message .text {{
        display: inline !important;
        word-break: break-word !important;
        line-height: 1.35 !important;
    }}
    .date.details {{
        display: inline-block !important;
        float: right !important;
        font-size: 11px !important;
        color: #8da4b8 !important;
        margin-left: 8px !important;
        margin-top: 4px !important;
        user-select: none !important;
    }}
    .message.is-out .date.details {{
        color: #b7b0db !important;
    }}
    .message.is-out .date.details::after {{
        content: " ✓✓" !important;
        font-size: 10px !important;
        letter-spacing: -2px !important;
        margin-left: 2px !important;
    }}

    /* Голосовые сообщения */
    .custom-voice-player {{
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 230px;
        padding: 3px 1px;
        user-select: none;
    }}
    .voice-play-btn {{
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: #5288c1;
        border: none;
        outline: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        transition: transform 0.1s ease;
    }}
    .message.is-out .voice-play-btn {{
        background-color: #9d8df1;
    }}
    .voice-play-btn:active {{
        transform: scale(0.94);
    }}
    .voice-play-btn svg {{
        width: 15px;
        height: 15px;
        fill: #ffffff;
    }}
    .voice-content {{
        display: flex;
        flex-direction: column;
        gap: 3px;
        flex-grow: 1;
    }}
    .voice-waveform {{
        display: flex;
        align-items: center;
        gap: 2px;
        height: 18px;
        cursor: pointer;
    }}
    .wave-bar {{
        width: 2px;
        border-radius: 1px;
        background-color: #7f8c99;
        transition: background-color 0.1s ease;
    }}
    .wave-bar.played {{
        background-color: #5288c1;
    }}
    .message.is-out .wave-bar.played {{
        background-color: #d1c8fc;
    }}
    .voice-meta {{
        font-size: 11px;
        color: #8da4b8;
    }}
    .message.is-out .voice-meta {{
        color: #b7b0db;
    }}

    /* Кружки */
    .message.has-round-video .body {{
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        border-radius: 50% !important;
    }}
    .message.has-round-video .from_name {{
        display: none !important;
    }}
    .round-thumb-container {{
        position: relative;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        overflow: hidden;
        cursor: pointer;
        background: #000000;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        display: block;
    }}
    .round-thumb-container img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
        display: block;
    }}
    .round-play-overlay {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.55);
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
    }}
    .round-play-overlay svg {{
        width: 24px;
        height: 24px;
        fill: #ffffff;
        margin-left: 3px;
    }}
    .message.has-round-video .date.details {{
        position: absolute;
        bottom: 8px;
        right: 14px;
        background: rgba(0, 0, 0, 0.6);
        padding: 2px 8px;
        border-radius: 10px;
        color: #ffffff !important;
        z-index: 10;
        font-size: 11px !important;
        float: none !important;
    }}

    /* Обычные видео */
    .native-video-card {{
        position: relative;
        cursor: pointer;
        display: inline-block;
        border-radius: 8px;
        overflow: hidden;
    }}
    .native-video-card img {{
        max-width: 100%;
        max-height: 360px;
        display: block;
        border-radius: 8px;
    }}
    .video-play-btn-badge {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.65);
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
    }}
    .video-play-btn-badge svg {{
        width: 26px;
        height: 26px;
        fill: #ffffff;
        margin-left: 3px;
    }}

    /* Палитра аватарок */
    .userpic1 {{ background: linear-gradient(135deg, #e17076, #ff8e8c) !important; }}
    .userpic2 {{ background: linear-gradient(135deg, #faa774, #fec87c) !important; }}
    .userpic3 {{ background: linear-gradient(135deg, #a695e7, #bbaafc) !important; }}
    .userpic4 {{ background: linear-gradient(135deg, #7bc862, #99e07e) !important; }}
    .userpic5 {{ background: linear-gradient(135deg, #6ec9cb, #8be2e4) !important; }}
    .userpic6 {{ background: linear-gradient(135deg, #65aadd, #7ec0f3) !important; }}
    .userpic7 {{ background: linear-gradient(135deg, #ee7aae, #fca3cf) !important; }}
    .userpic8 {{ background: linear-gradient(135deg, #e5a059, #f7b977) !important; }}

    .media_wrap {{
        margin-top: 3px !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}
    img.photo {{
        max-width: 100% !important;
        height: auto !important;
        border-radius: 6px !important;
        display: block !important;
    }}
    .video_duration {{
        position: absolute !important;
        top: 6px !important;
        right: 6px !important;
        background: rgba(0, 0, 0, 0.6) !important;
        padding: 2px 6px !important;
        border-radius: 10px !important;
        font-size: 11px !important;
        color: #ffffff !important;
    }}
    """