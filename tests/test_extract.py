# mengimport library yang dibutuhkan
import pytest
from types import SimpleNamespace
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from utils.extract import fetch_content, extract_product_data

# dummy class untuk meniru respons HTTP
class DummyResponse:
    def __init__(self, content, status_code=200):
        self.content = content
        self._status = status_code

    # jika status code di luar 200–299, lempar HTTPError
    def raise_for_status(self):
        if not (200 <= self._status < 300):
            raise requests.HTTPError(f"Status code: {self._status}")

# fixtures: HTML sampel full dan partial
@pytest.fixture
def sample_html_full():
    """HTML produk dengan semua elemen yang diharapkan."""
    return """
    <div class="product-details">
      <h3 class="product-title">Test Shirt</h3>
      <div class="price-container"><span class="price">99.99</span></div>
      <p style="font-size: 14px; color: #777;">Rating: 4.5 / 5</p>
      <p style="font-size: 14px; color: #777;">3 Colors available</p>
      <p style="font-size: 14px; color: #777;">Size: M</p>
      <p style="font-size: 14px; color: #777;">Gender: Unisex</p>
    </div>
    """

@pytest.fixture
def sample_html_partial():
    """HTML produk dengan elemen yang kurang (p tags < 4)."""
    return """
    <div class="product-details">
      <h3 class="product-title">Mystery Item</h3>
      <div class="price-container"><span class="price">49.50</span></div>
      <p style="font-size: 14px; color: #777;">Rating: 3.0 / 5</p>
    </div>
    """

# test untuk fungsi extract_product_data dengan HTML lengkap
def test_extract_product_data_full(sample_html_full):
    timestamp = "2025-05-14 12:00:00"
    soup = BeautifulSoup(sample_html_full, "html.parser")
    product_div = soup.find("div", class_="product-details")

    # memanggil fungsi extract_product_data
    result = extract_product_data(product_div, timestamp)

    # memeriksa hasil
    assert result["Title"] == "Test Shirt"
    assert result["Price"] == "99.99"
    assert result["Rating"] == "4.5"
    assert result["Colors"] == "3"
    assert result["Size"] == "M"
    assert result["Gender"] == "Unisex"
    assert result["Timestamp"] == timestamp

# test untuk fungsi extract_product_data dengan HTML parsial
def test_extract_product_data_partial(sample_html_partial):
    timestamp = "2025-05-14 13:00:00"
    soup = BeautifulSoup(sample_html_partial, "html.parser")
    product_div = soup.find("div", class_="product-details")

    # memanggil fungsi extract_product_data
    result = extract_product_data(product_div, timestamp)

    # memeriksa hasil
    assert result["Title"] == "Mystery Item"
    assert result["Price"] == "49.50"
    assert result["Rating"] == "Unknown Rating"
    assert result["Colors"] == "Unknown Colors"
    assert result["Size"] == "Unknown Size"
    assert result["Gender"] == "Unknown Gender"
    assert result["Timestamp"] == timestamp

# test untuk fungsi fetch_content
def test_fetch_content_success(monkeypatch):
    dummy = DummyResponse(b"<html>OK</html>", status_code=200)

    # mock requests.get → kembalikan DummyResponse
    monkeypatch.setattr(requests, "get", lambda url, headers: dummy)
    content = fetch_content("http://example.com")
    assert content == b"<html>OK</html>"

# test untuk fungsi fetch_content dengan status code 404
def test_fetch_content_http_error(monkeypatch, capsys):
    dummy = DummyResponse(b"", status_code=404)

    # mock requests.get → kembalikan DummyResponse
    monkeypatch.setattr(requests, "get", lambda url, headers: dummy)
    content = fetch_content("http://notfound/")
    captured = capsys.readouterr()

    # harus mengembalikan None dan mencetak pesan error
    assert content is None
    assert "[ERROR] Gagal mengambil dari http://notfound/" in captured.out

# test untuk fungsi fetch_content dengan exception
def test_fetch_content_exception(monkeypatch, capsys):
    def raise_exc(url, headers):
        raise requests.RequestException("Timeout")
    
    # mock requests.get → lempar exception
    monkeypatch.setattr(requests, "get", raise_exc)

    content = fetch_content("http://timeout/")
    captured = capsys.readouterr()

    # harus mengembalikan None dan mencetak pesan error
    assert content is None
    assert "[ERROR] Gagal mengambil dari http://timeout/" in captured.out