# **My Music Revisits:** Finding Tracks Worth Returning To
After switching music streaming services for roughly five months, I exported my listening data and used it to analyze patterns in my music behavior. Then built a small recommendation system that uses those patterns to find tracks worth revisiting.

---
## Project Summary
| Category        | Description                                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Objective**   | Analyze 146 days of my personal listening history to understand what my behavior reveals about my music taste and preferences, then use the patterns to make a recommendation system that helps me find tracks I would likely enjoy again.                                                                                                                                                                                |
| **Methodology** | Built a data pipeline that cleans and combines raw listening and library records into play- and track-level datasets; performed exploratory analysis on repetition, completion, skips, recency, listening context, and retention; engineered behavioral features to score revisit potential; and used TF-IDF, categorical encoding, feature scaling, and cosine-based nearest-neighbor search to identify similar tracks. |
| **Tools**       | Python, pandas, Parquet, scikit-learn, Plotly, and Streamlit.                                                                                                                                                                                                                                                                                                                                                             |
| **Key Result**  | Turned raw listening history into a reproducible analytics and recommendation pipeline that shows tracks worth revisiting, explains the listening signals behind those choices, and lets a user explore my listening patterns and related tracks through a dashboard.                                                                                                                                                     |
| **Status**      | Being Revised                                                                                                                                                                                                                                                                                                                                                                                                             |

## Quick Start
From your terminal:

```bash
git clone https://github.com/sumaitate/my-music-revisits.git
cd my-music-revisits
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/audit_data.py
python scripts/make_data.py
python scripts/make_eda.py
python scripts/make_recommendations.py
python -m streamlit run app/dashboard.py
```

## Results 

## Data
### Data Processing
The pipeline first reads the raw listening and library records, standardizes their fields, and matches listening events with track metadata. It then creates cleaned play-level and track-level datasets that can be reused by the notebook, recommendation system, and dashboard.

The project also defines behavioral signals from the listening history. These include whether a track was repeated, how much of it was played, whether a play ended early, how many different days the track appeared, how recently it appeared, and whether it remained part of the listening history after its first appearance.
### Exploratory Analysis
The exploratory notebook examines the overall listening history before the recommendation layer is built. It looks at listening volume over time, artists, genres, source routes, sessions, track lifecycles, completion, friction, discovery, retention, and track affinity.

The notebook also checks the processed datasets before interpreting them. The current analysis loads 15 analytical tables and records their dimensions, missing values, and duplicate counts. No exact duplicate rows were found in those loaded tables.

### Recommendation System
The recommendation layer uses both behavioral information and track metadata.

Text features are represented with TF-IDF. Categorical information is encoded numerically, while continuous behavioral features are scaled before being combined into the final feature matrix.

A cosine-based nearest-neighbor model then compares the resulting track representations. For a selected track, the model finds other tracks that are close to it in that feature space.

The system saves the candidate tracks and the resulting track-to-track similarity pairs so the dashboard can retrieve recommendations without rebuilding the model every time the application runs.

## Methodology

## Project Structure
The two notebooks were created first to check the data format and run exploratory analysis to find listening patterns. They were later modified as the project developed. The results from the notebooks were used to make decisions about the code in src and scripts. The main code is in src/music_analytics/, while scripts/ contains the starting points for the main stages of the project. The Streamlit component makes the results interactive.

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

## Limitations
The data covers 146 days of one person's listening history from October 18, 2025 through March 13, 2026, which is a small part. The data was taken from a new streaming platform I was trying at the time—most tracks were imported from another music streaming site, which is why this is not reliable for music discovery. The scope of this was very limited. The processed data contains 10,454 listening events across 2,962 tracks, 996 artists, 1,739 albums, and 71 genres, with activity on 143 days. Context is also important and is not present in this data, such as mood, interruption, and intention.

**AI Usage Disclosure:** For full transparency, AI built into the IDE was used for debugging and certain visual elements, like the coloring of the plots. Code from past personal projects was reused and modified.

## Conclusion and Reflection
The purpose of this project was to take a more thorough and analytical look at my own listening behavior and patterns to find which tracks I liked listening to and in what order, whether I listened to a specific genre of music on my commute to class, whether I listened to more ambient sounds around the time I studied, and so on. The recommendation layer came from my friends asking me for music recommendations. My friends also have different music tastes, so it would be interesting to see what they would get from this small system. Roughly 146 days of data doesn't fully capture how diverse my music taste is, especially because I started discovering and listening to new music immediately after the data was exported. I would be interested in revisiting this project with a larger dataset to see whether my listening habits changed and whether more tracks reveal additional patterns.
