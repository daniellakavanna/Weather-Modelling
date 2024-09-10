import pytest
import pandas as pd
from src.utils import find_range, k_value_lookup


def test_find_range():
    data = {
        "Wind Speed Range (kn)": ["0-10", "10-20", "20-30"],
        "Cloud Cover Range (oktas)": ["0-5", "6-10", "10-15"],
    }
    df = pd.DataFrame(data)

    assert find_range(5, "Wind Speed Range (kn)", df) == "0-10"
    assert find_range(15, "Wind Speed Range (kn)", df) == "10-20"
    assert find_range(25, "Wind Speed Range (kn)", df) == "20-30"
    assert find_range(7.2, "Cloud Cover Range (oktas)", df) == "6-10"
    assert find_range(12, "Cloud Cover Range (oktas)", df) == "10-15"

    with pytest.raises(ValueError):
        find_range(100, "Wind Speed Range (kn)", df)


def test_k_lookup():
    data = {
        "Wind Speed Range (kn)": ["0-10", "10-20", "20-30"],
        "Cloud Cover Range (oktas)": ["0-5", "5-10", "10-15"],
        "K Value": [1, 2, 3],
    }
    df = pd.DataFrame(data)

    assert k_value_lookup(5, 5, df) == 1
    assert k_value_lookup(15, 7, df) == 2
    assert k_value_lookup(25, 12, df) == 3

    with pytest.raises(ValueError):
        k_value_lookup(100, 100, df)
