from music_analytics.paths import make_paths
from music_analytics.recommend import build


def main() -> None:
    make_paths()
    settings = build(top=15)

    print("Recommendation layer saved.")
    print(f"Tracks: {settings['tracks']:,}")
    print(f"Matrix: {settings['matrix_rows']:,} rows x {settings['matrix_cols']:,} columns")
    print(f"Candidates: {settings['candidate_rows']:,}")
    print(f"Recommendation pairs: {settings['pair_rows']:,}")
    print("Saved data/processed/recommend_candidates.parquet")
    print("Saved data/processed/recommendations.parquet")
    print("Saved data/processed/recommend_profile.parquet")
    print("Saved models/recommend_settings.json")


if __name__ == "__main__":
    main()