# mengimport library yang dibutuhkan
from utils.extract import scrape_all_products_to_dataframe
from utils.transform import transform_data
from utils.load import save_to_csv, save_to_postgres, save_to_google_sheets

# kurs untuk mengonversi harga (misal USD → IDR)
EXCHANGE_RATE = 16000  

# konfigurasi database PostgreSQL
DB_CONFIG = {
    'dbname': 'fashiondb',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5432
}

# ID spreadsheet dan nama worksheet Google Sheets
SPREADSHEET_ID    = '1v69NfqzaGnL-PZ0Tsqx_NUQAAHat5r03ueKo8RQWeO4'
WORKSHEET_NAME    = 'Sheet1'
CREDENTIALS_FILE  = 'google-sheets-api.json'

# Fungsi utama untuk menjalankan proses ETL
def main():

    # scraping data
    # jika data kosong, hentikan proses
    print("[1] Scraping data...")
    raw_data = scrape_all_products_to_dataframe()
    if raw_data.empty:
        print("[WARNING] Data kosong setelah scraping. Proses dihentikan.")
        return

    # transformasi data
    # jika data kosong, hentikan proses
    print("[2] Transformasi data...")
    transformed_data = transform_data(raw_data, EXCHANGE_RATE)
    if transformed_data.empty:
        print("[WARNING] Data kosong setelah transformasi. Proses dihentikan.")
        return

    # menyimpan data ke berbagai format
    # jika data kosong, hentikan proses
    print("[3] Menyimpan data ke CSV...")
    save_to_csv(transformed_data, 'products.csv')

    # menyimpan data ke PostgreSQL
    # jika data kosong, hentikan proses
    print("[4] Menyimpan data ke PostgreSQL...")
    save_to_postgres(transformed_data, 'fashion_products', DB_CONFIG)

    # menyimpan data ke Google Sheets
    # jika data kosong, hentikan proses
    print("[5] Menyimpan data ke Google Sheets...")
    save_to_google_sheets(
        transformed_data,
        SPREADSHEET_ID,
        WORKSHEET_NAME,
        CREDENTIALS_FILE
    )

    # jika semua proses berhasil tampilkan pesan sukses
    print("Proses ETL selesai.")

# jika file ini dijalankan sebagai skrip utama panggil fungsi main
if __name__ == "__main__":
    main()
