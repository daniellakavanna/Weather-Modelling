from pydantic import BaseModel, Field, ValidationError


# Define Pydantic model for user input validation
class WeatherInput(BaseModel):
    midday_temp: float = Field(
        ..., gt=-50, lt=60, description="Midday temp must be between -50 and 60°C"
    )
    dew_point_temp: float = Field(
        ..., gt=-50, lt=50, description="Dew point must be between -50 and 50°C"
    )
    wind_speed: float = Field(
        ..., gt=0, lt=52, description="Wind speed must be between 0 and 52 knots"
    )
    cloud_cover: int = Field(
        ..., ge=0, le=8, description="Cloud cover must be between 0 and 8 oktas"
    )
