# Sumi’s Music Universe
This a personal music behavior analytics project built from 6 months of my music streaming data. The project takes listening history and turns it into clean interactive website that shows how I listen, what I replay, what I skip, what genres and artists shape my taste, where my music starts, and which tracks are strong candidates to revisit.

# Currently Being Modified

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
