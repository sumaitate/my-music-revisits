import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from music_analytics.build import save_data

tables = save_data()

print("Processed data saved.")
for name, table in tables.items():
    print(f"{name}: {len(table):,} rows")