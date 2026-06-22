# 🚀 Refactor Progress Tracker

## Current Status

* [ ] Tahap 1 — UserStateManager
* [ ] Tahap 2 — File Utilities
* [ ] Tahap 3 — Messages Module
* [ ] Tahap 4 — BatchManager
* [ ] Tahap 5 — DownloadQueueManager
* [ ] Tahap 6 — Downloader Service
* [ ] Tahap 7 — ConfigManager
* [ ] Tahap 8 — Client Factory
* [ ] Tahap 9 — TelegramFetcherBot
* [ ] Tahap 10 — Simplify `__main__.py`

---

## Detail Checklist

### Tahap 1 — UserStateManager

* [ ] Buat folder `colab_fetcher/core`
* [ ] Buat file `colab_fetcher/core/state_manager.py`
* [ ] Implement class `UserStateManager`
* [ ] Tambahkan instance `state_manager`
* [ ] Ganti seluruh `get_user_state()`
* [ ] Ganti seluruh `set_user_state()`
* [ ] Ganti seluruh `clear_user_state()`
* [ ] Test bot
* [ ] Hapus fungsi state lama dari `__main__.py`
* [ ] Commit perubahan

---

### Tahap 2 — File Utilities

* [ ] Buat file `colab_fetcher/utils/file_utils.py`
* [ ] Pindahkan `format_duration()`
* [ ] Pindahkan `smart_truncate_filename()`
* [ ] Pindahkan `sanitize_filename()`
* [ ] Pindahkan `get_file_extension()`
* [ ] Pindahkan `ext_from_mime()`
* [ ] Pindahkan `get_unique_filename()`
* [ ] Pindahkan `get_file_type()`
* [ ] Pindahkan `is_allowed_file()`
* [ ] Update seluruh import
* [ ] Test bot
* [ ] Commit perubahan

---

### Tahap 3 — Messages Module

* [ ] Buat file `colab_fetcher/messages.py`
* [ ] Pindahkan `get_start_message()`
* [ ] Pindahkan `get_tgdownload_message()`
* [ ] Pindahkan `get_progress_text()`
* [ ] Pindahkan `download_summary_message()`
* [ ] Update seluruh import
* [ ] Test bot
* [ ] Commit perubahan

---

### Tahap 4 — BatchManager

* [ ] Buat file `colab_fetcher/core/batch_manager.py`
* [ ] Implement class `BatchManager`
* [ ] Pindahkan `batch_buffer`
* [ ] Pindahkan `batch_tasks`
* [ ] Pindahkan `send_batch_message()`
* [ ] Hilangkan global state batch
* [ ] Test bot
* [ ] Commit perubahan

---

### Tahap 5 — DownloadQueueManager

* [ ] Buat file `colab_fetcher/core/queue_manager.py`
* [ ] Implement class `DownloadQueueManager`
* [ ] Pindahkan `download_queue`
* [ ] Pindahkan `active_downloads`
* [ ] Pindahkan `completed_downloads`
* [ ] Pindahkan `queue_worker()`
* [ ] Pindahkan `download_with_progress()`
* [ ] Update seluruh handler
* [ ] Hilangkan global queue state
* [ ] Test bot
* [ ] Commit perubahan

---

### Tahap 6 — Downloader Service

* [ ] Buat folder `colab_fetcher/services`
* [ ] Buat file `colab_fetcher/services/downloader.py`
* [ ] Implement class `Downloader`
* [ ] Pisahkan logika download dari queue manager
* [ ] Update dependency queue manager
* [ ] Test bot
* [ ] Commit perubahan

---

### Tahap 7 — ConfigManager

* [ ] Buat file `colab_fetcher/services/config_manager.py`
* [ ] Implement class `ConfigManager`
* [ ] Pindahkan loader `.env`
* [ ] Pindahkan writer `credentials.json`
* [ ] Pindahkan runtime config loader
* [ ] Hilangkan duplikasi `load_credentials()`
* [ ] Update import
* [ ] Test bot
* [ ] Commit perubahan

---

### Tahap 8 — Client Factory

* [ ] Refactor `utils/client.py`
* [ ] Hapus pembuatan client saat import
* [ ] Buat `create_client()`
* [ ] Update seluruh import
* [ ] Pastikan tidak ada import side effect
* [ ] Test bot
* [ ] Commit perubahan

---

### Tahap 9 — TelegramFetcherBot

* [ ] Buat file `colab_fetcher/core/bot.py`
* [ ] Implement class `TelegramFetcherBot`
* [ ] Tambahkan `register_handlers()`
* [ ] Tambahkan dependency injection
* [ ] Pindahkan handler `/start`
* [ ] Pindahkan handler `/help`
* [ ] Pindahkan handler `/tgdownload`
* [ ] Pindahkan handler file upload
* [ ] Pindahkan handler `/queue`
* [ ] Pindahkan handler `/cancelall`
* [ ] Pindahkan callback cancel
* [ ] Test seluruh fitur
* [ ] Commit perubahan

---

### Tahap 10 — Simplify **main**.py

* [ ] Buat entrypoint minimal
* [ ] Inisialisasi `TelegramFetcherBot`
* [ ] Jalankan worker dari class
* [ ] Jalankan bot dari class
* [ ] Hapus logic lama dari `__main__.py`
* [ ] Full regression test
* [ ] Commit final refactor

---

## Definition of Done

* [ ] Tidak ada global runtime state
* [ ] Queue berada di dalam class
* [ ] User state berada di dalam class
* [ ] Batch state berada di dalam class
* [ ] Client tidak dibuat saat import
* [ ] `__main__.py` < 50 baris
* [ ] Seluruh fitur lama tetap berjalan
* [ ] Struktur project sesuai target architecture
* [ ] Refactor selesai
