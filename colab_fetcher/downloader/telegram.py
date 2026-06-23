import os
import time
import asyncio

from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from colab_fetcher.utils.logging import logger
from colab_fetcher.utils.error_handler import send_error
from colab_fetcher.messages import get_progress_text


async def download_with_progress(
    message: Message,
    file_path: str,
    output_dir: str,
    active_downloads: dict,
):
    start_time = time.time()
    filename = os.path.basename(file_path)
    progress_msg = None
    is_cancelled = False
    last_progress_text = None
    last_update = 0

    # Cancel button
    cancel_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_dl_{message.id}")
    ]])

    active_downloads[message.id] = {
        "cancelled": False,
        "filename": filename,
        "chat_id": message.chat.id
    }

    async def progress(current, total):
        nonlocal progress_msg, is_cancelled, last_progress_text, last_update

        # Check cancel
        if active_downloads.get(message.id, {}).get("cancelled"):
            is_cancelled = True
            raise asyncio.CancelledError()

        elapsed = time.time() - start_time
        speed = current / elapsed if elapsed > 0 else 0
        eta = (total - current) / speed if speed > 0 else 0

        progress_text = get_progress_text(
            filename, current, total, speed, elapsed, eta, output_dir
        )

        # Update setiap 5 detik atau jika isi berubah
        if time.time() - last_update >= 5:
            if progress_text != last_progress_text:
                try:
                    if progress_msg:
                        await progress_msg.edit_text(
                            progress_text,
                            reply_markup=cancel_markup,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        progress_msg = await message.reply_text(
                            progress_text,
                            reply_markup=cancel_markup,
                            parse_mode=ParseMode.HTML
                        )
                    last_progress_text = progress_text
                    last_update = time.time()
                except:
                    pass

    try:
        file_path = await message.download(
            file_name=file_path,
            progress=progress
        )

        if is_cancelled:
            if os.path.exists(file_path):
                os.remove(file_path)
            return None, None

        if progress_msg:
            try:
                await progress_msg.delete()
            except:
                pass

        elapsed = time.time() - start_time
        return file_path, elapsed

    except asyncio.TimeoutError:
        if progress_msg:
            try:
                await progress_msg.edit_text("⏳ Download timeout", reply_markup=None)
            except:
                pass
        await send_error(message, "timeout")
        logger.exception("Download timeout")
        return None, None

    except asyncio.CancelledError:
        if progress_msg:
            try:
                await progress_msg.edit_text("❌ Download cancelled by user", reply_markup=None)
            except:
                pass
        if os.path.exists(file_path):
            os.remove(file_path)
        await send_error(message, "cancelled")
        logger.info("Download cancelled by user")
        return None, None

    except PermissionError as e:
        await send_error(message, "permission_denied", str(e))
        logger.exception("Permission denied")
        return None, None

    except OSError as e:
        if "network" in str(e).lower():
            await send_error(message, "network_error", str(e))
        else:
            await send_error(message, "processing_error", str(e))
        logger.exception("OS error during download")
        return None, None

    except Exception as e:
        if progress_msg:
            try:
                await progress_msg.edit_text(f"⚠️ Download error: {str(e)}", reply_markup=None)
            except:
                pass
        return None, None

    finally:
        active_downloads.pop(message.id, None)