from humanize import naturalsize

from fetcher_core.utils.file_utils import smart_truncate_filename, format_duration


def get_start_message() -> str:
    return (
        "👋 <b>Hello!</b> I'm your <b>Telegram Fetcher</b> bot.\n\n"
        "📤 Send me a file or command and I'll handle it.\n"
        "💾 Files will be saved to your configured local download folder.\n\n"
        "ℹ️ Type <b>/help</b> to see all available commands and their descriptions."
    )


def get_help_message() -> str:
    return (
        "🛠️ <b>Telegram Fetcher Bot - Help</b>\n\n"
        "Berikut adalah daftar command yang tersedia:\n\n"
        "• <b>/start</b> - Memulai bot dan menampilkan pesan sambutan.\n"
        "• <b>/tgdownload</b> - Mengaktifkan mode upload, bot akan menunggu file dikirim.\n"
        "• <b>/queue</b> - Menampilkan status antrian download, termasuk file aktif dan daftar file yang menunggu.\n"
        "• <b>/cancelall</b> - Membatalkan semua download aktif dan mengosongkan antrian.\n"
        "• <b>/help</b> - Menampilkan daftar command dan penjelasannya.\n\n"
        "📂 <b>Cara penggunaan:</b>\n"
        "1. Kirim <b>/tgdownload</b> untuk mengaktifkan mode upload.\n"
        "2. Kirim atau forward file (document, video, audio, atau photo) — bisa satu per satu atau banyak sekaligus.\n"
        "3. Gunakan /queue untuk melihat status antrian.\n"
        "4. Gunakan /cancelall untuk membatalkan semua proses.\n\n"
        "⚠️ <b>Penting:</b> Bot hanya memproses file setelah /tgdownload dikirim. Setiap kali ingin upload file baru secara terpisah, kirim /tgdownload lagi terlebih dahulu."
    )


def get_tgdownload_message() -> str:
    return (
        "📥 <b>Telegram File Upload</b>\n\n"
        "Please send the file you want to upload from Telegram.\n"
        "Make sure to send it as a <b>document</b> for best results.\n\n"
        "⏳ Waiting for your file..."
    )


def get_progress_text(filename, current, total, speed, elapsed, eta, output_dir) -> str:
    percent = current / total * 100
    filled = int(10 * percent / 100)
    bar = '▰' * filled + '▱' * (10 - filled)
    short_name = smart_truncate_filename(filename)

    return (
        f"<b>📥 Downloading...</b>\n\n"
        f"<b>» {short_name}</b>\n\n"
        f"╭「 {bar} 」 {percent:.1f}%\n"
        f"├✅ <b>Downloaded:</b> {naturalsize(current)}\n"
        f"├📦 <b>Total Size:</b> {naturalsize(total)}\n"
        f"├⚡ <b>Speed:</b> {naturalsize(speed)}/s\n"
        f"├⏱️ <b>Elapsed:</b> {format_duration(elapsed)}\n"
        f"├⏳ <b>ETA:</b> {format_duration(eta)}\n"
        f"╰💾 <b>Saved To:</b> {output_dir}"
    )


def download_summary_message(items: list, output_dir: str) -> str:
    """items: list of dict {filename, size, elapsed} — dari completed_downloads[user_id]."""
    total_files = len(items)
    total_size = sum(i["size"] for i in items)
    total_time = sum(i["elapsed"] for i in items)

    text = "✅ <b>Download Complete!</b>\n\n"
    text += "📂 <b>List File:</b>\n"
    for i in items:
        short_name = smart_truncate_filename(i["filename"])
        text += f"» {short_name}\n"

    text += (
        f"\n╭📂 <b>Total File »</b> {total_files}\n"
        f"├📁 <b>Total Size »</b> {naturalsize(total_size)}\n"
        f"├⏱️ <b>Saved Time »</b> {format_duration(total_time)}\n"
        f"╰💾 <b>Saved To »</b> {output_dir}"
    )
    return text


ERROR_MESSAGES = {
    "invalid_type": (
        "❌ <b>File type tidak didukung</b>\n"
        "Hanya menerima: Video, Audio, Gambar, PDF, atau Archive."
    ),
    "processing_error": (
        "⚠️ <b>Terjadi error saat memproses file</b>\n"
        "Silakan coba lagi atau kirim file lain."
    ),
    "download_failed": (
        "⏳ <b>Gagal mengunduh file</b>\n"
        "Pastikan koneksi stabil dan coba ulang."
    ),
    "drive_not_mounted": (
        "⚠️ <b>Google Drive belum ter-mount</b>\n"
        "Silakan mount terlebih dahulu sebelum upload."
    ),
    "file_too_large": (
        "❌ <b>File terlalu besar</b>\n"
        "Gunakan file dengan ukuran lebih kecil."
    ),
    "cancelled": "❌ <b>Download dibatalkan oleh user</b>",
    "timeout": "⏳ <b>Download timeout</b>\nCoba ulang dengan koneksi lebih cepat.",
    "permission_denied": "⚠️ <b>Tidak ada izin akses ke folder tujuan</b>",
    "unsupported_format": "❌ <b>Format file tidak didukung</b>",
    "network_error": "⚠️ <b>Koneksi terputus saat download</b>",
}


def get_error_text(error_type: str, detail: str = None) -> str:
    """Format teks error. Tidak mengirim apapun, cuma return string."""
    msg = ERROR_MESSAGES.get(error_type, "Terjadi kesalahan tidak diketahui")
    if detail:
        msg += f"\n\n🔍 <b>Detail:</b> <code>{detail}</code>"
    return msg
