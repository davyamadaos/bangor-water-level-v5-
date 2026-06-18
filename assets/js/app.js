/* ==========================================================
   Bangor Water Level Dashboard V5
   app.js
========================================================== */

window.dashboardData = null;

const REFRESH_INTERVAL =
    15 * 60 * 1000;

/* ==========================================================
   DATA LOADING
========================================================== */

async function loadDashboardData() {

    try {

        const url =
            `data/latest.json?t=${Date.now()}`;

        const response =
            await fetch(url);

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        window.dashboardData = data;

        renderDashboard(data);

    } catch (error) {

        console.error(error);

        showLoadError(error);
    }
}

function showLoadError(error) {

    const status =
        document.getElementById(
            "dataStatus"
        );

    if (!status) return;

    status.innerHTML = `
        <div class="status-error">
            Failed to load dashboard data.
            ${error.message}
        </div>
    `;
}

/* ==========================================================
   MAIN RENDER
========================================================== */

function renderDashboard(data) {

    renderCurrentStatus(data);

    renderForecastCards(data);

    renderRainfallSummary(data);

    renderWeather(data);

    renderTides(data);

    renderSummaryTable(data);

    renderMetadata(data);

    renderCharts(data);
}

/* ==========================================================
   CURRENT STATUS
========================================================== */

function renderCurrentStatus(data) {

    const current =
        data.current || {};

    setText(
        "currentLevel",
        formatLevel(
            current.level_m
        )
    );

    setText(
        "currentSource",
        sourceLabel(
            current.source
        )
    );

    setText(
        "currentTimestamp",
        formatDateTime(
            current.timestamp
        )
    );

    setText(
        "observationAge",
        formatAge(
            current.timestamp
        )
    );

    setText(
        "currentConfidence",
        confidenceLabel(
            current.confidence
        )
    );

    const river =
        safeArray(
            data.river
        );

    const rate =
        calculateRateMmHr(
            river
        );

    const trend =
        detectTrend(rate);

    const trendEl =
        document.getElementById(
            "trendLabel"
        );

    if (trendEl) {

        trendEl.textContent =
            trend.label;

        trendEl.className =
            trend.css;
    }

    setText(
        "trendRate",
        formatRate(rate)
    );

    const latestZip =
        latestPoint(
            safeArray(
                data.river_zip
            )
        );

    if (latestZip) {

        setText(
            "zipLevel",
            formatLevel(
                latestZip.level_m
            )
        );

        setText(
            "zipTimestamp",
            formatDateTime(
                latestZip.timestamp
            )
        );
    }

    const latestPng =
        latestPoint(
            safeArray(
                data.river_png
            )
        );

    if (latestPng) {

        setText(
            "pngAge",
            formatAge(
                latestPng.timestamp
            )
        );
    }
}

/* ==========================================================
   FORECAST
========================================================== */

function renderForecastCards(data) {

    const container =
        document.getElementById(
            "forecastCards"
        );

    if (!container) return;

    container.innerHTML = "";

    const forecasts =
        safeArray(
            data.forecast
        );

    forecasts.forEach(item => {

        const card =
            document.createElement(
                "div"
            );

        card.className =
            "forecast-card";

        card.innerHTML = `
            <div class="forecast-time">
                ${formatDateTime(
                    item.timestamp
                )}
            </div>

            <div class="forecast-level">
                ${formatLevel(
                    item.level_m
                )} m
            </div>

            <div>
                ${forecastBasisText(
                    item.basis
                )}
            </div>

            <div class="forecast-confidence">
                Confidence:
                ${confidenceLabel(
                    item.confidence
                )}
            </div>
        `;

        container.appendChild(card);
    });
}

/* ==========================================================
   RAINFALL
========================================================== */

function renderRainfallSummary(data) {

    const rain =
        data.rainfall_summary || {};

    setText(
        "rain24",
        formatRain(
            rain.past24h_mm
        )
    );

    setText(
        "rain48",
        formatRain(
            rain.past48h_mm
        )
    );

    setText(
        "rain6f",
        formatRain(
            rain.next6h_mm
        )
    );

    setText(
        "rain12f",
        formatRain(
            rain.next12h_mm
        )
    );

    setText(
        "rain24f",
        formatRain(
            rain.next24h_mm
        )
    );

    setText(
        "rain48f",
        formatRain(
            rain.next48h_mm
        )
    );
}

/* ==========================================================
   WEATHER
========================================================== */

function renderWeather(data) {

    const current =
        document.getElementById(
            "weatherCurrent"
        );

    const forecast =
        document.getElementById(
            "weatherForecast"
        );

    if (
        !current ||
        !forecast
    ) return;

    const weather =
        data.weather || {};

    current.innerHTML = `
        <p>
            <strong>
                ${weather.condition || "--"}
            </strong>
        </p>

        <p>
            Temperature:
            ${weather.temperature_c ?? "--"} °C
        </p>

        <p>
            Wind:
            ${weather.wind_speed_kmh ?? "--"} km/h
            ${weather.wind_direction || ""}
        </p>
    `;

    forecast.innerHTML = "";

    safeArray(
        weather.forecast
    ).slice(0, 7)
    .forEach(day => {

        const div =
            document.createElement(
                "div"
            );

        div.className =
            "weather-day";

        div.innerHTML = `
            <strong>
                ${day.day || ""}
            </strong>

            <div>
                ${day.condition || ""}
            </div>

            <div>
                ${day.temp_min ?? "--"}
                /
                ${day.temp_max ?? "--"} °C
            </div>

            <div>
                Rain:
                ${day.rain_mm ?? 0} mm
            </div>
        `;

        forecast.appendChild(div);
    });
}

/* ==========================================================
   TIDES
========================================================== */

function renderTides(data) {

    const events =
        document.getElementById(
            "tideEvents"
        );

    if (!events) return;

    events.innerHTML = "";

    safeArray(
        data.tide_events
    )
    .slice(0, 4)
    .forEach(event => {

        const div =
            document.createElement(
                "div"
            );

        div.innerHTML = `
            <strong>
                ${event.type}
            </strong>
            —
            ${formatDateTime(
                event.time
            )}
            —
            ${event.level ?? "--"} m
        `;

        events.appendChild(div);
    });
}

/* ==========================================================
   SUMMARY TABLE
========================================================== */

function renderSummaryTable(data) {

    const table =
        document.querySelector(
            "#summaryTable tbody"
        );

    if (!table) return;

    table.innerHTML = "";

    safeArray(
        data.summary_12h
    )
    .forEach(row => {

        const tr =
            document.createElement(
                "tr"
            );

        tr.innerHTML = `
            <td>
                ${formatDate(
                    row.timestamp
                )}
            </td>

            <td>
                ${formatTime(
                    row.timestamp
                )}
            </td>

            <td>
                ${formatLevel(
                    row.level_m
                )}
            </td>

            <td>
                ${sourceLabel(
                    row.source
                )}
            </td>

            <td>
                ${row.rain_3h_mm ?? "--"}
            </td>
        `;

        table.appendChild(tr);
    });
}

/* ==========================================================
   METADATA
========================================================== */

function renderMetadata(data) {

    const el =
        document.getElementById(
            "dataStatus"
        );

    if (!el) return;

    const meta =
        data.metadata || {};

    el.innerHTML = `
        <div>
            Last Update:
            ${formatDateTime(
                meta.last_update
            )}
        </div>

        <div>
            EPA ZIP:
            ${meta.epa_zip_ok ? "✓" : "✗"}
        </div>

        <div>
            EPA PNG:
            ${meta.epa_png_ok ? "✓" : "✗"}
        </div>

        <div>
            Weather:
            ${meta.weather_ok ? "✓" : "✗"}
        </div>

        <div>
            Rainfall:
            ${meta.rainfall_ok ? "✓" : "✗"}
        </div>

        <div>
            Tide:
            ${meta.tide_ok ? "✓" : "✗"}
        </div>
    `;
}

/* ==========================================================
   CHARTS
========================================================== */

function renderCharts(data) {

    renderRiverChart({

        river_zip:
            safeArray(
                data.river_zip
            ),

        river_png:
            safeArray(
                data.river_png
            ),

        forecast:
            safeArray(
                data.forecast
            ),

        rainfall:
            safeArray(
                data.rainfall_series
            )
    });

    renderTideChart(
        safeArray(
            data.tide_series
        )
    );
}

/* ==========================================================
   DARK MODE
========================================================== */

function initialiseDarkMode() {

    const btn =
        document.getElementById(
            "darkModeBtn"
        );

    const stored =
        localStorage.getItem(
            "dark_mode"
        );

    if (
        stored === "true"
    ) {
        document.body.classList.add(
            "dark"
        );
    }

    if (!btn) return;

    btn.addEventListener(
        "click",
        () => {

            document.body.classList.toggle(
                "dark"
            );

            localStorage.setItem(
                "dark_mode",
                document.body.classList.contains(
                    "dark"
                )
            );
        }
    );
}

/* ==========================================================
   DATUM OFFSET
========================================================== */

function initialiseDatumOffset() {

    const input =
        document.getElementById(
            "datumOffset"
        );

    const save =
        document.getElementById(
            "saveOffsetBtn"
        );

    if (
        !input ||
        !save
    ) {
        return;
    }

    input.value =
        getDatumOffset();

    save.addEventListener(
        "click",
        () => {

            setDatumOffset(
                input.value
            );

            loadDashboardData();
        }
    );
}

/* ==========================================================
   REFRESH
========================================================== */

function initialiseRefresh() {

    const btn =
        document.getElementById(
            "refreshBtn"
        );

    if (btn) {

        btn.addEventListener(
            "click",
            loadDashboardData
        );
    }

    setInterval(
        loadDashboardData,
        REFRESH_INTERVAL
    );
}

/* ==========================================================
   STARTUP
========================================================== */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initialiseDarkMode();

        initialiseDatumOffset();

        initialiseRefresh();

        initialiseRangeButtons();

        loadDashboardData();
    }
);
