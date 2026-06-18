/* ==========================================================
   Bangor Water Level Dashboard V5
   format.js

   Formatting, trends, offsets, confidence labels
========================================================== */

const DATUM_STORAGE_KEY = "bangor_datum_offset_v5";

/* ==========================================================
   DATUM OFFSET
========================================================== */

function getDatumOffset() {
    const value = localStorage.getItem(DATUM_STORAGE_KEY);

    if (!value) return 0;

    const parsed = parseFloat(value);

    return Number.isFinite(parsed) ? parsed : 0;
}

function setDatumOffset(value) {

    const parsed = parseFloat(value);

    if (!Number.isFinite(parsed)) {
        return;
    }

    localStorage.setItem(
        DATUM_STORAGE_KEY,
        parsed.toString()
    );
}

function applyDatumOffset(level) {

    const offset = getDatumOffset();

    if (!Number.isFinite(level)) {
        return null;
    }

    return level + offset;
}

/* ==========================================================
   NUMBERS
========================================================== */

function formatLevel(level) {

    if (
        level === null ||
        level === undefined ||
        !Number.isFinite(level)
    ) {
        return "--";
    }

    return applyDatumOffset(level).toFixed(3);
}

function formatRain(mm) {

    if (
        mm === null ||
        mm === undefined ||
        !Number.isFinite(mm)
    ) {
        return "--";
    }

    return `${mm.toFixed(1)} mm`;
}

function formatRate(mmHr) {

    if (
        mmHr === null ||
        mmHr === undefined ||
        !Number.isFinite(mmHr)
    ) {
        return "--";
    }

    return `${mmHr.toFixed(1)} mm/hr`;
}

/* ==========================================================
   DATES
========================================================== */

function formatDateTime(value) {

    if (!value) return "--";

    const date = new Date(value);

    if (isNaN(date.getTime())) {
        return "--";
    }

    return date.toLocaleString(
        "en-IE",
        {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}

function formatDate(value) {

    if (!value) return "--";

    const date = new Date(value);

    if (isNaN(date.getTime())) {
        return "--";
    }

    return date.toLocaleDateString(
        "en-IE",
        {
            year: "numeric",
            month: "short",
            day: "numeric"
        }
    );
}

function formatTime(value) {

    if (!value) return "--";

    const date = new Date(value);

    if (isNaN(date.getTime())) {
        return "--";
    }

    return date.toLocaleTimeString(
        "en-IE",
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}

/* ==========================================================
   RELATIVE AGE
========================================================== */

function ageMinutes(timestamp) {

    if (!timestamp) return null;

    const now = Date.now();

    const then = new Date(timestamp).getTime();

    if (!Number.isFinite(then)) {
        return null;
    }

    return Math.round(
        (now - then) / 60000
    );
}

function formatAge(timestamp) {

    const mins = ageMinutes(timestamp);

    if (mins === null) {
        return "--";
    }

    if (mins < 60) {
        return `${mins} min`;
    }

    const hours = mins / 60;

    if (hours < 24) {
        return `${hours.toFixed(1)} hr`;
    }

    const days = hours / 24;

    return `${days.toFixed(1)} d`;
}

/* ==========================================================
   TREND DETECTION
========================================================== */

function detectTrend(mmHr) {

    if (
        mmHr === null ||
        mmHr === undefined ||
        !Number.isFinite(mmHr)
    ) {
        return {
            label: "Unknown",
            css: ""
        };
    }

    if (mmHr > 2) {
        return {
            label: "▲ Rising",
            css: "trend-rising"
        };
    }

    if (mmHr < -2) {
        return {
            label: "▼ Falling",
            css: "trend-falling"
        };
    }

    return {
        label: "► Stable",
        css: "trend-stable"
    };
}

/* ==========================================================
   SOURCE LABELS
========================================================== */

function sourceLabel(source) {

    switch (source) {

        case "epa_zip":
            return "EPA ZIP";

        case "epa_png":
            return "Chart";

        case "estimated":
            return "Est.";

        case "forecast":
            return "Fcst";

        default:
            return source || "--";
    }
}

function sourceDescription(source) {

    switch (source) {

        case "epa_zip":
            return "Official structured observation";

        case "epa_png":
            return "EPA chart-derived";

        case "estimated":
            return "Estimated current level";

        case "forecast":
            return "Forecast model output";

        default:
            return "Unknown";
    }
}

/* ==========================================================
   CONFIDENCE
========================================================== */

function confidenceLabel(confidence) {

    switch (
        String(confidence || "")
        .toLowerCase()
    ) {

        case "high":
            return "High";

        case "medium":
            return "Medium";

        case "low":
            return "Low";

        default:
            return "--";
    }
}

function confidenceClass(confidence) {

    switch (
        String(confidence || "")
        .toLowerCase()
    ) {

        case "high":
            return "status-ok";

        case "medium":
            return "status-warning";

        case "low":
            return "status-error";

        default:
            return "";
    }
}

/* ==========================================================
   FORECAST LABELS
========================================================== */

function forecastBasisText(basis) {

    if (!basis) return "--";

    return basis
        .replaceAll("_", " ")
        .replace(/\b\w/g, c => c.toUpperCase());
}

/* ==========================================================
   SERIES HELPERS
========================================================== */

function latestPoint(series) {

    if (!Array.isArray(series)) {
        return null;
    }

    if (series.length === 0) {
        return null;
    }

    return series[series.length - 1];
}

function firstPoint(series) {

    if (!Array.isArray(series)) {
        return null;
    }

    if (series.length === 0) {
        return null;
    }

    return series[0];
}

function calculateRateMmHr(series) {

    if (
        !Array.isArray(series) ||
        series.length < 2
    ) {
        return null;
    }

    const end =
        series[series.length - 1];

    const start =
        series[Math.max(
            0,
            series.length - 5
        )];

    const dtHours =
        (
            new Date(end.timestamp)
            -
            new Date(start.timestamp)
        ) / 3600000;

    if (
        !Number.isFinite(dtHours) ||
        dtHours <= 0
    ) {
        return null;
    }

    const diffM =
        end.level_m -
        start.level_m;

    return (
        diffM * 1000
    ) / dtHours;
}

/* ==========================================================
   SAFE GETTERS
========================================================== */

function safeArray(value) {

    return Array.isArray(value)
        ? value
        : [];
}

function safeNumber(value) {

    const n = Number(value);

    return Number.isFinite(n)
        ? n
        : null;
}

/* ==========================================================
   DOM HELPER
========================================================== */

function setText(id, value) {

    const el =
        document.getElementById(id);

    if (!el) return;

    el.textContent =
        value ?? "--";
}
