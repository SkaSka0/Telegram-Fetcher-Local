import os
import asyncio
from humanize import naturalsize
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from colab_fetcher.utils.client import app
from colab_fetcher.utils.logging import logger

from colab_fetcher.utils.file_utils import (
    smart_truncate_filename,
    get_unique_filename,
    is_allowed_file,
    get_output_directory,
)

from colab_fetcher.messages import (
    get_start_message,
    get_help_message,
    get_tgdownload_message,
)

from colab_fetcher.core.state_manager import (
    set_user_state,
    get_user_state,
)

from colab_fetcher.core.queue_manager import (
    download_queue,
    active_downloads,
    queue_worker,
    send_error,
)

from colab_fetcher.core.batch_manager import (
    batch_buffer,
    batch_tasks,
    send_batch_message,
)

# ==========================
# 📌 HANDLER FUNCTIONS
# ==========================

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    logger.info(f"/start command received from user {user_id}")
    await client.send_message(
        chat_id=message.chat.id,
        text=get_start_message(),
        reply_to_message_id=message.id
    )
    logger.info("Start message sent.")
    
@app.on_message(filters.command("help") & filters.private)
async def help_handler(client, message: Message):
    help_text = get_help_message()

    await client.send_message(
        chat_id=message.chat.id,
        text=help_text,
        reply_to_message_id=message.id,
        parse_mode=ParseMode.HTML
    )

@app.on_message(filters.command("tgdownload"))
async def tgdownload_command(client, message: Message):
    try:
        logger.info(f"Received /tgdownload command from user {message.from_user.id}")

        await client.send_message(
            chat_id=message.chat.id,
            text=get_tgdownload_message(),
            reply_to_message_id=message.id
        )

        await set_user_state(message.from_user.id, "waiting_for_file")
        logger.info(f"Set user {message.from_user.id} state to 'waiting_for_file'")
    except Exception as e:
        logger.exception("Error in /tgdownload handler")
        await send_error(message, "processing_error", str(e))
        
@app.on_message(filters.private & (
    filters.document | filters.video | filters.audio |
    filters.photo | filters.voice | filters.sticker | filters.animation
))
async def handle_file_upload(client, message: Message):
    user_id = message.from_user.id

    # Hanya proses file kalau user sudah mengaktifkan mode upload via /tgdownload
    state = await get_user_state(user_id)
    if state != "waiting_for_file":
        return  # diam total, tidak ada respon apapun

    try:
        # Validasi tipe file
        if not is_allowed_file(message):
            return await send_error(message, "invalid_type")

        output_dir = get_output_directory()
        unique_name = get_unique_filename(output_dir, message)
        file_path = os.path.join(output_dir, unique_name)

        # Masukkan ke antrian download
        await download_queue.put((client, message, file_path, output_dir))

        # ===== BATCHING MESSAGE =====
        filename = os.path.basename(file_path)

        if user_id not in batch_buffer:
            batch_buffer[user_id] = []
        batch_buffer[user_id].append((message, filename))

        if user_id not in batch_tasks:
            batch_tasks[user_id] = asyncio.create_task(
                send_batch_message(client, message.chat.id, user_id)
            )

    except Exception as e:
        await send_error(message, "download_failed", str(e))
        logger.exception("Download error")

@app.on_message(filters.command("queue"))
async def queue_command(client, message: Message):
    queue_text = "📊 <b>Status Antrian</b>\n\n"

    # Active download
    if active_downloads:
        queue_text += "📥 <b>Active Download:</b>\n"
        for msg_id, info in active_downloads.items():
            filename = info.get("filename", f"Pesan ID {msg_id}")
            queue_text += f"<a href='https://t.me/c/{info['chat_id']}/{msg_id}'>{filename}</a>\n"
    else:
        queue_text += "✅ Tidak ada download aktif.\n"

    # Queue size
    size = download_queue.qsize()
    queue_text += f"\n📂 <b>Total file dalam antrian:</b> {size}\n"

    # List file dalam queue
    if size > 0:
        queue_text += "\n📝 <b>Daftar file:</b>\n"
        for idx, item in enumerate(list(download_queue._queue), start=1):
            _, msg, file_path, _ = item
            filename = os.path.basename(file_path)
            short_name = smart_truncate_filename(filename)
            queue_text += f"{idx}. {short_name}\n"

        # Hitung total size
        total_size = 0
        for _, msg, _, _ in list(download_queue._queue):
            if msg.document:
                total_size += msg.document.file_size or 0
            elif msg.video:
                total_size += msg.video.file_size or 0
            elif msg.audio:
                total_size += msg.audio.file_size or 0
        if total_size > 0:
            queue_text += f"\n📦 <b>Total queue size:</b> {naturalsize(total_size)}\n"

    await message.reply_text(queue_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

@app.on_callback_query(filters.regex(r"cancel_dl_(\d+)"))
async def handle_cancel(client, callback_query):
    message_id = int(callback_query.data.split("_")[-1])

    if message_id in active_downloads:
        active_downloads[message_id]["cancelled"] = True
        await callback_query.answer("Cancelling download...")
    else:
        await callback_query.answer("No active download to cancel", show_alert=True)

@app.on_message(filters.command("cancelall"))
async def cancel_all_command(client, message: Message):
    cancelled_count = 0

    # Batalkan semua download aktif
    if active_downloads:
        for msg_id in list(active_downloads.keys()):
            active_downloads[msg_id]["cancelled"] = True
            cancelled_count += 1

    # Kosongkan queue
    queue_size = download_queue.qsize()
    while not download_queue.empty():
        try:
            download_queue.get_nowait()
            download_queue.task_done()
        except asyncio.QueueEmpty:
            break

    # Buat pesan konfirmasi
    if cancelled_count > 0 or queue_size > 0:
        await message.reply_text(
            f"❌ Semua download dibatalkan.\n\n"
            f"📥 Active cancelled: {cancelled_count}\n"
            f"📂 Queue cleared: {queue_size}",
            parse_mode=ParseMode.HTML
        )
        logger.info(f"User {message.from_user.id} cancelled {cancelled_count} active downloads and cleared {queue_size} queued files.")
    else:
        await message.reply_text(
            "✅ Tidak ada download aktif atau file dalam antrian untuk dibatalkan.",
            parse_mode=ParseMode.HTML
        )

# ==========================
# 📌 MAIN ENTRY POINT
# ==========================

if __name__ == "__main__":
    logger.info("Starting the bot...")

    loop = asyncio.get_event_loop()
    worker_task = loop.create_task(queue_worker())

    try:
        app.run()
    finally:
        worker_task.cancel()
        try:
            loop.run_until_complete(worker_task)
        except asyncio.CancelledError:
            logger.info("Worker task cancelled cleanly.")

    logger.info("Bot stopped.")
