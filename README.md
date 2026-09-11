# **My Music Revisits:** Finding Tracks Worth Returning To

After switching music streaming services for roughly five months, I exported my listening data and used it to analyze patterns in my music behavior. Then built a small recommendation system that uses those patterns to find tracks worth revisiting.
## Project Summary
| Category        | Description                                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Objective**   | Analyze 146 days of my personal listening history to understand what my behavior reveals about my music taste and preferences, then use the patterns to make a recommendation system that helps me find tracks I would likely enjoy again.                                                                                                                                                                                |
| **Methodology** | Built a data pipeline that cleans and combines raw listening and library records into play- and track-level datasets; performed exploratory analysis on repetition, completion, skips, recency, listening context, and retention; engineered behavioral features to score revisit potential; and used TF-IDF, categorical encoding, feature scaling, and cosine-based nearest-neighbor search to identify similar tracks. |
| **Tools**       | Python, pandas, Parquet, scikit-learn, Plotly, and Streamlit.                                                                                                                                                                                                                                                                                                                                                             |
| **Key Result**  | Turned raw listening history into a reproducible analytics and recommendation pipeline that shows tracks worth revisiting, explains the listening signals behind those choices, and lets a user explore my listening patterns and related tracks through a dashboard.                                                                                                                                                     |
| **Status**      | Being Revised                                                                                                                                                                                                                                                                                                                                                                                                             |


## Run in 3 mins

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
