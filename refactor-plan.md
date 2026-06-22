# Telegram Fetcher Refactor Plan (Class-Based Architecture)

## Tujuan Refactor

Melakukan refactor project Telegram Fetcher yang saat ini masih didominasi global state dan procedural code menjadi arsitektur berbasis class (Class-Based Components) yang:

* Mudah dipelihara
* Mudah ditest
* Mudah dikembangkan
* Mengurangi global variable
* Memisahkan business logic dari handler Telegram
* Tetap mempertahankan seluruh fitur yang sudah berjalan

---

# Struktur Saat Ini

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

Masalah utama:

* Terlalu banyak global state
* **main**.py memegang terlalu banyak responsibility
* Client dibuat saat import
* State management tersebar
* Queue management bercampur dengan handler Telegram
* Download logic bercampur dengan UI logic

---

# Target Arsitektur

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

# Prinsip Refactor

JANGAN:

* Refactor seluruh project sekaligus
* Mengubah behavior bot
* Mengubah fitur saat refactor

LAKUKAN:

* Refactor bertahap
* Pastikan bot tetap berjalan setelah setiap tahap
* Commit setiap tahap yang berhasil

---

# Tahap 1 — UserStateManager

Tujuan:

Menghilangkan fungsi global:

```python
load_user_state()
save_user_state()
set_user_state()
get_user_state()
clear_user_state()
```

Buat:

```text
colab_fetcher/core/state_manager.py
```

Implementasi:

```python
class UserStateManager:
    async def load()
    async def save()
    async def set()
    async def get()
    async def clear()
```

Langkah:

1. Buat class
2. Tambahkan instance:

```python
state_manager = UserStateManager(STATE_FILE)
```

3. Ganti semua pemanggilan:

```python
await get_user_state()
```

menjadi

```python
await state_manager.get()
```

4. Test bot
5. Hapus fungsi lama

Commit:

```bash
git commit -m "refactor: introduce UserStateManager"
```

---

# Tahap 2 — File Utilities

Buat:

```text
colab_fetcher/utils/file_utils.py
```

Pindahkan:

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

Semua tetap function biasa.

Tidak perlu class.

Update import.

Test bot.

Commit:

```bash
git commit -m "refactor: extract file utilities"
```

---

# Tahap 3 — Messages Module

Buat:

```text
colab_fetcher/messages.py
```

Pindahkan:

```python
get_start_message()
get_tgdownload_message()
get_progress_text()
download_summary_message()
```

Semua tetap function.

Tujuan:

Memisahkan UI text dari business logic.

Commit:

```bash
git commit -m "refactor: extract bot messages"
```

---

# Tahap 4 — BatchManager

Masalah saat ini:

```python
batch_buffer = {}
batch_tasks = {}
```

Masih global.

Buat:

```text
colab_fetcher/core/batch_manager.py
```

Implementasi:

```python
class BatchManager:
    def __init__(self):
        self.buffer = {}
        self.tasks = {}

    async def add_file(...)
    async def send_batch_message(...)
```

Pindahkan:

```python
send_batch_message()
```

ke class.

Hilangkan global:

```python
batch_buffer
batch_tasks
```

Commit:

```bash
git commit -m "refactor: introduce BatchManager"
```

---

# Tahap 5 — Queue Manager

Ini bagian terbesar.

Buat:

```text
colab_fetcher/core/queue_manager.py
```

Pindahkan:

```python
download_queue
active_downloads
completed_downloads
```

ke:

```python
class DownloadQueueManager
```

Contoh:

```python
class DownloadQueueManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.active = {}
        self.completed = {}
```

Pindahkan:

```python
queue_worker()
download_with_progress()
```

ke dalam class.

Handler tidak lagi mengakses global variable.

Commit:

```bash
git commit -m "refactor: introduce DownloadQueueManager"
```

---

# Tahap 6 — Downloader Service

Buat:

```text
colab_fetcher/services/downloader.py
```

Pindahkan logika download murni.

Contoh:

```python
class Downloader:
    async def download(...)
```

Tujuan:

QueueManager hanya mengatur antrian.

Downloader hanya mengurus download.

Commit:

```bash
git commit -m "refactor: extract Downloader service"
```

---

# Tahap 7 — ConfigManager

Gabungkan:

main.py

dan

**init**.py

yang saat ini sama-sama mengelola konfigurasi.

Buat:

```text
colab_fetcher/services/config_manager.py
```

Implementasi:

```python
class ConfigManager:
    def load_env()
    def save_runtime_config()
    def load_runtime_config()
```

Hilangkan duplikasi load_credentials().

Commit:

```bash
git commit -m "refactor: centralize configuration management"
```

---

# Tahap 8 — Client Factory

Saat ini:

```python
app = Client(...)
```

langsung dibuat saat import.

Ubah menjadi:

```python
def create_client():
    return Client(...)
```

File:

```text
colab_fetcher/utils/client.py
```

Tujuan:

Menghilangkan import side effect.

Commit:

```bash
git commit -m "refactor: use client factory"
```

---

# Tahap 9 — TelegramFetcherBot

Buat:

```text
colab_fetcher/core/bot.py
```

Implementasi:

```python
class TelegramFetcherBot:
```

Memiliki dependency:

```python
self.client
self.state_manager
self.queue_manager
self.batch_manager
```

Tambahkan:

```python
register_handlers()
```

Semua handler menjadi method class.

Contoh:

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

# Tahap 10 — Sederhanakan **main**.py

Target akhir:

```python
from colab_fetcher.core.bot import TelegramFetcherBot

def main():
    bot = TelegramFetcherBot()
    bot.run()

if __name__ == "__main__":
    main()
```

File ini hanya menjadi entrypoint.

Commit:

```bash
git commit -m "refactor: simplify application entrypoint"
```

---

# Hasil Akhir

Global variable yang tersisa:

* Konstanta
* Configuration path
* Logger

Global state berikut harus hilang:

```python
completed_downloads
active_downloads
download_queue
batch_buffer
batch_tasks
```

Seluruh state runtime harus berada di dalam class.

Target akhir:

* Single Responsibility Principle
* Dependency lebih jelas
* Handler lebih kecil
* Mudah menambah fitur baru
* Mudah unit testing
* Tidak ada import side effect yang berbahaya
* **main**.py menjadi sangat kecil

```
```
