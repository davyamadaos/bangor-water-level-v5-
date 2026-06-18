from datetime import (
    datetime,
    timedelta,
    timezone
)

import numpy as np

from config import (
    RIVER_JSON,
    RAIN_JSON,
    FORECAST_JSON
)

from utils import (
    read_json,
    write_json
)


FORECAST_HOURS = [
    0,
    3,
    6,
    12,
    24
]


def parse_time(ts):

    return datetime.fromisoformat(
        ts.replace(
            "Z",
            "+00:00"
        )
    )


def latest_level():

    river = read_json(
        RIVER_JSON,
        []
    )

    if not river:
        return None

    return river[-1]


def calculate_rate():

    river = read_json(
        RIVER_JSON,
        []
    )

    if len(river) < 8:
        return 0

    recent = river[-8:]

    first = recent[0]
    last = recent[-1]

    t1 = parse_time(
        first["timestamp"]
    )

    t2 = parse_time(
        last["timestamp"]
    )

    hours = (
        t2 - t1
    ).total_seconds() / 3600

    if hours <= 0:
        return 0

    delta = (
        last["level_m"]
        - first["level_m"]
    )

    return delta / hours


def rainfall_forecast():

    rain = read_json(
        RAIN_JSON,
        {}
    )

    return (
        rain.get(
            "summary",
            {}
        )
    )


def confidence_from_inputs(
    rate,
    rain
):

    if abs(rate) < 0.005:

        return "high"

    if (
        rain.get(
            "next24h_mm",
            0
        ) > 25
    ):
        return "low"

    return "medium"


def rainfall_response(
    hour,
    rain_summary
):

    total = rain_summary.get(
        "next24h_mm",
        0
    )

    if total <= 0:
        return 0

    # Catchment lag

    if hour < 3:
        return 0

    if hour <= 6:
        return (
            total *
            0.001
        )

    if hour <= 12:
        return (
            total *
            0.002
        )

    return (
        total *
        0.003
    )


def recession_factor(
    hour
):

    return max(
        0.25,
        1 -
        (
            hour / 30
        )
    )


def build_forecast():

    current = latest_level()

    if not current:

        write_json(
            FORECAST_JSON,
            []
        )

        return {
            "ok": False
        }

    now_level = (
        current["level_m"]
    )

    now_time = parse_time(
        current["timestamp"]
    )

    rate = (
        calculate_rate()
    )

    rain = (
        rainfall_forecast()
    )

    confidence = (
        confidence_from_inputs(
            rate,
            rain
        )
    )

    results = []

    for hour in (
        FORECAST_HOURS
    ):

        forecast_time = (
            now_time +
            timedelta(
                hours=hour
            )
        )

        trend_component = (
            rate *
            hour *
            recession_factor(
                hour
            )
        )

        rain_component = (
            rainfall_response(
                hour,
                rain
            )
        )

        level = (
            now_level +
            trend_component +
            rain_component
        )

        basis = []

        if abs(rate) > 0.001:
            basis.append(
                "recent trend"
            )

        if (
            rain.get(
                "next24h_mm",
                0
            ) > 0
        ):
            basis.append(
                "rainfall forecast"
            )

        if not basis:
            basis.append(
                "stable river"
            )

        results.append({

            "timestamp":
            forecast_time.isoformat(),

            "level_m":
            round(
                level,
                3
            ),

            "basis":
            ", ".join(
                basis
            ),

            "confidence":
            confidence,

            "source":
            "forecast"
        })

    write_json(
        FORECAST_JSON,
        results
    )

    return {
        "ok": True,
        "count":
        len(results)
    }


if __name__ == "__main__":

    print(
        build_forecast()
    )
