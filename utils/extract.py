# mengimport library yang dibutuhkan
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# set up logging
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR)

# konstanta untuk header permintaan
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

# fungsi untuk mengambil konten dari URL
def fetch_content(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Gagal mengambil dari {url}: {e}")
        return None

# fungsi untuk mengekstrak data produk dari elemen HTML
def extract_product_data(product, timestamp):
    try:
        product_title_tag = product.find('h3', class_='product-title')
        product_title = product_title_tag.text.strip() if product_title_tag else "Unknown Product"

        price_tag = product.find('div', class_='price-container')
        price = price_tag.find('span', class_='price').text.strip() if price_tag else "Unknown Price"

        p_tags = product.find_all('p', style="font-size: 14px; color: #777;")
        if len(p_tags) >= 4:
            rating_raw = p_tags[0].text.strip()
            rating = rating_raw.replace("Rating: ", "").replace("/ 5", "").strip()
            colors = p_tags[1].text.strip().split()[0]
            size = p_tags[2].text.strip().replace("Size:", "").strip()
            gender = p_tags[3].text.strip().replace("Gender:", "").strip()
        else:
            rating, colors, size, gender = "Unknown Rating", "Unknown Colors", "Unknown Size", "Unknown Gender"

        return {
            "Title": product_title,
            "Price": price,
            "Rating": rating,
            "Colors": colors,
            "Size": size,
            "Gender": gender,
            "Timestamp": timestamp
        }

    # menangani kesalahan jika elemen tidak ditemukan
    except Exception as e:
        logging.error(f"Gagal extract produk: {e}")
        return {
            "Title": "Unknown Product",
            "Price": "Unknown Price",
            "Rating": "Unknown Rating",
            "Colors": "Unknown Colors",
            "Size": "Unknown Size",
            "Gender": "Unknown Gender",
            "Timestamp": timestamp
        }

# fungsi utama untuk mengumpulkan semua produk ke dalam DataFrame
def scrape_all_products_to_dataframe():
    all_data = []
    for page in range(1, 51):       # mengambil 50 halaman
        url = "https://fashion-studio.dicoding.dev/" if page == 1 else f"https://fashion-studio.dicoding.dev/page{page}"
        print(f"Scraping halaman {page}: {url}")
        content = fetch_content(url)

        # jika konten tidak berhasil diambil, lanjutkan ke halaman berikutnya
        if not content:
            continue

        # parsing konten HTML
        soup = BeautifulSoup(content, "html.parser")
        articles = soup.find_all('div', class_='product-details')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for article in articles:
            data = extract_product_data(article, timestamp)
            all_data.append(data)

        time.sleep(1)   # jeda 1 detik untuk menghindari pemblokiran IP

    if not all_data:
        print("[WARNING] Tidak ada data yang berhasil diambil.")
        return pd.DataFrame()

    # mengonversi data ke DataFrame
    df = pd.DataFrame(all_data)
    print(f"[INFO] Jumlah total data yang di-scrape: {len(df)}")
    return df