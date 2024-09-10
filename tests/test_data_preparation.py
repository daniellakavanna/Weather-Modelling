import pandas as pd


def test_create_reference_data(reference_df):
    expected_data = {
        "Wind Speed (knots)": ["0-12", "13-25", "26-38", "39-51"],
        "0-2": [-2.2, -1.1, -0.6, 1.1],
        "2-4": [-1.7, 0.0, 0.0, 1.7],
        "4-6": [-0.6, 0.6, 0.6, 2.8],
        "6-8": [0.0, 1.1, 1.1, None],
    }
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(reference_df, expected_df)


def test_create_trial_data(trial_df):
    expected_data = {
        "Date": [1, 1, 2, 2],
        "Location": ["A", "B", "B", "C"],
        "Midday Temperature (°C)": [22.4, 18.6, 26.0, 13.2],
        "Midday Dew Point (°C)": [10.9, 12.65, 8.5, 9.4],
        "Wind (Kn)": [14.56, 3.4, 0.0, 12.5],
        "Cloud (oktas)": [3.9, 6.0, 0.0, 4.1],
    }
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(trial_df, expected_df)
