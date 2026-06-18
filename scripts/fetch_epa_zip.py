import io
import zipfile
import requests
import pandas as pd

from dateutil import parser

from config import (
    EPA_ZIP_URL,
    RIVER_ZIP_JSON
)

from utils import write_json


def fetch_epa_zip():

    try:

        response = requests.get(
            EPA_ZIP_URL,
            timeout=60
        )

        response.raise_for_status()

        z = zipfile.ZipFile(
            io.BytesIO(response.content)
        )

        csv_files = [
            n for n in z.namelist()
            if n.lower().endswith(".csv")
        ]

        if not csv_files:
            raise RuntimeError(
                "No CSV found in ZIP"
            )

        csv_name = csv_files[0]

        with z.open(csv_name) as f:
            df = pd.read_csv(f)

        cols = [
            c.lower()
            for c in df.columns
        ]

        timestamp_col = None
        value_col = None

        for c in df.columns:

            lc = c.lower()

            if (
                "date" in lc
                or "time" in lc
            ):
                timestamp_col = c

            if (
                "level" in lc
                or "value" in lc
            ):
                value_col = c

        if (
            timestamp_col is None
            or value_col is None
        ):
            raise RuntimeError(
                "Could not identify columns"
            )

        records = []

        for _, row in df.iterrows():

            try:

                ts = parser.parse(
                    str(
                        row[
                            timestamp_col
                        ]
                    )
                )

                level = float(
                    row[value_col]
                )

                records.append(
                    {
                        "timestamp":
                        ts.isoformat(),

                        "level_m":
                        round(
                            level,
                            3
                        ),

                        "source":
                        "epa_zip",

                        "quality":
                        "official",

                        "confidence":
                        "high"
                    }
                )

            except Exception:
                pass

        records.sort(
            key=lambda r:
            r["timestamp"]
        )

        write_json(
            RIVER_ZIP_JSON,
            records
        )

        return {
            "ok": True,
            "count":
            len(records)
        }

    except Exception as e:

        write_json(
            RIVER_ZIP_JSON,
            []
        )

        return {
            "ok": False,
            "error": str(e)
        }


if __name__ == "__main__":

    print(
        fetch_epa_zip()
    )
