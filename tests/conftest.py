import pytest
import pandas as pd
from src.data_preperation import create_reference_data, create_trial_data


@pytest.fixture
def reference_df():
    """Fixture to provide the reference DataFrame."""
    return create_reference_data()


@pytest.fixture
def trial_df():
    """Fixture to provide the trial DataFrame."""
    return create_trial_data()


@pytest.fixture
def sample_calculation_data():
    """Fixture to provide sample data for calculation tests."""
    return {"midday_temp": 18, "dew_point": 10, "k_value": 0}
