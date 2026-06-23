#!/usr/bin/env python3
"""Telegram Fetcher - local runner"""

import os
import sys
import json
import subprocess
from pathlib import Path

from dotenv import load_dotenv

APPNAME = "TelegramFetcher"
REPO_DIR = Path(__file__).resolve().parent
ENV_PATH = REPO_DIR / ".env"
CONFIG_DIR = REPO_DIR / "fetcher_core" / "config"


def log(message, level="INFO"):
    print(f"{level}:{APPNAME}:{message}")


def load_credentials():
    if not ENV_PATH.exists():
        raise FileNotFoundError(
            f"File .env tidak ditemukan di {ENV_PATH}. "
            "Salin dari .env.example lalu isi credentials-nya."
        )
    load_dotenv(ENV_PATH)

    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN")
    download_path = os.getenv("DOWNLOAD_PATH", str(REPO_DIR / "downloads"))

    missing = [k for k, v in {
        "API_ID": api_id, "API_HASH": api_hash, "BOT_TOKEN": bot_token
    }.items() if not v]
    if missing:
        raise ValueError(f"Variabel .env belum diisi: {', '.join(missing)}")

    try:
        api_id = int(api_id)
    except ValueError:
        raise ValueError("API_ID harus berupa angka integer!")

    return api_id, api_hash, bot_token, download_path


def save_runtime_config(api_id, api_hash, bot_token, download_path):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    Path(download_path).mkdir(parents=True, exist_ok=True)
    credentials = {
        "api_id": api_id,
        "api_hash": api_hash,
        "bot_token": bot_token,
        "download_path": download_path,
    }
    with open(CONFIG_DIR / "credentials.json", "w") as f:
        json.dump(credentials, f, indent=4)
    log("Credentials disimpan ke fetcher_core/config/credentials.json")


def run_bot():
    """Jalankan bot dari package fetcher_core."""
    log("Memulai bot...", level="INFO")
    try:
        subprocess.run(
            [sys.executable, "-m", "fetcher_core"],
            cwd=REPO_DIR,
            check=True,
        )
    except KeyboardInterrupt:
        log("Bot dihentikan oleh user (Ctrl+C).", level="INFO")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Bot crash! Error: {e}")


def main():
    try:
        creds = load_credentials()
        save_runtime_config(*creds)
        run_bot()
    except KeyboardInterrupt:
        log("Dihentikan oleh user.", level="INFO")
        sys.exit(0)
    except Exception as e:
        log(f"ERROR: {e}", level="ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()