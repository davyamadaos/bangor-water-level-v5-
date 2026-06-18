import pandas as pd
import requests

from datetime import (
    datetime,
    timezone
)

from config import (
    TIDE_JSON
)

from utils import (
    write_json
)

HIGHLOW_URL = (
    "https://erddap.marine.ie/erddap/"
    "tabledap/"
    "IMI_TidePrediction_HighLow.csv"
    "?stationID,time,longitude,"
    "latitude,tide_time_category,"
    "Water_Level_ODMalin"
    "&stationID=%22Ballyglass%22"
    "&time%3E=now-30days"
    "&time%3C=now%2B14days"
)

SERIES_URL = (
    "https://erddap.marine.ie/erddap/"
    "tabledap/"
    "IMI-TidePrediction.csv"
    "?time,longitude,latitude,"
    "stationID,Water_Level,"
    "Water_Level_ODM"
    "&stationID=%22Ballyglass%22"
    "&time%3E=now-7days"
    "&time%3C=now%2B7days"
)


def parse_events(df):

    now = datetime.now(
        timezone.utc
    )

    events = []

    for _, row in df.iterrows():

        try:

            ts = pd.to_datetime(
                row["time"],
                utc=True
            )

            events.append({

                "time":
                ts.isoformat(),

                "type":
                row[
                    "tide_time_category"
                ],

                "level":
                float(
                    row[
                        "Water_Level_ODMalin"
                    ]
                )
            })

        except Exception:
            pass

    events.sort(
        key=lambda x:
        x["time"]
    )

    previous = [
        e for e in events
        if pd.to_datetime(
            e["time"]
        ) <= now
    ]

    future = [
        e for e in events
        if pd.to_datetime(
            e["time"]
        ) > now
    ]

    summary = {

        "previous_high":
        None,

        "previous_low":
        None,

        "next_high":
        None,

        "next_low":
        None
    }

    for e in reversed(
        previous
    ):

        t = str(
            e["type"]
        ).lower()

        if (
            summary[
                "previous_high"
            ] is None
            and "high" in t
        ):
            summary[
                "previous_high"
            ] = e

        if (
            summary[
                "previous_low"
            ] is None
            and "low" in t
        ):
            summary[
                "previous_low"
            ] = e

    for e in future:

        t = str(
            e["type"]
        ).lower()

        if (
            summary[
                "next_high"
            ] is None
            and "high" in t
        ):
            summary[
                "next_high"
            ] = e

        if (
            summary[
                "next_low"
            ] is None
            and "low" in t
        ):
            summary[
                "next_low"
            ] = e

    return events, summary


def parse_series(df):

    result = []

    for _, row in df.iterrows():

        try:

            result.append({

                "timestamp":
                pd.to_datetime(
                    row["time"],
                    utc=True
                ).isoformat(),

                "level":
                float(
                    row[
                        "Water_Level_ODM"
                    ]
                )
            })

        except Exception:
            pass

    return result


def fetch_tides():

    try:

        highlow = pd.read_csv(
            HIGHLOW_URL
        )

        series = pd.read_csv(
            SERIES_URL
        )

        events, summary = (
            parse_events(
                highlow
            )
        )

        tide_series = (
            parse_series(
                series
            )
        )

        output = {

            "events":
            events,

            "summary":
            summary,

            "series":
            tide_series
        }

        write_json(
            TIDE_JSON,
            output
        )

        return {
            "ok": True
        }

    except Exception as e:

        write_json(
            TIDE_JSON,
            {
                "events": [],
                "summary": {},
                "series": []
            }
        )

        return {
            "ok": False,
            "error": str(e)
        }


if __name__ == "__main__":

    print(
        fetch_tides()
    )
