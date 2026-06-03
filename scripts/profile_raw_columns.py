from pathlib import Path
import json
import zipfile
from typing import Any

import pandas as pd


PROJECT_ROOT = Path.cwd()

CSV_DIR = PROJECT_ROOT / "data" / "raw" / "csv"
JSON_ZIP_DIR = PROJECT_ROOT / "data" / "raw" / "json_zips"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"

COLUMN_PROFILE_PATH = METADATA_DIR / "raw_column_profile.csv"
FILE_PREVIEW_DIR = METADATA_DIR / "file_previews"


def read_csv_file(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def read_json_zip_file(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path, "r") as zip_file:
        member_name = zip_file.namelist()[0]

        with zip_file.open(member_name) as file:
            data = json.load(file)

    if isinstance(data, list):
        return pd.json_normalize(data, sep=".")

    if isinstance(data, dict):
        return pd.json_normalize([data], sep=".")

    return pd.DataFrame({"value": [data]})


def make_hashable_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    return value


def make_hashable_series(series: pd.Series) -> pd.Series:
    return series.map(make_hashable_value)


def clean_sample_values(series: pd.Series, sample_size: int = 5) -> str:
    values = (
        make_hashable_series(series)
        .dropna()
        .astype(str)
        .drop_duplicates()
        .head(sample_size)
        .tolist()
    )

    return " | ".join(values)


def profile_dataframe(file_name: str, file_type: str, dataframe: pd.DataFrame) -> list[dict]:
    records = []
    row_count = len(dataframe)

    for column in dataframe.columns:
        series = dataframe[column]
        hashable_series = make_hashable_series(series)

        non_null_count = int(series.notna().sum())
        missing_count = int(series.isna().sum())
        unique_count = int(hashable_series.nunique(dropna=True))

        records.append(
            {
                "file_name": file_name,
                "file_type": file_type,
                "column_name": column,
                "dtype": str(series.dtype),
                "row_count": row_count,
                "non_null_count": non_null_count,
                "missing_count": missing_count,
                "missing_rate": round(missing_count / row_count, 4) if row_count else 0,
                "unique_count": unique_count,
                "sample_values": clean_sample_values(series),
            }
        )

    return records


def save_preview(file_name: str, dataframe: pd.DataFrame) -> None:
    safe_name = file_name.replace(".json.zip", "").replace(".csv", "")
    preview_path = FILE_PREVIEW_DIR / f"{safe_name}_preview.csv"

    preview = dataframe.head(25).copy()

    for column in preview.columns:
        preview[column] = preview[column].map(make_hashable_value)

    preview.to_csv(preview_path, index=False)


def build_column_profile() -> pd.DataFrame:
    records = []

    for path in sorted(CSV_DIR.glob("*.csv")):
        dataframe = read_csv_file(path)
        save_preview(path.name, dataframe)
        records.extend(profile_dataframe(path.name, "csv", dataframe))

    for path in sorted(JSON_ZIP_DIR.glob("*.json.zip")):
        dataframe = read_json_zip_file(path)
        save_preview(path.name, dataframe)
        records.extend(profile_dataframe(path.name, "json_zip", dataframe))

    return pd.DataFrame(records)


def main() -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    FILE_PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    column_profile = build_column_profile()
    column_profile.to_csv(COLUMN_PROFILE_PATH, index=False)

    print(column_profile[["file_name", "column_name", "dtype", "missing_rate", "unique_count"]].to_string(index=False))
    print()
    print(f"Saved column profile to: {COLUMN_PROFILE_PATH}")
    print(f"Saved file previews to: {FILE_PREVIEW_DIR}")


if __name__ == "__main__":
    main()
