# Telegram Fetcher Refactor Plan (Class-Based Architecture)

## Refactor Goal

Refactor the Telegram Fetcher project, which currently relies heavily on global state and procedural code, into a class-based architecture that is:

* Easier to maintain
* Easier to test
* Easier to extend
* Less dependent on global variables
* Better at separating business logic from Telegram handlers
* Fully backward compatible with existing functionality

---

# Current Structure

```text
Telegram-Fetcher/
├── colab_fetcher/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config/
│   ├── utils/
│   │   ├── client.py
│   │   └── logging.py
│   └── my_bot.session
├── downloads/
├── .env
├── .env.example
├── main.py
└── requirements.txt
```

Current issues:

* Excessive use of global state
* `main.py` handles too many responsibilities
* Client instance is created during import
* State management is scattered across the codebase
* Queue management is mixed with Telegram handlers
* Download logic is mixed with UI logic

---

# Target Architecture

```text
colab_fetcher/

├── core/
│   ├── bot.py
│   ├── state_manager.py
│   ├── queue_manager.py
│   └── batch_manager.py
│
├── services/
│   ├── config_manager.py
│   └── downloader.py
│
├── utils/
│   ├── client.py
│   ├── logging.py
│   └── file_utils.py
│
├── messages.py
│
├── __init__.py
└── __main__.py
```

---

# Refactor Principles

DO NOT:

* Refactor the entire project at once
* Change bot behavior
* Introduce new features during refactoring

DO:

* Refactor incrementally
* Ensure the bot remains functional after each stage
* Commit every successful stage

---

# Phase 1 — UserStateManager

Goal:

Replace the following global functions:

```python
load_user_state()
save_user_state()
set_user_state()
get_user_state()
clear_user_state()
```

Create:

```text
colab_fetcher/core/state_manager.py
```

Implementation:

```python
class UserStateManager:
    async def load()
    async def save()
    async def set()
    async def get()
    async def clear()
```

Steps:

1. Create the class.
2. Add a singleton instance:

```python
state_manager = UserStateManager(STATE_FILE)
```

3. Replace all usages:

```python
await get_user_state()
```

with:

```python
await state_manager.get()
```

4. Test the bot.
5. Remove the old functions.

Commit:

```bash
git commit -m "refactor: introduce UserStateManager"
```

---

# Phase 2 — File Utilities

Create:

```text
colab_fetcher/utils/file_utils.py
```

Move the following functions:

```python
format_duration()
smart_truncate_filename()
sanitize_filename()
get_file_extension()
ext_from_mime()
get_unique_filename()
get_file_type()
is_allowed_file()
```

These should remain regular utility functions.

Update imports accordingly.

Test the bot.

Commit:

```bash
git commit -m "refactor: extract file utilities"
```

---

# Phase 3 — Messages Module

Create:

```text
colab_fetcher/messages.py
```

Move:

```python
get_start_message()
get_tgdownload_message()
get_progress_text()
download_summary_message()
```

Keep them as plain functions.

Goal:

Separate UI text generation from business logic.

Commit:

```bash
git commit -m "refactor: extract bot messages"
```

---

# Phase 4 — BatchManager

Current problem:

```python
batch_buffer = {}
batch_tasks = {}
```

These are still global variables.

Create:

```text
colab_fetcher/core/batch_manager.py
```

Implementation:

```python
class BatchManager:
    def __init__(self):
        self.buffer = {}
        self.tasks = {}

    async def add_file(...)
    async def send_batch_message(...)
```

Move:

```python
send_batch_message()
```

into the class.

Remove global variables:

```python
batch_buffer
batch_tasks
```

Commit:

```bash
git commit -m "refactor: introduce BatchManager"
```

---

# Phase 5 — Queue Manager

This is the largest refactor stage.

Create:

```text
colab_fetcher/core/queue_manager.py
```

Move:

```python
download_queue
active_downloads
completed_downloads
```

into:

```python
class DownloadQueueManager
```

Example:

```python
class DownloadQueueManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.active = {}
        self.completed = {}
```

Move:

```python
queue_worker()
download_with_progress()
```

into the class.

Telegram handlers should no longer access global variables directly.

Commit:

```bash
git commit -m "refactor: introduce DownloadQueueManager"
```

---

# Phase 6 — Downloader Service

Create:

```text
colab_fetcher/services/downloader.py
```

Move all pure download logic into:

```python
class Downloader:
    async def download(...)
```

Goal:

* QueueManager handles queue orchestration
* Downloader handles file downloading

Commit:

```bash
git commit -m "refactor: extract Downloader service"
```

---

# Phase 7 — ConfigManager

Currently, both:

```text
main.py
```

and

```text
__init__.py
```

contain configuration-related logic.

Create:

```text
colab_fetcher/services/config_manager.py
```

Implementation:

```python
class ConfigManager:
    def load_env()
    def save_runtime_config()
    def load_runtime_config()
```

Remove duplicated `load_credentials()` implementations.

Commit:

```bash
git commit -m "refactor: centralize configuration management"
```

---

# Phase 8 — Client Factory

Current implementation:

```python
app = Client(...)
```

The client instance is created during import.

Refactor to:

```python
def create_client():
    return Client(...)
```

File:

```text
colab_fetcher/utils/client.py
```

Goal:

Eliminate import-time side effects.

Commit:

```bash
git commit -m "refactor: use client factory"
```

---

# Phase 9 — TelegramFetcherBot

Create:

```text
colab_fetcher/core/bot.py
```

Implementation:

```python
class TelegramFetcherBot:
```

Dependencies:

```python
self.client
self.state_manager
self.queue_manager
self.batch_manager
```

Add:

```python
register_handlers()
```

Convert all Telegram handlers into class methods.

Example:

```python
async def start_handler(...)
async def help_handler(...)
async def tgdownload_handler(...)
```

Commit:

```bash
git commit -m "refactor: introduce TelegramFetcherBot"
```

---

# Phase 10 — Simplify main.py

Final target:

```python
from colab_fetcher.core.bot import TelegramFetcherBot

def main():
    bot = TelegramFetcherBot()
    bot.run()

if __name__ == "__main__":
    main()
```

`main.py` should become a minimal application entrypoint.

Commit:

```bash
git commit -m "refactor: simplify application entrypoint"
```

---

# Final Outcome

Remaining global variables should be limited to:

* Constants
* Configuration paths
* Logger

The following runtime global state must be eliminated:

```python
completed_downloads
active_downloads
download_queue
batch_buffer
batch_tasks
```

All runtime state should live inside dedicated classes.

Final objectives:

* Single Responsibility Principle (SRP)
* Clear dependency ownership
* Smaller, cleaner handlers
* Easier feature development
* Easier unit testing
* No dangerous import side effects
* A minimal and maintainable `main.py`

```
```
