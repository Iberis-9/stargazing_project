# ✨ Stargazing Dashboard (Sweden) ✨ 

An interactive Streamlit dashboard designed to assess **night-sky observing conditions across Sweden**, combining real-time weather data, moonlight conditions, and near-Earth object information to support stargazing decisions.
Rather than presenting raw metrics in isolation, the aim is to provide a clear, interpretable overview of observing conditions for a given night.

The dashboard includes a small amount of astronomical context — such as NASA’s Astronomy Picture of the Day and near-Earth object activity — but its primary focus is practical decision-making rather than scientific precision.

## ✦ Stargazing score 

At the core of the app is a stargazing score, designed as a heuristic summary of overall observing conditions. Cloud cover, visibility, humidity, and moon illumination are each scaled and blended into a 0–100 score.

The score is not intended to be an objective measure of sky quality. Instead, it highlights relative changes over time, making it easier to identify windows during the night when conditions are more favourable for observation.

## ✦ Possible extensions 

This project could be extended in several directions. Location handling could be made more flexible by allowing custom coordinates or map-based selection, rather than relying on predefined locations within Sweden.

Given the geographic focus, an obvious addition would be aurora (northern lights) forecasts. Another would be mapping celestial objects that are actually visible from the selected location and time, rather than showing only distance-based context.


## ✦ Data & implementation 

The app is built in Python using Streamlit, with pandas handling data transformation and Altair used for visualisation. Minor CSS and HTML adjustments are used to improve layout and visual hierarchy within Streamlit.

Data is sourced from NASA’s APOD and NEO APIs, as well as a weather API providing local forecasts and visibility metrics.

###  Data sources 

- NASA APOD API - Astronomy Picture of the Day
- NASA NEO API - Near Earth Objects
- Weather API - Local weather and sky conditions

## ✦ Teck stack 

| Tools | Purpose |
|-----------|---------|
| Python | Application logic and data processing |
| Streamlit | Interactive dashboard framework |
| pandas | Data manipulation |
| Altair | Data visualisation |
| CSS / HTML | Minor layout and visual refinements |

## 🚀 Live app

The dashboard is deployed on Streamlit Cloud and can be explored here:  
👉 https://iberis-9-streamlit-nod-the-dashboardapp-bcuxpv.streamlit.app/

## ✦ Running locally 

🗝️ API keys for NASA and the weather service are required to run the app locally and are expected in .streamlit/secrets.toml.

```bash
git clone https://github.com/your-username/stargazing-streamlit-dashboard.git
cd stargazing-streamlit-dashboard/the_dashboard
streamlit run app.py


