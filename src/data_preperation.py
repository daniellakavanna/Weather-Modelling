import pandas as pd
import logging
from typing import Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_data_from_csv(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file into a DataFrame.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the loaded data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Data loaded successfully from file: {file_path}")
        return df
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise


def save_data_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """Save a DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to be saved.
        file_path (str): Path to save the CSV file.
    """
    try:
        df.to_csv(file_path, index=False)
        logging.info(f"Data saved successfully to file: {file_path}")
    except Exception as e:
        logging.error(f"Error saving data to file: {e}")
        raise


def create_reference_data() -> pd.DataFrame:
    """Create reference data for wind speed and cloud cover ranges and save it to a CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the reference data.
    """
    data = {
        "Wind Speed (knots)": ["0-12", "13-25", "26-38", "39-51"],
        "0-2": [-2.2, -1.1, -0.6, 1.1],
        "2-4": [-1.7, 0.0, 0.0, 1.7],
        "4-6": [-0.6, 0.6, 0.6, 2.8],
        "6-8": [0.0, 1.1, 1.1, None],  # None for missing values
    }

    reference = pd.DataFrame(data)
    save_data_to_csv(reference, "./data/processed/reference.csv")
    return reference


def create_trial_data() -> pd.DataFrame:
    """Create trial data for temperature, dew point, wind speed, and cloud cover and save it to a CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the trial data.
    """
    data = {
        "Date": [1, 1, 2, 2],
        "Location": ["A", "B", "B", "C"],
        "Midday Temperature (°C)": [22.4, 18.6, 26.0, 13.2],
        "Midday Dew Point (°C)": [10.9, 12.65, 8.5, 9.4],
        "Wind (Kn)": [14.56, 3.4, 0.0, 12.5],
        "Cloud (oktas)": [3.9, 6.0, 0.0, 4.1],
    }

    trial_data = pd.DataFrame(data)
    save_data_to_csv(trial_data, "./data/processed/trial_data.csv")
    return trial_data


def transform_reference_data(reference: pd.DataFrame) -> pd.DataFrame:
    """Transform reference data to a long format suitable for lookups and save it to a CSV file.

    Args:
        reference (pd.DataFrame): DataFrame containing reference data.

    Returns:
        pd.DataFrame: Transformed DataFrame.
    """
    formatted_rows: list[Dict[str, Optional[float]]] = []

    # Iterate through the DataFrame and create rows for each Cloud Cover Range
    for _, row in reference.iterrows():
        wind_speed_range = row["Wind Speed (knots)"]
        for cloud_cover_range in ["0-2", "2-4", "4-6", "6-8"]:
            k_value = row[cloud_cover_range]
            if pd.notna(k_value):  # Check for NaN values
                formatted_rows.append(
                    {
                        "Wind Speed Range (kn)": wind_speed_range,
                        "Cloud Cover Range (oktas)": cloud_cover_range,
                        "K Value": k_value,
                    }
                )

    transformed_df = pd.DataFrame(formatted_rows)
    save_data_to_csv(transformed_df, "./data/processed/transformed_reference.csv")
    return transformed_df
