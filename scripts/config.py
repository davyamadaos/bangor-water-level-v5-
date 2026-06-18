from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DEBUG_DIR = DATA_DIR / "debug"

EPA_ZIP_URL = (
    "https://epawebapp.epa.ie/Hydronet/output/"
    "internet/stations/CAS/33008/S/3_months.zip"
)

EPA_PNG_URL = (
    "https://epawebapp.epa.ie/Hydronet/output/"
    "internet/stations/CAS/33008/S/"
    "extralarge_3m_extralarge.png"
)

LATEST_JSON = DATA_DIR / "latest.json"

RIVER_JSON = DATA_DIR / "river.json"
RIVER_ZIP_JSON = DATA_DIR / "river_zip.json"
RIVER_PNG_JSON = DATA_DIR / "river_png_derived.json"

RAIN_JSON = DATA_DIR / "rainfall.json"
WEATHER_JSON = DATA_DIR / "weather.json"

TIDE_JSON = DATA_DIR / "tide.json"

FORECAST_JSON = DATA_DIR / "forecast.json"

METADATA_JSON = DATA_DIR / "metadata.json"

DEBUG_DIR.mkdir(
    parents=True,
    exist_ok=True
)
