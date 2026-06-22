# 🚀 Refactor Progress Tracker

## Current Status

* [ ] Phase 1 — UserStateManager
* [ ] Phase 2 — File Utilities
* [ ] Phase 3 — Messages Module
* [ ] Phase 4 — BatchManager
* [ ] Phase 5 — DownloadQueueManager
* [ ] Phase 6 — Downloader Service
* [ ] Phase 7 — ConfigManager
* [ ] Phase 8 — Client Factory
* [ ] Phase 9 — TelegramFetcherBot
* [ ] Phase 10 — Simplify `__main__.py`

---

## Detail Checklist

### Phase 1 — UserStateManager

* [ ] Create directory `colab_fetcher/core`
* [ ] Create file `colab_fetcher/core/state_manager.py`
* [ ] Implement `UserStateManager` class
* [ ] Add `state_manager` instance
* [ ] Refactor all `get_user_state()` calls
* [ ] Refactor all `set_user_state()` calls
* [ ] Refactor all `clear_user_state()` calls
* [ ] Test bot functionality
* [ ] Remove legacy state functions from `__main__.py`
* [ ] Commit changes

---

### Phase 2 — File Utilities

* [ ] Create file `colab_fetcher/utils/file_utils.py`
* [ ] Migrate `format_duration()`
* [ ] Migrate `smart_truncate_filename()`
* [ ] Migrate `sanitize_filename()`
* [ ] Migrate `get_file_extension()`
* [ ] Migrate `ext_from_mime()`
* [ ] Migrate `get_unique_filename()`
* [ ] Migrate `get_file_type()`
* [ ] Migrate `is_allowed_file()`
* [ ] Update all imports
* [ ] Test bot functionality
* [ ] Commit changes

---

### Phase 3 — Messages Module

* [ ] Create file `colab_fetcher/messages.py`
* [ ] Migrate `get_start_message()`
* [ ] Migrate `get_tgdownload_message()`
* [ ] Migrate `get_progress_text()`
* [ ] Migrate `download_summary_message()`
* [ ] Update all imports
* [ ] Test bot functionality
* [ ] Commit changes

---

### Phase 4 — BatchManager

* [ ] Create file `colab_fetcher/core/batch_manager.py`
* [ ] Implement `BatchManager` class
* [ ] Migrate `batch_buffer`
* [ ] Migrate `batch_tasks`
* [ ] Migrate `send_batch_message()`
* [ ] Eliminate global batch state
* [ ] Test bot functionality
* [ ] Commit changes

---

### Phase 5 — DownloadQueueManager

* [ ] Create file `colab_fetcher/core/queue_manager.py`
* [ ] Implement `DownloadQueueManager` class
* [ ] Migrate `download_queue`
* [ ] Migrate `active_downloads`
* [ ] Migrate `completed_downloads`
* [ ] Migrate `queue_worker()`
* [ ] Migrate `download_with_progress()`
* [ ] Update all handlers
* [ ] Eliminate global queue state
* [ ] Test bot functionality
* [ ] Commit changes

---

### Phase 6 — Downloader Service

* [ ] Create directory `colab_fetcher/services`
* [ ] Create file `colab_fetcher/services/downloader.py`
* [ ] Implement `Downloader` class
* [ ] Decouple download logic from queue manager
* [ ] Update queue manager dependencies
* [ ] Test bot functionality
* [ ] Commit changes

---

### Phase 7 — ConfigManager

* [ ] Create file `colab_fetcher/services/config_manager.py`
* [ ] Implement `ConfigManager` class
* [ ] Migrate `.env` loader
* [ ] Migrate `credentials.json` writer
* [ ] Migrate runtime configuration loader
* [ ] Remove `load_credentials()` duplication
* [ ] Update imports
* [ ] Test bot functionality
* [ ] Commit changes

---

### Phase 8 — Client Factory

* [ ] Refactor `utils/client.py`
* [ ] Remove client initialization upon import
* [ ] Create `create_client()` function
* [ ] Update all imports
* [ ] Ensure no import side effects
* [ ] Commit changes

---

### Phase 9 — TelegramFetcherBot

* [ ] Create file `colab_fetcher/core/bot.py`
* [ ] Implement `TelegramFetcherBot` class
* [ ] Add `register_handlers()` method
* [ ] Add dependency injection
* [ ] Migrate `/start` handler
* [ ] Migrate `/help` handler
* [ ] Migrate `/tgdownload` handler
* [ ] Migrate file upload handler
* [ ] Migrate `/queue` handler
* [ ] Migrate `/cancelall` handler
* [ ] Migrate cancel callback
* [ ] Test all features
* [ ] Commit changes

---

### Phase 10 — Simplify `__main__.py`

* [ ] Create minimal entrypoint
* [ ] Initialize `TelegramFetcherBot`
* [ ] Run worker from the class
* [ ] Run bot from the class
* [ ] Remove legacy logic from `__main__.py`
* [ ] Perform full regression testing
* [ ] Commit final refactor

---

## Definition of Done

* [ ] No global runtime state
* [ ] Queue contained within class
* [ ] User state contained within class
* [ ] Batch state contained within class
* [ ] Client initialized on-demand (no import-time init)
* [ ] `__main__.py` < 50 lines
* [ ] All legacy features fully operational
* [ ] Project structure aligns with target architecture
* [ ] Refactor completed
