from datetime import (
    datetime,
    timedelta,
    timezone
)

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

    if not ts:
        return None

    try:

        return datetime.fromisoformat(
            ts.replace(
                "Z",
                "+00:00"
            )
        )

    except Exception:

        return None


def latest_level():

    river = read_json(
        RIVER_JSON,
        []
    )

    if not river:
        return None

    latest = river[-1]

    return {

        "timestamp":
        latest.get(
            "timestamp"
        ),

        "level_m":
        latest.get(
            "level_m"
        ),

        "source":
        latest.get(
            "source",
            "unknown"
        ),

        "confidence":
        latest.get(
            "confidence",
            "medium"
        )
    }


def observation_age_hours(
    timestamp
):

    try:

        dt = parse_time(
            timestamp
        )

        if not dt:
            return 999

        now = datetime.now(
            timezone.utc
        )

        return (
            now - dt
        ).total_seconds() / 3600

    except Exception:

        return 999


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
        first.get(
            "timestamp"
        )
    )

    t2 = parse_time(
        last.get(
            "timestamp"
        )
    )

    if not t1 or not t2:
        return 0

    hours = (
        t2 - t1
    ).total_seconds() / 3600

    if hours <= 0:
        return 0

    try:

        delta = (
            float(
                last["level_m"]
            )
            -
            float(
                first["level_m"]
            )
        )

        return delta / hours

    except Exception:

        return 0


def rainfall_summary():

    rain = read_json(
        RAIN_JSON,
        {}
    )

    return rain.get(
        "summary",
        {}
    )


def confidence_from_inputs(
    rate,
    rain,
    age_hours
):

    if age_hours > 24:
        return "low"

    if (
        rain.get(
            "next24h_mm",
            0
        ) > 30
    ):
        return "low"

    if abs(rate) < 0.002:
        return "high"

    return "medium"


def rainfall_response(
    hour,
    rain
):

    total = rain.get(
        "next24h_mm",
        0
    )

    if total <= 0:
        return 0

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


def trend_label(rate):

    mm_hr = (
        rate * 1000
    )

    if mm_hr > 2:
        return "rising"

    if mm_hr < -2:
        return "falling"

    return "stable"


def build_basis(
    rate,
    rain
):

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

    return ", ".join(
        basis
    )


def build_forecast():

    current = latest_level()

    if not current:

        write_json(
            FORECAST_JSON,
            []
        )

        return {
            "ok": False,
            "error":
            "No river data"
        }

    now_level = current.get(
        "level_m"
    )

    now_time = parse_time(
        current.get(
            "timestamp"
        )
    )

    if (
        now_level is None
        or
        not now_time
    ):

        write_json(
            FORECAST_JSON,
            []
        )

        return {
            "ok": False,
            "error":
            "Invalid current observation"
        }

    rate = calculate_rate()

    rain = rainfall_summary()

    age_hours = (
        observation_age_hours(
            current[
                "timestamp"
            ]
        )
    )

    confidence = (
        confidence_from_inputs(
            rate,
            rain,
            age_hours
        )
    )

    trend = trend_label(
        rate
    )

    forecast = []

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

        forecast.append({

            "timestamp":
            forecast_time.isoformat(),

            "hours_ahead":
            hour,

            "level_m":
            round(
                level,
                3
            ),

            "basis":
            build_basis(
                rate,
                rain
            ),

            "confidence":
            confidence,

            "source":
            "forecast",

            "trend":
            trend,

            "starting_level":
            round(
                now_level,
                3
            ),

            "starting_level_source":
            current.get(
                "source"
            ),

            "starting_level_confidence":
            current.get(
                "confidence"
            ),

            "observation_age_hours":
            round(
                age_hours,
                1
            )
        })

    write_json(
        FORECAST_JSON,
        forecast
    )

    return {

        "ok": True,

        "count":
        len(
            forecast
        ),

        "trend":
        trend,

        "confidence":
        confidence
    }


if __name__ == "__main__":

    result = (
        build_forecast()
    )

    print(
        result
    )
