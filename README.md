# Data-Processing

====================================
CARA MENJALANKAN SKRIP ETL PIPELINE
====================================

1. Download dan extract file ZIP proyek ini
2. Buka terminal di dalam folder hasil extract lalu ketik cmd agar mengarah ke cmd.
3. Buat virtual environment dengan code 
   -> python -m venv .env

4. Aktifkan virtual environment:
   Windows     -> .env\Scripts\activate
   macOS/Linux -> source .env/bin/activate

5. Install semua dependensi
   -> pip install -r requirements.txt

6. Setelah itu ketik
   -> code .

7. Jalankan skrip utama yaitu main.py
   -> python main.py

Script ini akan melakukan proses ETL:
- Scraping data produk fashion
- Transformasi harga ke dalam Rupiah
- Menyimpan data ke file CSV, database PostgreSQL, dan Google Sheets


============================
CARA MENJALANKAN UNIT TEST
============================

1. Pastikan sudah berada di direktori proyek tests, lalu jalankan
   -> pytest

===============================
CARA MENJALANKAN TEST COVERAGE
===============================

1. menjalankan pytest sekaligus mengukur dan menampilkan laporan coverage kode secara lengkap di terminal
   -> pytest --cov=. --cov-report=term-missing
      hasil coverage 100%

Penjelasan:
--cov=. : mengukur cakupan (coverage) kode pada direktori kerja saat ini (.) dan subfoldernya.

--cov-report=term-missing :menampilkan laporan coverage di terminal, termasuk baris kode yang tidak tercakup oleh tes (missing lines).


2. Untuk mengecek seberapa banyak kode yang telah diuji (utils):
   -> pytest --cov=utils --cov-report=term-missing -p no:pytest_postgresql
      Hasil coverage 80%
      
Penjelasan:
`--cov=utils`: menghitung coverage hanya untuk modul `utils`
`--cov-report=term-missing`: menampilkan bagian kode yang belum diuji
`-p no:pytest_postgresql`: menonaktifkan plugin pytest-postgresql jika tidak digunakan


==================
URL GOOGLE SHEETS
==================

- planning the event concept, candidate debate theme, and event objectives.
- organize the event to run smoothly from start to finish.
- help coordinate between other divisions
Hasil akhir data juga dikirim ke Google Sheets dan dapat diakses melalui link berikut:
https://docs.google.com/spreadsheets/d/1v69NfqzaGnL-PZ0Tsqx_NUQAAHat5r03ueKo8RQWeO4/edit?usp=sharing
