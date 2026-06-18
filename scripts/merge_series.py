from utils import (
    read_json,
    write_json
)

from config import (
    RIVER_JSON,
    RIVER_ZIP_JSON,
    RIVER_PNG_JSON
)


def merge_series():

    zip_data = read_json(
        RIVER_ZIP_JSON,
        []
    )

    png_data = read_json(
        RIVER_PNG_JSON,
        []
    )

    merged = list(zip_data)

    latest_zip = None

    if zip_data:
        latest_zip = (
            zip_data[-1]
            ["timestamp"]
        )

    for row in png_data:

        if (
            latest_zip is None
            or row["timestamp"]
            > latest_zip
        ):
            merged.append(row)

    merged.sort(
        key=lambda r:
        r["timestamp"]
    )

    write_json(
        RIVER_JSON,
        merged
    )

    return merged


if __name__ == "__main__":

    merge_series()
