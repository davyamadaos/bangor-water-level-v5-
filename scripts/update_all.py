from datetime import datetime

from utils import (
    read_json,
    write_json,
    now_iso
)

from config import *

from fetch_epa_zip import (
    fetch_epa_zip
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
        now_iso()
    }

    zip_result = (
        fetch_epa_zip()
    )

    metadata[
        "epa_zip_ok"
    ] = zip_result["ok"]

    metadata[
        "epa_png_ok"
    ] = False

    metadata[
        "weather_ok"
    ] = False

    metadata[
        "rainfall_ok"
    ] = False

    metadata[
        "tide_ok"
    ] = False

    write_json(
        METADATA_JSON,
        metadata
    )

    merge_series()

    build_latest()

    print(
        "Update complete"
    )


if __name__ == "__main__":
    main()
