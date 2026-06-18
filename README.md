# Bangor Water Level Dashboard V5

Mobile-first river monitoring dashboard for:

- Bangor EPA Station 33008
- Rainfall forecasting
- Tide context
- Hybrid river forecasting

Hosted entirely on GitHub Pages.

## Features

- EPA ZIP observations
- EPA PNG chart extraction
- OCR and computer vision
- Rainfall forecasts
- Weather forecasts
- Tide forecasts
- Hybrid river forecast
- Dark mode
- Manual datum offset
- GitHub Actions updates every 15 minutes

## Data Sources

EPA Hydronet:
https://epawebapp.epa.ie/hydronet/#33008

Met Éireann:
https://openaccess.pf.api.met.ie

Marine Institute:
https://erddap.marine.ie

## Deployment

1. Create GitHub repository
2. Upload files
3. Enable GitHub Pages
4. Enable GitHub Actions
5. Run workflow manually
6. Review:

data/debug/epa_chart_extraction.json

7. Open Pages URL

## Notes

PNG-derived values are estimates generated from computer vision and are not official EPA observations.
