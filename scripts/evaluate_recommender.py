import pandas as pd
from music_analytics.paths import clean_path, make_paths
from music_analytics.evaluate import evaluate


def main():
    make_paths()
    settings = evaluate(pd.read_parquet(clean_path / "plays.parquet"))
    print("Evaluation saved to reports/evaluation.md and evaluation.csv")
    print("Selected evaluation blend:", settings["score_weights"])


if __name__ == "__main__":
    main()
