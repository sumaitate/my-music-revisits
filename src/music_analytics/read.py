import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from music_analytics.paths import raw_path, work_path


def clean_name(value: str) -> str:
    value = str(value).strip()
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_").lower()


def clean_cols(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.columns = [clean_name(col) for col in data.columns]
    return data


def text_key(value) -> str:
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def find_file(name: str) -> Path | None:
    files = [path for path in raw_path.rglob(name) if path.is_file()]

    if files:
        return sorted(files)[0]

    return None


def need_file(name: str) -> Path:
    path = find_file(name)

    if path is None:
        raise FileNotFoundError(f"Missing raw file named {name} under data/raw.")

    return path


def read_csv(name: str) -> pd.DataFrame:
    path = need_file(name)
    data = pd.read_csv(path, low_memory=False)
    data = clean_cols(data)
    data["source_file"] = path.name
    return data


def read_zip(name: str) -> pd.DataFrame:
    path = need_file(name)

    with zipfile.ZipFile(path) as archive:
        names = [item for item in archive.namelist() if not item.endswith("/")]

        if not names:
            raise ValueError(f"No JSON file found inside {path}")

        with archive.open(names[0]) as file:
            value = json.load(file)

    if isinstance(value, dict):
        lists = [item for item in value.values() if isinstance(item, list)]
        data = pd.json_normalize(lists[0]) if len(lists) == 1 else pd.json_normalize(value)
    else:
        data = pd.json_normalize(value)

    data = clean_cols(data)
    data["source_file"] = path.name

    return data


def raw_files() -> list[Path]:
    files = []

    for path in raw_path.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() == ".csv" or path.name.endswith(".json.zip"):
            files.append(path)

    return sorted(files)


def audit_data() -> pd.DataFrame:
    rows = []

    for path in raw_files():
        if path.suffix.lower() == ".csv":
            data = pd.read_csv(path, nrows=5, low_memory=False)
            kind = "csv"

        elif path.name.endswith(".json.zip"):
            with zipfile.ZipFile(path) as archive:
                names = [item for item in archive.namelist() if not item.endswith("/")]

                if not names:
                    data = pd.DataFrame()
                else:
                    with archive.open(names[0]) as file:
                        value = json.load(file)

                    if isinstance(value, dict):
                        lists = [item for item in value.values() if isinstance(item, list)]
                        data = pd.json_normalize(lists[0]) if len(lists) == 1 else pd.json_normalize(value)
                    else:
                        data = pd.json_normalize(value)

            kind = "json_zip"

        else:
            continue

        rows.append(
            {
                "file": path.name,
                "folder": str(path.parent.relative_to(raw_path)),
                "kind": kind,
                "rows_sample": len(data),
                "columns": ", ".join([clean_name(col) for col in data.columns]),
            }
        )

    audit = pd.DataFrame(rows)

    if audit.empty:
        audit = pd.DataFrame(columns=["file", "folder", "kind", "rows_sample", "columns"])

    audit.to_csv(work_path / "raw_audit.csv", index=False)

    return audit


def as_time(value: pd.Series) -> pd.Series:
    number = pd.to_numeric(value, errors="coerce")

    if number.notna().mean() > 0.8 and number.dropna().gt(10**11).any():
        return pd.to_datetime(number, errors="coerce", unit="ms", utc=True)

    return pd.to_datetime(value, errors="coerce", utc=True)


def as_day(value: pd.Series) -> pd.Series:
    text = value.astype("string").str.replace(".0", "", regex=False)
    return pd.to_datetime(text, format="%Y%m%d", errors="coerce", utc=True)


def split_track(value: pd.Series) -> pd.DataFrame:
    text = value.fillna("").astype(str)
    split = text.str.split(" - ", n=1, expand=True)
    found = text.str.contains(" - ", regex=False)

    data = pd.DataFrame(index=value.index)
    data["artist"] = split[0].where(found, pd.NA)

    if split.shape[1] > 1:
        data["track"] = split[1].where(found, text)
    else:
        data["track"] = text

    data["track"] = data["track"].replace("", pd.NA)
    data["artist"] = data["artist"].replace("", pd.NA)

    return data


def safe_rate(top: pd.Series, bottom: pd.Series) -> pd.Series:
    top = pd.to_numeric(top, errors="coerce").fillna(0).astype(float)
    bottom = pd.to_numeric(bottom, errors="coerce").fillna(0).astype(float)

    value = np.divide(
        top.to_numpy(),
        bottom.to_numpy(),
        out=np.zeros(len(top), dtype=float),
        where=bottom.to_numpy() != 0,
    )

    return pd.Series(value, index=top.index)