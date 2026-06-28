# FunnelFlux Analytics


A high-performance, interactive user journey funnel optimization and business intelligence engine built in Python. This platform processes multi-step customer progression data frames to identify conversion drop-offs, isolate frictional drop-out vectors, and calculate customer acquisition pathways.

---

## Live Deployment
The application is live and securely hosted in production via Streamlit Community Cloud. 

**[Launch the Live FunnelFlux Dashboard](https://funnelflux-analytics-dygo6lxycsarqvucbdqcce.streamlit.app/)**

---

## System Architecture & Layout
The project follows a clean, production-grade directory setup, separating client-side presentation code from modular analytics computations:

```text
funnelflux-analytics/
├── src/
│   └── __init__.py          # Bundles core sub-modules
├── app.py                   # Main routing interface and layout view
├── requirements.txt         # Managed cloud dependencies package list
└── README.md                # Project documentation
