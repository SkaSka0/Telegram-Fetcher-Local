import asyncio

from pyrogram.enums import ParseMode

from fetcher_core.core.state_manager import clear_user_state
from fetcher_core.utils.file_utils import smart_truncate_filename

# ==========================
# 📌 BATCH STATE
# ==========================

batch_buffer = {}
batch_tasks = {}
BATCH_DELAY = 2  # detik


async def send_batch_message(client, chat_id, user_id):
    await asyncio.sleep(BATCH_DELAY)

    items = batch_buffer.get(user_id, [])
    if not items:
        return

    total = len(items)
    filenames = [name for _, name in items]

    # Batasi tampilan max 10 file
    display_list = filenames[:10]
    more = total - len(display_list)

    text = (
        f"📥 <b>Total Files: {total}</b>\n\n"
        "📝 <b>Daftar file:</b>\n"
    )

    for name in display_list:
        short_name = smart_truncate_filename(name)
        text += f"» {short_name}\n"

    if more > 0:
        text += f"\n...dan {more} file lainnya"

    text += "\n✅ Ditambahkan ke antrian download"

    last_message = items[-1][0]

    await client.send_message(
        chat_id=chat_id,
        text=text,
        reply_to_message_id=last_message.id,
        parse_mode=ParseMode.HTML
    )

    batch_buffer.pop(user_id, None)
    batch_tasks.pop(user_id, None)
    await clear_user_state(user_id)
