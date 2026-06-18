from utils import (
    read_json,
    write_json,
    now_iso
)

from config import *

from fetch_epa_zip import (
    fetch_epa_zip
)

from extract_epa_png import (
    main as extract_epa_png
)

from fetch_weather import (
    fetch_weather
)

from fetch_rainfall import (
    fetch_rainfall
)

from fetch_tides import (
    fetch_tides
)

from forecast import (
    build_forecast
)

from merge_series import (
    merge_series
)


def build_latest():

    river = read_json(
        RIVER_JSON,
        []
    )

    river_zip = read_json(
        RIVER_ZIP_JSON,
        []
    )

    river_png = read_json(
        RIVER_PNG_JSON,
        []
    )

    rainfall = read_json(
        RAIN_JSON,
        {}
    )

    weather = read_json(
        WEATHER_JSON,
        {}
    )

    tides = read_json(
        TIDE_JSON,
        {}
    )

    forecast = read_json(
        FORECAST_JSON,
        []
    )

    metadata = read_json(
        METADATA_JSON,
        {}
    )

    current = {}

    if river:
        current = river[-1]

    latest = {

        "generated":
        now_iso(),

        "current":
        current,

        "river":
        river,

        "river_zip":
        river_zip,

        "river_png":
        river_png,

        "forecast":
        forecast,

        "rainfall":
        rainfall,

        "weather":
        weather,

        "tides":
        tides,

        "metadata":
        metadata,

        "rainfall_series":
        rainfall.get(
            "series",
            []
        ),

        "rainfall_summary":
        rainfall.get(
            "summary",
            {}
        ),

        "tide_series":
        tides.get(
            "series",
            []
        ),

        "tide_events":
        tides.get(
            "events",
            []
        ),

        "summary_12h":
        []
    }

    write_json(
        LATEST_JSON,
        latest
    )


def main():

    metadata = {

        "last_update":
        now_iso(),

        "epa_zip_ok":
        False,

        "epa_png_ok":
        False,

        "weather_ok":
        False,

        "rainfall_ok":
        False,

        "tide_ok":
        False,

        "forecast_ok":
        False
    }

    # --------------------------------------------------
    # EPA ZIP
    # --------------------------------------------------

    zip_result = (
        fetch_epa_zip()
    )

    metadata[
        "epa_zip_ok"
    ] = zip_result.get(
        "ok",
        False
    )

    # --------------------------------------------------
    # EPA PNG EXTRACTION
    # --------------------------------------------------

    png_result = (
        extract_epa_png()
    )

    metadata[
        "epa_png_ok"
    ] = png_result.get(
        "success",
        False
    )

    # --------------------------------------------------
    # WEATHER
    # --------------------------------------------------

    weather_result = (
        fetch_weather()
    )

    metadata[
        "weather_ok"
    ] = weather_result.get(
        "ok",
        False
    )

    # --------------------------------------------------
    # RAINFALL
    # --------------------------------------------------

    rain_result = (
        fetch_rainfall()
    )

    metadata[
        "rainfall_ok"
    ] = rain_result.get(
        "ok",
        False
    )

    # --------------------------------------------------
    # TIDES
    # --------------------------------------------------

    tide_result = (
        fetch_tides()
    )

    metadata[
        "tide_ok"
    ] = tide_result.get(
        "ok",
        False
    )

    # --------------------------------------------------
    # MERGE RIVER SERIES
    # IMPORTANT:
    # Forecast must use merged ZIP + PNG data
    # --------------------------------------------------

    merge_series()

    # --------------------------------------------------
    # FORECAST
    # --------------------------------------------------

    forecast_result = (
        build_forecast()
    )

    metadata[
        "forecast_ok"
    ] = forecast_result.get(
        "ok",
        False
    )

    # --------------------------------------------------
    # SAVE METADATA
    # --------------------------------------------------

    write_json(
        METADATA_JSON,
        metadata
    )

    # --------------------------------------------------
    # BUILD FRONTEND BUNDLE
    # --------------------------------------------------

    build_latest()

    print(
        "Update complete"
    )


if __name__ == "__main__":
    main()
