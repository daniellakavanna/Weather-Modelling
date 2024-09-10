from src.calculations import overnight_minimum_temp


def test_calculate_overnight_temp(sample_calculation_data):
    midday_temp = sample_calculation_data["midday_temp"]
    dew_point = sample_calculation_data["dew_point"]
    k_value = sample_calculation_data["k_value"]

    expected_result = 10.0
    result = overnight_minimum_temp(midday_temp, dew_point, k_value)
    assert result == expected_result
