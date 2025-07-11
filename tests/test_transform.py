# mengimport library yang dibutuhkan
import pandas as pd
import pytest
from pandas.api.types import is_string_dtype, is_float_dtype
from utils.transform import transform_data

# fixture raw_df: data mentah contoh
@pytest.fixture
def raw_df():
    """Fixture untuk menyediakan DataFrame mentah untuk pengujian."""
    data = {
        "Title": [
            "Good Shirt",
            "Unknown Product",
            "Fancy Pants",
            "Bad Data",
            "Fancy Pants"  
        ],
        "Price": [
            "$10.00",   
            "$20.00",    
            "30.50",     
            "not a price",  
            "30.50"      
        ],
        "Rating": [
            "4.0",       
            "5.0",       
            "3.5 stars", 
            "n/a",       
            "3.5 stars"  
        ],
        "Colors": ["Red", "Blue", "Green", "Yellow", "Green"],
        "Size": ["M", "L", "S", "XL", "S"],
        "Gender": ["Unisex", "Male", "Female", "Male", "Female"],
        "Timestamp": [
            "2025-05-14 10:00:00",
            "2025-05-14 10:05:00",
            "2025-05-14 10:10:00",
            "2025-05-14 10:15:00",
            "2025-05-14 10:10:00"
        ]
    }
    return pd.DataFrame(data)

# test tranforrm basic
def test_transform_basic(raw_df):
    rate = 2.0
    df = transform_data(raw_df, exchange_rate=rate)

    # hanya 2 baris valid tersisa
    assert len(df) == 2
    assert set(df["Title"].tolist()) == {"Good Shirt", "Fancy Pants"}

    # harga dikonversi & dikali rate
    good_price = df.loc[df["Title"] == "Good Shirt", "Price"].iloc[0]
    fancy_price = df.loc[df["Title"] == "Fancy Pants", "Price"].iloc[0]
    assert pytest.approx(good_price) == 10.00 * rate
    assert pytest.approx(fancy_price) == 30.50 * rate

    # rating dikonversi ke float
    good_rating = df.loc[df["Title"] == "Good Shirt", "Rating"].iloc[0]
    fancy_rating = df.loc[df["Title"] == "Fancy Pants", "Rating"].iloc[0]
    assert isinstance(good_rating, float)
    assert isinstance(fancy_rating, float)
    assert good_rating == 4.0
    assert fancy_rating == 3.5

    # urutan kolom sesuai
    expected_cols = ["Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"]
    assert df.columns.tolist() == expected_cols

# test tipe data kolom string
def test_string_dtypes(raw_df):
    df = transform_data(raw_df, exchange_rate=1.0)
    assert is_string_dtype(df["Title"].dtype)
    assert is_string_dtype(df["Size"].dtype)
    assert is_string_dtype(df["Gender"].dtype)

# test penghapusan kolom unknown dan NaN
def test_drop_unknown_and_nan(raw_df):
    df = transform_data(raw_df, exchange_rate=1.0)
    assert not (df["Title"] == "Unknown Product").any()
    assert not df["Price"].isna().any()
    assert not df["Rating"].isna().any()

# test penghapusan duplikasi
def test_drop_duplicates(raw_df):
    rate = 1.0
    df = transform_data(raw_df, exchange_rate=rate)
    assert df[df["Title"] == "Fancy Pants"].shape[0] == 1

# test error handling saat kolom hilang
def test_error_handling_missing_column():
    df_bad = pd.DataFrame({"Foo": [1,2,3]})
    result = transform_data(df_bad, exchange_rate=1.0)
    assert result.empty