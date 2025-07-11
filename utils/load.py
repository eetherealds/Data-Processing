# mengimport library yang dibutuhkan
import os
import pandas as pd
import psycopg2
from psycopg2 import sql, OperationalError
import gspread
from google.oauth2.service_account import Credentials
import logging

# menyimpan data ke dalam file CSV
def save_to_csv(data: pd.DataFrame, filename: str) -> None:
    try:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        data.to_csv(filename, index=False)
        logging.info(f"CSV saved: {filename}")
    except Exception as e:
        logging.error(f"Failed to save CSV '{filename}': {e}")

# menyimpan data ke dalam database PostgreSQL
def save_to_postgres(data: pd.DataFrame, table_name: str, db_config: dict):
    try:
        conn = psycopg2.connect(
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config.get('port', 5432)
        )
        cur = conn.cursor()

        # membuat tabel jika belum ada
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                Title TEXT,
                Price FLOAT,
                Rating FLOAT,
                Colors TEXT,
                Size TEXT,
                Gender TEXT,
                Timestamp TIMESTAMP
            )
        """).format(sql.Identifier(table_name))
        cur.execute(create_table_query)

        # menyimpan data ke dalam tabel
        for _, row in data.iterrows():
            insert_query = sql.SQL("""
                INSERT INTO {} (Title, Price, Rating, Colors, Size, Gender, Timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """).format(sql.Identifier(table_name))
            cur.execute(insert_query, tuple(row))

        # commit perubahan
        conn.commit()
        cur.close()
        conn.close()
        print(f"[INFO] Data berhasil disimpan ke PostgreSQL table '{table_name}'")

    # menangani kesalahan koneksi
    except OperationalError as oe:
        print(f"[ERROR] Koneksi ke PostgreSQL gagal: {oe}")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan data ke PostgreSQL: {e}")

# menyimpan data ke dalam Google Sheets
def save_to_google_sheets(data: pd.DataFrame, spreadsheet_id: str, worksheet_name: str, creds_file: str):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
        client = gspread.authorize(creds)

        # membuka spreadsheet
        sheet = client.open_by_key(spreadsheet_id)
        try:
            worksheet = sheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")

        # menyimpan data ke worksheet
        worksheet.clear()
        worksheet.update([data.columns.values.tolist()] + data.values.tolist())
        print(f"[INFO] Data berhasil disimpan ke Google Sheets ID: {spreadsheet_id} -> {worksheet_name}")

    # menangani kesalahan saat menyimpan ke Google Sheets
    except FileNotFoundError:
        print(f"[ERROR] File kredensial Google Sheets tidak ditemukan: {creds_file}")
    except gspread.exceptions.APIError as e:
        print(f"[ERROR] Google Sheets API error: {e}")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan ke Google Sheets: {e}")