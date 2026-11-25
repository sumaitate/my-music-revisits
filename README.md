# My Music Revisits

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?logo=scipy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-663399?logo=css&logoColor=white)

## About 

I spent about around 5 months experimenting with Apple Music after importing much of my existing music library. When I got my data, I thought about what I actually wanted to learn about myself. I already knew who my favorite artists were, but I knew there were very specific songs I listened to in very specific patterns, and I wanted to explore that.

This project became a little **time capsule of my music taste**. Out of everything I've worked on, this is the project I find myself returning to the most. Whenever I don't know what to listen to, I open the dashboard and find something I had completely forgotten about.

## Data

My personal Apple Music export from approximately October 2025 to March 2026.

| Data | Raw records |
|---|---:|
| Playback activity | 22,872 |
| Daily listening history | 5,042 |
| Library tracks | 10,738 |
| Track import records | 9,547 |
| Library playlists | 144 |

Much of my music was imported from Spotify, YouTube, Soundcloud, and other platforms, making it difficult to find genuine discoveries from songs I already knew. Five months is also a fairly small window for meaningful recommendation modeling, especially considering how many years I've spent building my music taste. 

## Dashboard & Recommendations

The dashboard explores genre preferences, artist rankings, repeat listening behavior, daily activity and weekly listening patterns.

Building the recommendation system was probably the hardest part. I wanted to work with what little data I had without artificially inflating the importance of certain songs. I used statistical smoothing, behavioral scoring, TF-IDF and cosine similarity to recommend tracks from my existing listening history.

Historical replay experiments compare ranking methods using Recall@K and NDCG@K. The interactive interface was built with Streamlit and Plotly.

## Design

I was extremely particular about how I wanted this project to feel. I took inspiration from retro iPods, 8-bit games, and old-school video game posters, combining a clean interface with the kind of graphic design I've always enjoyed.

One of the most fun parts was letting my friends play around with the dashboard and find recommendations through my music taste.

## Reflections

As much as I love applied mathematics and research, this project made me realize how much I enjoy creating products. It was a fun way to apply statistics and machine learning to something I genuinely care about.

## AI Transparency Notice

I used ChatGPT (OpenAI) and Claude (Anthropic) as development assistants, primarily for frontend implementation, debugging, and refining the dashboard's visual design.
