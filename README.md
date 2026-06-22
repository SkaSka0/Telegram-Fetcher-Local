# Telegram Fetcher

A self-hosted Telegram bot that downloads files sent or forwarded by a user directly to local storage, with queue management, batch handling, real-time progress tracking, and cancellation support.

Originally built and run on Google Colab, this version has been migrated to run natively on a local machine, with no dependency on Colab, Google Drive mounting, or any notebook-specific APIs.

## Features

- **Command-gated uploads** — the bot only processes files after an explicit `/tgupload` command. Files sent without an active upload session are silently ignored.
- **Batch handling** — forward multiple files at once and they are grouped into a single queue batch with one summary message, instead of one notification per file.
- **Live download progress** — progress bar, transfer speed, elapsed time, and ETA updates directly in the chat.
- **Cancellable downloads** — cancel an individual in-progress download via an inline button, or clear the entire queue with `/cancelall`.
- **Persistent download queue** — files are processed sequentially through an `asyncio.Queue`, avoiding concurrent overload on disk and network.
- **Per-user state tracking** — upload sessions are tracked per user and persisted to disk (`user_state.json`), so concurrent users don't interfere with each other.
- **Local-first configuration** — credentials and settings are managed through a `.env` file, no cloud secrets manager required.

## Tech Stack

- [Pyrofork](https://github.com/Mayuri-Chan/pyrofork) — Pyrogram fork, MTProto framework for the Telegram Bot API
- [TgCrypto](https://github.com/pyrogram/tgcrypto) — fast cryptography library for Pyrogram/Pyrofork
- [tqdm](https://github.com/tqdm/tqdm) — progress bar utilities
- [humanize](https://github.com/python-humanize/humanize) — human-readable byte sizes
- [python-dotenv](https://github.com/theskumar/python-dotenv) — `.env` file loading

## Requirements

- Python 3.10+
- A Telegram Bot Token (via [@BotFather](https://t.me/BotFather))
- A Telegram API ID and API Hash (via [my.telegram.org](https://my.telegram.org/apps))
- A C compiler toolchain (required to build TgCrypto), e.g. `base-devel` on Arch Linux, `build-essential` on Debian/Ubuntu

## Project Structure

```
Telegram-Fetcher/
├── colab_fetcher/
│   ├── __init__.py          # Loads credentials from credentials.json
│   ├── __main__.py          # Bot entrypoint, command handlers, download/queue logic
│   ├── config/
│   │   ├── credentials.json # Generated at runtime, not tracked in git
│   │   └── user_state.json  # Per-user upload session state
│   ├── utils/
│   │   ├── client.py        # Pyrogram client initialization
│   │   └── logging.py       # Shared logger configuration
│   └── my_bot.session       # Pyrogram session file, not tracked in git
├── downloads/               # Default download destination
├── .env                     # Local credentials, not tracked in git
├── .env.example             # Template for .env
├── main.py                  # Entry script: loads .env, writes credentials.json, starts the bot
└── requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/Telegram-Fetcher.git
cd Telegram-Fetcher
```

Create a virtual environment and install dependencies.

Using `venv` + `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Using [`uv`](https://github.com/astral-sh/uv):

```bash
uv venv
uv pip install -r requirements.txt
```

## Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
BOT_TOKEN=your_bot_token
DOWNLOAD_PATH=/absolute/path/to/downloads
```

| Variable | Description |
|---|---|
| `API_ID` | Telegram API ID, obtained from [my.telegram.org](https://my.telegram.org/apps) |
| `API_HASH` | Telegram API Hash, obtained from the same page as `API_ID` |
| `BOT_TOKEN` | Bot token issued by [@BotFather](https://t.me/BotFather) |
| `DOWNLOAD_PATH` | Absolute path where downloaded files will be saved |

> **Note:** `DOWNLOAD_PATH` must be an absolute path written literally. Shell expansions such as `~` or `$HOME` are **not** expanded inside `.env` files, since `.env` is parsed by `python-dotenv` rather than the shell.

## Usage

Start the bot:

```bash
source .venv/bin/activate   # if using venv
python3 main.py
```

Or with `uv`:

```bash
uv run main.py
```

On first run, `main.py` will validate the `.env` file, generate `colab_fetcher/config/credentials.json`, and launch the bot process. Press `Ctrl+C` to stop the bot gracefully.

### Bot Commands

| Command | Description |
|---|---|
| `/start` | Displays a welcome message |
| `/tgupload` | Activates upload mode; the bot will accept the next file(s) sent |
| `/queue` | Shows active downloads and pending files in the queue |
| `/cancelall` | Cancels all active downloads and clears the queue |
| `/help` | Lists all available commands |

### Upload Flow

The bot **only processes files immediately after `/tgupload` is sent**. Files sent without an active upload session are ignored without any reply, by design.

1. Send `/tgupload`.
2. Send or forward one or more files (documents, videos, audio, or photos). Files forwarded together within a short window are grouped into a single batch and queued together.
3. The bot replies with a batch confirmation, then processes files sequentially, posting live progress for each one.
4. Once the queue is empty, a summary message is sent with the list of completed downloads, total size, and elapsed time.
5. To upload another file separately afterward, send `/tgupload` again.

## How It Works

- **Queue worker** — a single background `asyncio` task (`queue_worker`) consumes the download queue one item at a time, so downloads do not run concurrently and overwhelm the disk or connection.
- **Batching** — incoming files are buffered per user for a short delay (`BATCH_DELAY`); if more files arrive within that window, they're grouped into one batch notification instead of spamming individual messages.
- **State persistence** — each user's upload session state is stored in `colab_fetcher/config/user_state.json`, so the gating logic survives process restarts mid-session (though active downloads themselves do not resume across restarts).
- **Cancellation** — each active download is tracked in memory with a cancellation flag, checked periodically inside the download's progress callback, and toggled either through the inline cancel button or `/cancelall`.

## Troubleshooting

**`tgcrypto` fails to build during install**
Install a C compiler toolchain first (e.g. `sudo pacman -S base-devel` on Arch Linux, `sudo apt install build-essential` on Debian/Ubuntu), then reinstall dependencies.

**`Missing secret: API_ID` / `Variabel .env belum diisi`**
The `.env` file exists but one or more required variables are empty. Double-check `API_ID`, `API_HASH`, and `BOT_TOKEN` are filled in `.env`.

**Files are not being saved to the expected folder**
Confirm `DOWNLOAD_PATH` in `.env` is an absolute path, written out in full — not `~/...` or `$HOME/...`.

**Bot does not respond to forwarded files**
Make sure `/tgupload` was sent immediately before forwarding. If a file is sent without an active session, the bot intentionally does not reply.

## Security Notes

The following files contain sensitive data and are excluded from version control via `.gitignore`:

- `.env` — Telegram API credentials
- `colab_fetcher/config/credentials.json` — runtime copy of credentials
- `*.session` / `*.session-journal` — active Pyrogram login session
- `colab_fetcher/config/user_state.json` — per-user runtime state

Never commit these files or share them publicly; the session file in particular grants live access to the bot account.

## License

This project is licensed under the **GNU Affero General Public License v3.0**. See [LICENSE](./LICENSE) for the full text.
