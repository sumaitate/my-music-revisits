from pathlib import Path
import json
import zipfile
from typing import Any

import pandas as pd


PROJECT_ROOT = Path.cwd()

JSON_ZIP_DIR = PROJECT_ROOT / "data" / "raw" / "json_zips"
INTERIM_JSON_DIR = PROJECT_ROOT / "data" / "interim" / "json"
INTERIM_CSV_DIR = PROJECT_ROOT / "data" / "interim" / "csv"
PROCESSED_PARQUET_DIR = PROJECT_ROOT / "data" / "processed" / "parquet"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"

CONVERSION_REPORT_PATH = METADATA_DIR / "json_conversion_report.csv"


def read_json_zip(path: Path) -> tuple[str, Any]:
    with zipfile.ZipFile(path, "r") as zip_file:
        member_names = zip_file.namelist()

        if not member_names:
            raise ValueError(f"No files found inside {path.name}")

        member_name = member_names[0]

        with zip_file.open(member_name) as file:
            data = json.load(file)

    return member_name, data


def write_extracted_json(output_path: Path, data: Any) -> None:
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def normalize_json_data(data: Any) -> pd.DataFrame:
    if isinstance(data, list):
        return pd.json_normalize(data, sep=".")

    if isinstance(data, dict):
        return pd.json_normalize([data], sep=".")

    return pd.DataFrame({"value": [data]})


def stringify_nested_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    return value


def stringify_nested_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    converted = dataframe.copy()

    for column in converted.columns:
        converted[column] = converted[column].map(stringify_nested_value)

    return converted


def convert_json_zip(path: Path) -> dict:
    stem = path.name.replace(".json.zip", "")
    member_name, data = read_json_zip(path)

    extracted_json_path = INTERIM_JSON_DIR / f"{stem}.json"
    readable_csv_path = INTERIM_CSV_DIR / f"{stem}.csv"
    parquet_path = PROCESSED_PARQUET_DIR / f"{stem}.parquet"

    write_extracted_json(extracted_json_path, data)

    normalized = normalize_json_data(data)
    readable = stringify_nested_columns(normalized)

    readable.to_csv(readable_csv_path, index=False)
    readable.to_parquet(parquet_path, index=False)

    return {
        "source_file": path.name,
        "json_member_name": member_name,
        "extracted_json_path": str(extracted_json_path.relative_to(PROJECT_ROOT)),
        "readable_csv_path": str(readable_csv_path.relative_to(PROJECT_ROOT)),
        "parquet_path": str(parquet_path.relative_to(PROJECT_ROOT)),
        "row_count": len(readable),
        "column_count": len(readable.columns),
    }


def convert_all_json_zips() -> pd.DataFrame:
    records = []

    for path in sorted(JSON_ZIP_DIR.glob("*.json.zip")):
        records.append(convert_json_zip(path))

    return pd.DataFrame(records)


def main() -> None:
    INTERIM_JSON_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_CSV_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    report = convert_all_json_zips()
    report.to_csv(CONVERSION_REPORT_PATH, index=False)

    print(report[["source_file", "row_count", "column_count", "readable_csv_path", "parquet_path"]].to_string(index=False))
    print()
    print(f"Saved conversion report to: {CONVERSION_REPORT_PATH}")


if __name__ == "__main__":
    main()
