"""Compare artist and track rankings under three listening definitions."""
from itertools import combinations
import numpy as np
import pandas as pd
from music_analytics.paths import clean_path, report_path, make_paths


def main():
    make_paths()
    plays = pd.read_parquet(clean_path / "plays.parquet", columns=["artist", "track_key", "display", "minutes", "valid_play"])
    results = []
    top_rows = []
    for entity, key in [("artist", "artist"), ("track", "track_key")]:
        table = plays.groupby(key).agg(events=("valid_play", "size"), valid_plays=("valid_play", "sum"), minutes=("minutes", "sum"))
        tops = {metric: table.sort_values(metric, ascending=False, kind="stable").head(10).index for metric in table.columns}
        for metric, keys in tops.items():
            for rank, item in enumerate(keys, 1):
                label = item if entity == "artist" else plays.loc[plays[key].eq(item), "display"].iloc[0]
                top_rows.append({"entity": entity, "metric": metric, "rank": rank, "key": item, "label": label, "value": table.loc[item, metric]})
        for left, right in combinations(table.columns, 2):
            union = tops[left].union(tops[right])
            a = table.loc[union, left].rank(method="average", ascending=False)
            b = table.loc[union, right].rank(method="average", ascending=False)
            corr = a.corr(b) if a.nunique() > 1 and b.nunique() > 1 else np.nan
            results.append({"entity": entity, "left": left, "right": right, "top10_overlap": len(tops[left].intersection(tops[right])), "union_size": len(union), "spearman": corr})
    comparison = pd.DataFrame(results)
    comparison.to_csv(report_path / "ranking_comparison.csv", index=False)
    pd.DataFrame(top_rows).to_csv(report_path / "ranking_top10.csv", index=False)
    text = "# Ranking comparison\n\nEvents count every retained positive-duration PLAY_END. Valid plays last at least 30 seconds. Minutes include all retained event time.\n\nSpearman correlations use average-tie ranks of the actual scores within the union of each pair of top-10 sets. Top-10 ties use the sorted entity key for reproducibility.\n\n"
    text += comparison.to_string(index=False) + "\n"
    (report_path / "ranking_comparison.md").write_text(text, encoding="utf-8")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
