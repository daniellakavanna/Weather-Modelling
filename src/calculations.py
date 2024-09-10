import pandas as pd
from .utils import k_value_lookup


def round_value(value: float) -> int:
    """Round a value to the nearest integer, handling .5 cases explicitly."""
    return int(value + 0.5) if value >= 0 else int(value - 0.5)


def overnight_minimum_temp(midday_temp: float, midday_dew: float, K: float) -> float:
    """Calculate the overnight minimum temperature."""
    return float(round_value((0.316 * midday_temp) + (0.548 * midday_dew) - 1.24 + K))


def calculate_overnight_temp(
    trial_data: pd.DataFrame, reference: pd.DataFrame
) -> pd.DataFrame:
    """Calculate the overnight minimum temperature for each row in the trial data."""
    trial_data["Overnight Min Temperature (°C)"] = trial_data.apply(
        lambda row: overnight_minimum_temp(
            row["Midday Temperature (°C)"],
            row["Midday Dew Point (°C)"],
            k_value_lookup(row["Wind (Kn)"], row["Cloud (oktas)"], reference),
        ),
        axis=1,
    )
    return trial_data
