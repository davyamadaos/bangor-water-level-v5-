import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

import cv2
import numpy as np
import pytesseract
import requests

from PIL import Image

from config import (
    EPA_PNG_URL,
    DEBUG_DIR,
    RIVER_PNG_JSON
)

from utils import (
    write_json,
    now_iso
)

PNG_FILE = DEBUG_DIR / "epa_chart_latest.png"

DEBUG_JSON = (
    DEBUG_DIR /
    "epa_chart_extraction.json"
)


# ==========================================================
# DOWNLOAD
# ==========================================================

def download_png():

    response = requests.get(
        EPA_PNG_URL,
        timeout=60
    )

    response.raise_for_status()

    PNG_FILE.write_bytes(
        response.content
    )

    return PNG_FILE


# ==========================================================
# IMAGE LOAD
# ==========================================================

def load_image():

    return cv2.imread(
        str(PNG_FILE)
    )


# ==========================================================
# PLOT DETECTION
# ==========================================================

def detect_plot_area(image):

    h, w = image.shape[:2]

    # Conservative fallback
    fallback = {

        "left": int(w * 0.09),
        "right": int(w * 0.95),

        "top": int(h * 0.12),
        "bottom": int(h * 0.88),

        "method":
        "fallback"
    }

    try:

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        edges = cv2.Canny(
            gray,
            50,
            150
        )

        lines = cv2.HoughLinesP(
            edges,
            1,
            np.pi / 180,
            threshold=100,
            minLineLength=200,
            maxLineGap=20
        )

        if lines is None:
            return fallback

        xs = []
        ys = []

        for l in lines:

            x1, y1, x2, y2 = l[0]

            xs.extend([x1, x2])
            ys.extend([y1, y2])

        if len(xs) < 10:
            return fallback

        return {

            "left":
            max(
                min(xs),
                fallback["left"]
            ),

            "right":
            min(
                max(xs),
                fallback["right"]
            ),

            "top":
            max(
                min(ys),
                fallback["top"]
            ),

            "bottom":
            min(
                max(ys),
                fallback["bottom"]
            ),

            "method":
            "detected"
        }

    except Exception:

        return fallback


# ==========================================================
# OCR
# ==========================================================

def run_ocr():

    try:

        image = Image.open(
            PNG_FILE
        )

        text = pytesseract.image_to_string(
            image
        )

        return text

    except Exception:

        return ""


# ==========================================================
# TRACE EXTRACTION
# ==========================================================

def extract_trace(image, plot):

    left = plot["left"]
    right = plot["right"]

    top = plot["top"]
    bottom = plot["bottom"]

    crop = image[
        top:bottom,
        left:right
    ]

    hsv = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2HSV
    )

    # Generic darker trace threshold

    mask = cv2.inRange(
        hsv,
        (0, 0, 0),
        (180, 255, 140)
    )

    h, w = mask.shape

    points = []

    for x in range(w):

        ys = np.where(
            mask[:, x] > 0
        )[0]

        if len(ys) == 0:
            continue

        y = int(
            np.median(ys)
        )

        points.append(
            (x, y)
        )

    return points, h, w


# ==========================================================
# PIXEL → TIME
# ==========================================================

def pixel_to_timestamp(
    x,
    width
):

    now = datetime.now(
        timezone.utc
    )

    start = (
        now -
        timedelta(days=90)
    )

    fraction = x / width

    dt = (
        start +
        (
            now - start
        ) * fraction
    )

    return dt.isoformat()


# ==========================================================
# PIXEL → LEVEL
# ==========================================================

def pixel_to_level(
    y,
    height
):

    # Conservative default
    # Manual calibration can improve

    max_level = 105.0
    min_level = 95.0

    frac = (
        1 -
        (y / height)
    )

    return round(
        min_level +
        (
            max_level -
            min_level
        ) * frac,
        3
    )


# ==========================================================
# RESAMPLE
# ==========================================================

def build_series(
    points,
    height,
    width
):

    series = []

    for x, y in points:

        series.append(
            {
                "timestamp":
                pixel_to_timestamp(
                    x,
                    width
                ),

                "level_m":
                pixel_to_level(
                    y,
                    height
                ),

                "source":
                "epa_png",

                "quality":
                "chart_derived",

                "confidence":
                "medium"
            }
        )

    return series


# ==========================================================
# CONFIDENCE
# ==========================================================

def confidence_score(
    point_count
):

    if point_count > 1000:
        return "high"

    if point_count > 300:
        return "medium"

    return "low"


# ==========================================================
# MAIN
# ==========================================================

def main():

    diagnostics = {

        "generated":
        now_iso()
    }

    try:

        download_png()

        image = load_image()

        plot = detect_plot_area(
            image
        )

        ocr_text = run_ocr()

        points, h, w = (
            extract_trace(
                image,
                plot
            )
        )

        confidence = (
            confidence_score(
                len(points)
            )
        )

        series = build_series(
            points,
            h,
            w
        )

        for row in series:
            row[
                "confidence"
            ] = confidence

        diagnostics[
            "plot"
        ] = plot

        diagnostics[
            "ocr_preview"
        ] = ocr_text[:500]

        diagnostics[
            "point_count"
        ] = len(points)

        diagnostics[
            "confidence"
        ] = confidence

        diagnostics[
            "success"
        ] = True

        write_json(
            RIVER_PNG_JSON,
            series
        )

        write_json(
            DEBUG_JSON,
            diagnostics
        )

        return diagnostics

    except Exception as e:

        diagnostics[
            "success"
        ] = False

        diagnostics[
            "error"
        ] = str(e)

        write_json(
            DEBUG_JSON,
            diagnostics
        )

        write_json(
            RIVER_PNG_JSON,
            []
        )

        return diagnostics


if __name__ == "__main__":

    result = main()

    print(
        json.dumps(
            result,
            indent=2
        )
    )
