from pathlib import Path

root_path = Path(__file__).resolve().parents[2]

data_path = root_path / "data"
raw_path = data_path / "raw"
csv_path = raw_path / "csv"
zip_path = raw_path / "json_zips"

work_path = data_path / "interim"
clean_path = data_path / "processed"

report_path = root_path / "reports"
plot_path = report_path / "figures"
model_path = root_path / "models"


def make_paths() -> None:
    paths = [
        csv_path,
        zip_path,
        work_path,
        clean_path,
        report_path,
        plot_path,
        model_path,
    ]

    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


make_paths()