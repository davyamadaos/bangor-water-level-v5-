import json
from pathlib import Path
from datetime import datetime, timezone


def now_iso():
    return (
        datetime.now(timezone.utc)
        .isoformat()
    )


def write_json(path, data):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


def read_json(path, default=None):

    path = Path(path)

    if not path.exists():
        return default

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:
        return default
