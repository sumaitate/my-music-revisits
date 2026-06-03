from pathlib import Path
import json
import zipfile

import pandas as pd


PROJECT_ROOT = Path.cwd()

CSV_DIR = PROJECT_ROOT / "data" / "raw" / "csv"
JSON_ZIP_DIR = PROJECT_ROOT / "data" / "raw" / "json_zips"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"

INVENTORY_PATH = METADATA_DIR / "raw_data_inventory.csv"


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as file:
        return max(sum(1 for _ in file) - 1, 0)


def inspect_csv(path: Path) -> dict:
    preview = pd.read_csv(path, nrows=5)

    return {
        "file_name": path.name,
        "file_type": "csv",
        "row_count": count_csv_rows(path),
        "column_count": len(preview.columns),
        "columns": ", ".join(preview.columns),
        "notes": "CSV export table",
    }


def read_json_zip(path: Path):
    with zipfile.ZipFile(path, "r") as zip_file:
        member_name = zip_file.namelist()[0]

        with zip_file.open(member_name) as file:
            data = json.load(file)

    return member_name, data


def inspect_json_zip(path: Path) -> dict:
    member_name, data = read_json_zip(path)

    if isinstance(data, list):
        normalized = pd.json_normalize(data, sep=".")
        row_count = len(normalized)
        column_count = len(normalized.columns)
        columns = ", ".join(normalized.columns)
        notes = f"JSON zip list from {member_name}"
    elif isinstance(data, dict):
        row_count = 1
        column_count = len(data)
        columns = ", ".join(data.keys())
        notes = f"JSON zip object from {member_name}"
    else:
        row_count = 1
        column_count = 1
        columns = "value"
        notes = f"JSON zip {type(data).__name__} from {member_name}"

    return {
        "file_name": path.name,
        "file_type": "json_zip",
        "row_count": row_count,
        "column_count": column_count,
        "columns": columns,
        "notes": notes,
    }


def inspect_all_raw_files() -> pd.DataFrame:
    records = []

    for path in sorted(CSV_DIR.glob("*.csv")):
        records.append(inspect_csv(path))

    for path in sorted(JSON_ZIP_DIR.glob("*.json.zip")):
        records.append(inspect_json_zip(path))

    return pd.DataFrame(records)


def main() -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    inventory = inspect_all_raw_files()
    inventory.to_csv(INVENTORY_PATH, index=False)

    print(inventory[["file_name", "file_type", "row_count", "column_count"]].to_string(index=False))
    print()
    print(f"Saved inventory to: {INVENTORY_PATH}")


if __name__ == "__main__":
    main()
