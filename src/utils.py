import pandas as pd
import logging
from typing import Tuple


def round_value(value: float) -> int:
    """Round a value to the nearest integer, handling .5 cases explicitly."""
    return int(value + 0.5) if value >= 0 else int(value - 0.5)


def parse_range(range_str: str) -> Tuple[float, float]:
    """Parse a range string into a tuple of floats."""
    lower, upper = map(float, range_str.split("-"))
    return lower, upper


def find_range(value: float, column: str, reference: pd.DataFrame) -> str:
    """Find the range for the given value from the reference DataFrame, considering both original and rounded values."""
    value = float(value)
    rounded_value = float(round_value(value))  # Use rounding to get the nearest integer

    # Iterate through the DataFrame rows to find the matching range
    for idx, row in reference.iterrows():
        lower, upper = parse_range(row[column])
        # Check if either the original or rounded value falls within the range
        if (lower <= value <= upper) or (lower <= rounded_value < upper):
            return row[column]

    # Raise an error if no matching range is found
    raise ValueError(
        f"Value {value} (or its rounded value {rounded_value}) does not fall into any defined range."
    )


def k_value_lookup(
    wind_value: float, cloud_value: float, reference: pd.DataFrame
) -> float:
    """Lookup the K value based on wind and cloud cover values from the reference DataFrame."""
    wind_range = find_range(wind_value, "Wind Speed Range (kn)", reference)
    cloud_range = find_range(cloud_value, "Cloud Cover Range (oktas)", reference)
    # Lookup the K value from the reference DataFrame
    k_value = reference[
        (reference["Wind Speed Range (kn)"] == wind_range)
        & (reference["Cloud Cover Range (oktas)"] == cloud_range)
    ]

    if k_value.empty:
        raise ValueError(
            f"Combination of wind range {wind_range} and cloud range {cloud_range} is not found in the reference DataFrame."
        )

    return k_value["K Value"].values[0]
