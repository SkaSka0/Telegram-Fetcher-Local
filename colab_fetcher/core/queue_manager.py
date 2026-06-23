import os
import asyncio

from pyrogram.enums import ParseMode

from colab_fetcher.downloader.telegram import download_with_progress
from colab_fetcher.utils.error_handler import send_error
from colab_fetcher.utils.logging import logger
from colab_fetcher.messages import download_summary_message

# ==========================
# 📌 QUEUE STATE
# ==========================

download_queue = asyncio.Queue()
active_downloads = {}
completed_downloads = {}


# ==========================
# 📌 WORKER & DOWNLOAD LOGIC
# ==========================

async def queue_worker():
    while True:
        client, message, file_path, output_dir = await download_queue.get()
        user_id = message.from_user.id
        logger.info(f"Start processing file {file_path} for user {user_id}")
        try:
            downloaded_path, elapsed_time = await download_with_progress(client, message, file_path, output_dir)
            if downloaded_path:
                if user_id not in completed_downloads:
                    completed_downloads[user_id] = []
                completed_downloads[user_id].append({
                    "filename": os.path.basename(file_path),
                    "size": os.path.getsize(downloaded_path),
                    "elapsed": elapsed_time
                })

                if download_queue.qsize() == 0:
                    summary_text = download_summary_message(completed_downloads.get(user_id, []), output_dir)
                    await client.send_message(
                        chat_id=message.chat.id,
                        text=summary_text,
                        reply_to_message_id=message.id,
                        parse_mode=ParseMode.HTML
                    )
                    completed_downloads.pop(user_id, None)

        except Exception as e:
            await send_error(message, "download_failed", str(e))
            logger.exception("Error in queue worker")
        finally:
            download_queue.task_done()
            logger.info(f"Finished processing file {file_path}")
