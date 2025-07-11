# mengimport library yang dibutuhkan
import os
import pandas as pd
import psycopg2
import gspread
import pytest
from psycopg2 import OperationalError
from google.oauth2.service_account import Credentials
from utils.load import save_to_csv, save_to_postgres, save_to_google_sheets

# dummy classes untuk mocking PostgreSQL
class DummyCursor:
    def __init__(self):
        self.queries = []

    def execute(self, query, args=None):
        self.queries.append((query, args))

    def close(self):
        pass

class DummyConn:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def close(self):
        pass

# dummy classes untuk mocking Google Sheets
class DummyWorksheet:
    def __init__(self):
        self.cleared = False
        self.updated = None

    def clear(self):
        self.cleared = True

    def update(self, data):
        self.updated = data

class DummySheet:
    def __init__(self, worksheet=None, throw_notfound=False):
        self._ws = worksheet or DummyWorksheet()
        self._throw = throw_notfound

    def worksheet(self, name):
        if self._throw:
            raise gspread.exceptions.WorksheetNotFound("no ws")
        return self._ws

    def add_worksheet(self, title, rows, cols):
        self._ws = DummyWorksheet()
        return self._ws

class DummyClient:
    def __init__(self, sheet):
        self._sheet = sheet

    def open_by_key(self, key):
        return self._sheet

# test untuk fungsi save_to_csv
def test_save_to_csv_success(tmp_path, caplog):
    caplog.set_level("INFO")
    df = pd.DataFrame({"col":[1,2,3]})
    out = tmp_path / "sub" / "out.csv"

    save_to_csv(df, str(out))

    # pastikan direktori ada
    assert out.exists()
    df2 = pd.read_csv(str(out))
    pd.testing.assert_frame_equal(df, df2)
    assert any("CSV saved" in rec.message for rec in caplog.records)

# test untuk fungsi save_to_csv dengan path yang tidak valid
def test_save_to_csv_failure(monkeypatch, tmp_path, caplog):
    caplog.set_level("ERROR")
    df = pd.DataFrame({"col":[1]})
    out = tmp_path / "file.csv"
    monkeypatch.setattr(pd.DataFrame, "to_csv",
                        lambda self, *args, **kwargs: (_ for _ in ()).throw(Exception("disk full")))

    # pastikan direktori tidak ada
    save_to_csv(df, str(out))
    assert any("Failed to save CSV" in rec.message for rec in caplog.records)

# test untuk fungsi save_to_postgres
def test_save_to_postgres_success(monkeypatch, capsys):
    df = pd.DataFrame([["T1", 1.1, 4.4, "Red", "M", "Uni", "ts"]],
                      columns=["Title","Price","Rating","Colors","Size","Gender","Timestamp"])
    dummy_cur = DummyCursor()
    dummy_conn = DummyConn(dummy_cur)
    monkeypatch.setattr(psycopg2, "connect", lambda **kwargs: dummy_conn)

    # mock konfigurasi PostgreSQL
    cfg = {"dbname":"db","user":"u","password":"p","host":"h"}
    save_to_postgres(df, "mytable", cfg)

    # pastikan koneksi berhasil
    out = capsys.readouterr().out
    assert "[INFO] Data berhasil disimpan ke PostgreSQL table 'mytable'" in out
    assert any("CREATE TABLE IF NOT EXISTS" in str(q[0]) for q in dummy_cur.queries)
    assert any("INSERT INTO" in str(q[0]) for q in dummy_cur.queries)
    assert dummy_conn.committed

# test untuk fungsi save_to_postgres dengan koneksi yang gagal
def test_save_to_postgres_operational_error(monkeypatch, capsys):
    monkeypatch.setattr(psycopg2, "connect",
                        lambda **kwargs: (_ for _ in ()).throw(OperationalError("conn fail")))
    cfg = {"dbname":"db","user":"u","password":"p","host":"h"}

    # mock DataFrame kosong
    save_to_postgres(pd.DataFrame(), "tbl", cfg)
    out = capsys.readouterr().out
    assert "Koneksi ke PostgreSQL gagal: conn fail" in out

# test untuk fungsi save_to_postgres dengan kesalahan saat menyimpan data
def test_save_to_postgres_generic_error(monkeypatch, capsys):
    class BadCursor(DummyCursor):
        def execute(self, query, args=None):
            raise Exception("bad insert")
    bad_conn = DummyConn(BadCursor())
    monkeypatch.setattr(psycopg2, "connect", lambda **kwargs: bad_conn)
    cfg = {"dbname":"db","user":"u","password":"p","host":"h"}

    # mock DataFrame kosong
    save_to_postgres(pd.DataFrame(), "tbl", cfg)
    out = capsys.readouterr().out
    assert "Gagal menyimpan data ke PostgreSQL: bad insert" in out

def test_save_to_google_sheets_add_new_worksheet(monkeypatch, capsys):
    df = pd.DataFrame({"Z": [1]})
    sheet = DummySheet(throw_notfound=True)  # simulate worksheet not found
    client = DummyClient(sheet)

    monkeypatch.setattr(Credentials, "from_service_account_file", lambda f, scopes: "cred")
    monkeypatch.setattr(gspread, "authorize", lambda creds: client)

    save_to_google_sheets(df, "spreadsheet_id", "ws", "creds.json")
    out = capsys.readouterr().out
    assert "[INFO] Data berhasil disimpan ke Google Sheets ID: spreadsheet_id -> ws" in out
    assert sheet._ws.updated is not None  # memastikan update berhasil dilakukan

# test untuk fungsi save_to_google_sheets
def test_save_to_google_sheets_success(monkeypatch, capsys):
    df = pd.DataFrame({"A": [1], "B": [2]})
    dummy_ws = DummyWorksheet()
    sheet = DummySheet(worksheet=dummy_ws)
    client = DummyClient(sheet)

    # mock Google Sheets API
    monkeypatch.setattr(Credentials, "from_service_account_file", lambda f, scopes: "cred")
    monkeypatch.setattr(gspread, "authorize", lambda creds: client)

    save_to_google_sheets(df, "spreadsheet_id", "ExistingWS", "creds.json")
    out = capsys.readouterr().out
    
    assert dummy_ws.cleared is True
    assert dummy_ws.updated is not None
    assert "[INFO] Data berhasil disimpan ke Google Sheets ID: spreadsheet_id -> ExistingWS" in out

# test untuk fungsi save_to_google_sheets
def test_save_to_google_sheets_api_error(monkeypatch, capsys):
    df = pd.DataFrame({"Z":[0]})
    dummy_ws = DummyWorksheet()
    sheet = DummySheet(worksheet=dummy_ws)
    client = DummyClient(sheet)

    # mock Google Sheets API
    monkeypatch.setattr(Credentials, "from_service_account_file", lambda f, scopes: "cred")
    monkeypatch.setattr(gspread, "authorize", lambda creds: client)
    monkeypatch.setattr(
        DummyWorksheet, 
        "update",
        lambda self, d: (_ for _ in ()).throw(gspread.exceptions.APIError("api fail"))
    )

    # mock DataFrame kosong
    save_to_google_sheets(df, "sid3", "ws", "creds.json")
    out = capsys.readouterr().out
    assert "[ERROR] Gagal menyimpan ke Google Sheets" in out