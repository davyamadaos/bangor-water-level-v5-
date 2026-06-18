/* ==========================================================
   Bangor Water Level Dashboard V5
   charts.js
========================================================== */

let riverChart = null;
let tideChart = null;

let currentRange = "24h";

/* ==========================================================
   RANGE FILTERING
========================================================== */

function rangeToMilliseconds(range) {

    switch (range) {

        case "6h":
            return 6 * 3600 * 1000;

        case "12h":
            return 12 * 3600 * 1000;

        case "24h":
            return 24 * 3600 * 1000;

        case "48h":
            return 48 * 3600 * 1000;

        case "7d":
            return 7 * 24 * 3600 * 1000;

        case "30d":
            return 30 * 24 * 3600 * 1000;

        case "3m":
            return 90 * 24 * 3600 * 1000;

        default:
            return 24 * 3600 * 1000;
    }
}

function filterSeriesByRange(series, range) {

    if (!Array.isArray(series)) {
        return [];
    }

    const duration =
        rangeToMilliseconds(range);

    const latest =
        series.length
            ? new Date(
                  series[
                      series.length - 1
                  ].timestamp
              ).getTime()
            : Date.now();

    const start =
        latest - duration;

    return series.filter(item => {

        const t =
            new Date(
                item.timestamp
            ).getTime();

        return t >= start;
    });
}

/* ==========================================================
   BUILD DATASETS
========================================================== */

function buildObservedDataset(series) {

    return {
        label: "EPA ZIP",
        data: series.map(r => ({
            x: r.timestamp,
            y: applyDatumOffset(
                r.level_m
            )
        })),
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.2
    };
}

function buildPngDataset(series) {

    return {
        label: "Chart Derived",
        data: series.map(r => ({
            x: r.timestamp,
            y: applyDatumOffset(
                r.level_m
            )
        })),
        borderWidth: 2,
        pointRadius: 3,
        tension: 0.2
    };
}

function buildForecastDataset(series) {

    return {
        label: "Forecast",
        data: series.map(r => ({
            x: r.timestamp,
            y: applyDatumOffset(
                r.level_m
            )
        })),
        borderDash: [6, 6],
        borderWidth: 2,
        pointRadius: 4,
        tension: 0.2
    };
}

function buildRainfallDataset(series) {

    return {
        label: "Rainfall",
        type: "bar",
        yAxisID: "rain",
        data: series.map(r => ({
            x: r.timestamp,
            y: r.rain_mm
        }))
    };
}

/* ==========================================================
   LABEL HELPERS
========================================================== */

function createPointLabels(chart) {

    if (!chart) return;

    const ctx = chart.ctx;

    chart.data.datasets.forEach(
        dataset => {

            if (
                !dataset.data ||
                !dataset.data.length
            ) {
                return;
            }

            const meta =
                chart.getDatasetMeta(
                    chart.data.datasets.indexOf(
                        dataset
                    )
                );

            if (
                !meta ||
                !meta.data ||
                !meta.data.length
            ) {
                return;
            }

            const lastIndex =
                meta.data.length - 1;

            const point =
                meta.data[lastIndex];

            if (!point) return;

            const value =
                dataset.data[lastIndex].y;

            ctx.save();

            ctx.font =
                "12px sans-serif";

            ctx.fillStyle =
                getComputedStyle(
                    document.body
                ).getPropertyValue(
                    "--text"
                );

            ctx.fillText(
                Number(value).toFixed(3),
                point.x + 8,
                point.y - 8
            );

            ctx.restore();
        }
    );
}

/* ==========================================================
   RIVER CHART
========================================================== */

function renderRiverChart(data) {

    const canvas =
        document.getElementById(
            "riverChart"
        );

    if (!canvas) return;

    const zipSeries =
        filterSeriesByRange(
            safeArray(
                data.river_zip
            ),
            currentRange
        );

    const pngSeries =
        filterSeriesByRange(
            safeArray(
                data.river_png
            ),
            currentRange
        );

    const forecastSeries =
        filterSeriesByRange(
            safeArray(
                data.forecast
            ),
            currentRange
        );

    const rainfallSeries =
        filterSeriesByRange(
            safeArray(
                data.rainfall
            ),
            currentRange
        );

    if (riverChart) {
        riverChart.destroy();
    }

    riverChart =
        new Chart(
            canvas,
            {
                type: "line",

                data: {
                    datasets: [

                        buildObservedDataset(
                            zipSeries
                        ),

                        buildPngDataset(
                            pngSeries
                        ),

                        buildForecastDataset(
                            forecastSeries
                        ),

                        buildRainfallDataset(
                            rainfallSeries
                        )
                    ]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    interaction: {
                        mode: "nearest",
                        intersect: false
                    },

                    plugins: {

                        legend: {
                            display: true
                        },

                        tooltip: {

                            callbacks: {

                                label:
                                    function(
                                        ctx
                                    ) {

                                        return `${ctx.dataset.label}: ${ctx.parsed.y}`;
                                    }
                            }
                        }
                    },

                    scales: {

                        x: {

                            type: "time",

                            time: {

                                unit:
                                    currentRange ===
                                        "6h" ||
                                    currentRange ===
                                        "12h" ||
                                    currentRange ===
                                        "24h"
                                        ? "hour"
                                        : "day"
                            }
                        },

                        y: {

                            title: {
                                display: true,
                                text: "River Level (m)"
                            }
                        },

                        rain: {

                            position: "right",

                            beginAtZero: true,

                            grid: {
                                drawOnChartArea: false
                            },

                            title: {
                                display: true,
                                text: "Rain (mm)"
                            }
                        }
                    },

                    animation: {

                        onComplete() {

                            createPointLabels(
                                riverChart
                            );
                        }
                    }
                }
            }
        );
}

/* ==========================================================
   TIDE CHART
========================================================== */

function renderTideChart(series) {

    const canvas =
        document.getElementById(
            "tideChart"
        );

    if (!canvas) return;

    if (tideChart) {
        tideChart.destroy();
    }

    tideChart =
        new Chart(
            canvas,
            {
                type: "line",

                data: {

                    datasets: [
                        {
                            label:
                                "Ballyglass Tide",

                            data:
                                safeArray(
                                    series
                                ).map(
                                    item => ({
                                        x:
                                            item.timestamp ||
                                            item.time,
                                        y:
                                            item.level ??
                                            item.water_level
                                    })
                                ),

                            borderWidth: 2,
                            pointRadius: 0,
                            tension: 0.25
                        }
                    ]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            display: true
                        }
                    },

                    scales: {

                        x: {
                            type: "time"
                        },

                        y: {

                            title: {
                                display: true,
                                text: "Tide (m)"
                            }
                        }
                    }
                }
            }
        );
}

/* ==========================================================
   RANGE BUTTONS
========================================================== */

function initialiseRangeButtons() {

    document
        .querySelectorAll(
            ".range-btn"
        )
        .forEach(btn => {

            btn.addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll(
                            ".range-btn"
                        )
                        .forEach(
                            b =>
                                b.classList.remove(
                                    "active"
                                )
                        );

                    btn.classList.add(
                        "active"
                    );

                    currentRange =
                        btn.dataset.range;

                    if (
                        window.dashboardData
                    ) {

                        renderRiverChart(
                            window.dashboardData
                        );
                    }
                }
            );
        });
}
