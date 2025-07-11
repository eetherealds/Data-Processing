# mengimport library yang dibutuhkan
import pandas as pd

# fungsi untuk mentransformasi data
def transform_data(df: pd.DataFrame, exchange_rate: float) -> pd.DataFrame:
    try:
        df['Price'] = pd.to_numeric(
        df['Price'].replace(r'[\$,]', '', regex=True), errors='coerce'
        ) * exchange_rate

        # menghapus simbol mata uang dan mengonversi ke float
        df['Rating'] = df['Rating'].str.extract(r'(\d+(\.\d+)?)')[0].astype(float)

        # mengonversi kolom ke tipe data yang sesuai
        df['Title'] = df['Title'].astype('string')
        df['Size'] = df['Size'].astype('string')
        df['Gender'] = df['Gender'].astype('string')

        df = df[df['Title'] != 'Unknown Product'].copy()

       # menghapus baris yang tidak memiliki harga atau rating 
        df = df.dropna(subset=['Price', 'Rating'])

        # menghapus baris yang memiliki duplikasi
        df = df.drop_duplicates()

        df = df[['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'Timestamp']]

        return df

    # mengatasi kesalahan saat mentransformasi data
    except Exception as e:
        print(f"[ERROR] Gagal melakukan transformasi data: {e}")
        return pd.DataFrame()