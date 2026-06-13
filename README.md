# Sumi’s Music Universe
This a personal music behavior analytics project built from 6 months of my music streaming data. The project takes listening history and turns it into clean interactive website that shows how I listen, what I replay, what I skip, what genres and artists shape my taste, where my music starts, and which tracks are strong candidates to revisit.

## Overview
The dashboard is organized around human music behavior questions: who I am as a listener, when I listen, what I listen to, what I discover, what I skip, where my listening starts, and what should come back.

## Results
The pipeline processes 10,454 play events, 2,962 tracks, 996 artists, 1,853 albums, 71 genres, 448 listening sessions, and 10 source contexts.

The project identifies repeat behavior, skip/friction patterns, discovery retention, playlist dependence, listening sessions, genre concentration, artist pull, source routes, and recommendation-ready tracks.

## Skills Demonstrated
This project demonstrates end-to-end data cleaning, feature engineering, exploratory analysis, dashboard design, behavioral analytics, product thinking, and interactive data visualization.

The main tools used are Python, pandas, NumPy, PyArrow, Streamlit, Plotly, and scikit-learn-ready feature design.

## Repository Structure

```text
music-analytics/
├── app/
│   └── dashboard.py
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── reports/
│   ├── eda.md
│   └── figures/
├── scripts/
│   ├── audit_data.py
│   ├── make_data.py
│   └── make_eda.py
├── src/
│   └── music_analytics/
│       ├── build.py
│       ├── paths.py
│       └── read.py
├── requirements.txt
└── README.md
```

## How to Run

```bash
cd ~/Documents/Coding/music-analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/audit_data.py
python3 scripts/make_data.py
python3 scripts/make_eda.py
streamlit run app/dashboard.py
```
