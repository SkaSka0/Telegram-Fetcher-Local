from pyrogram.enums import ParseMode
from pyrogram.types import Message

from fetcher_core.messages import get_error_text


async def send_error(message: Message, error_type: str, detail: str = None):
    """Mengirim pesan error yang user-friendly dengan detail tambahan"""
    msg = get_error_text(error_type, detail)
    await message.reply_text(msg, parse_mode=ParseMode.HTML)