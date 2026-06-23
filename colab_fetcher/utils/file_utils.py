import os
import json
import mimetypes
from datetime import datetime
from pathlib import Path

from pyrogram.types import Message

from colab_fetcher.services.config_manager import CONFIG_PATH

# colab_fetcher/utils/file_utils.py -> root repo
REPO_DIR = Path(__file__).resolve().parent.parent.parent

# Dictionary ekstensi file
EXTENSIONS = {
    # Video
    ".mp4": "video", ".avi": "video", ".mkv": "video", ".m2ts": "video",
    ".mov": "video", ".ts": "video", ".webm": "video", ".mpg": "video",
    # Audio
    ".mp3": "audio", ".wav": "audio", ".flac": "audio", ".aac": "audio",
    # Gambar
    ".jpg": "photo", ".jpeg": "photo", ".png": "photo", ".bmp": "photo",
    # Dokumen
    ".pdf": "pdf", ".doc": "document", ".docx": "document",
    # Archive
    ".zip": "archive", ".rar": "archive", ".7z": "archive",
    # Subtitle
    ".srt": "subtitle", ".ass": "subtitle"
}


def format_duration(seconds: float) -> str:
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    parts = []
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def smart_truncate_filename(filename: str, max_length: int = 20) -> str:
    """Jika nama file terlalu panjang, langsung potong stringnya saja tanpa peduli ekstensi,

    aman dari segala jenis crash akibat format nama file.
    """
    if len(filename) > max_length:
        return f"{filename[:max_length]}..."
    return filename


def sanitize_filename(name: str) -> str:
    """Sanitize filename to remove unsupported characters."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '.', '_')).rstrip()


def ext_from_mime(mime_type: str, default: str = ".bin") -> str:
    """Ambil ekstensi dari MIME type Telegram."""
    if not mime_type:
        return default

    ext = mimetypes.guess_extension(mime_type.lower())
    if ext == ".jpe":
        return ".jpg"
    return ext or default


def get_file_extension(message: Message) -> str:
    """Mendapatkan ekstensi file dari nama file atau MIME metadata Telegram."""
    # Document
    if message.document:
        if message.document.file_name:
            ext = os.path.splitext(message.document.file_name)[1]
        else:
            ext = ext_from_mime(message.document.mime_type, ".bin")
        return ext.lower()

    # Video
    if message.video:
        if message.video.file_name:
            ext = os.path.splitext(message.video.file_name)[1]
        else:
            ext = ext_from_mime(message.video.mime_type, ".mp4")
        return ext.lower()

    # Audio
    if message.audio:
        if message.audio.file_name:
            ext = os.path.splitext(message.audio.file_name)[1]
        else:
            ext = ext_from_mime(message.audio.mime_type, ".mp3")
        return ext.lower()

    # Photo / voice / sticker / fallback
    if message.photo:
        return ".jpg"
    if message.voice:
        return ".ogg"
    if message.sticker:
        return ".webp"

    return ".bin"


def get_unique_filename(directory: str, message: Message) -> str:
    """
    Generate unique filename dari:
    1. Nama file asli Telegram jika ada
    2. Caption jika file_name tidak ada
    3. Timestamp sebagai fallback
    Ekstensi diambil dari file_name atau MIME metadata Telegram.
    """
    os.makedirs(directory, exist_ok=True)
    ext = get_file_extension(message)

    # Ambil filename asli kalau ada
    original_filename = None
    if message.document and message.document.file_name:
        original_filename = message.document.file_name
    elif message.video and message.video.file_name:
        original_filename = message.video.file_name
    elif message.audio and message.audio.file_name:
        original_filename = message.audio.file_name

    if original_filename:
        base = sanitize_filename(os.path.splitext(original_filename)[0])
        final_name = f"{base}{ext}"
    elif message.caption:
        base = sanitize_filename(message.caption)[:50]
        final_name = f"{base}{ext}"
    else:
        final_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"

    # Handle duplikat nama
    counter = 1
    original_name = final_name
    while os.path.exists(os.path.join(directory, final_name)):
        name_part, ext_part = os.path.splitext(original_name)
        final_name = f"{name_part}_{counter}{ext_part}"
        counter += 1

    return final_name


def get_file_type(file_path: str) -> str:
    """Mendapatkan tipe file berdasarkan ekstensi"""
    _, ext = os.path.splitext(file_path)
    return EXTENSIONS.get(ext.lower(), "other")


def is_allowed_file(message: Message) -> bool:
    return True


def get_output_directory() -> str:
    # Baca konfigurasi dari credentials.json
    with open(CONFIG_PATH) as f:
        creds = json.load(f)

    download_path = creds.get("download_path") or str(REPO_DIR / "downloads")
    os.makedirs(download_path, exist_ok=True)

    return download_path
