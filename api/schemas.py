from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class AirportsResponse(BaseModel):
    airports: List[str]

class ForecastResponse(BaseModel):
    airport: str
    last_observed_month: date
    forecast_month: date
    horizon: int
    predicted_avg_delay_minutes: float
    lower_95: Optional[float] = None
    upper_95: Optional[float] = None
    model_used: str
