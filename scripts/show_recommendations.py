from music_analytics.paths import make_paths
import sys


from music_analytics.recommend import find_track, recommend_for


def main() -> None:
    make_paths()
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/show_recommendations.py "track, artist, album, or genre"')
        return

    query = " ".join(sys.argv[1:])
    matches = find_track(query, limit=8)

    if matches.empty:
        print("No matching tracks found.")
        return

    print()
    print("Matching tracks")
    print()

    for place, row in enumerate(matches.itertuples(index=False), start=1):
        print(f"{place}. {row.display} — {row.artist}")
        print(f"   Genre: {row.genre}")
        print(f"   Role: {row.recommend_role}")
        print(f"   Score: {row.recommend_score:.3f}")
        print()

    seed = matches.iloc[0]

    print("Seed track")
    print(f"{seed['display']} — {seed['artist']}")
    print(f"Role: {seed['recommend_role']}")
    print(f"Score: {seed['recommend_score']:.3f}")
    print()

    results = recommend_for(seed["track_key"], limit=10)

    if results.empty:
        print("No recommendations found for this track.")
        return

    print("Recommendations")
    print()

    for place, row in enumerate(results.itertuples(index=False), start=1):
        print(f"{place}. {row.candidate_display} — {row.candidate_artist}")
        print(f"   Similarity: {row.similarity:.3f}")
        print(f"   Role: {row.recommend_role}")
        print(f"   Skip Rate: {row.friction_rate:.1%}")
        print(f"   Reason: {row.recommend_reason}")
        print()


if __name__ == "__main__":
    main()
