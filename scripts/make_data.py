from music_analytics.paths import make_paths
from music_analytics.build import save_data

make_paths()

tables = save_data()

print("Processed data saved.")
for name, table in tables.items():
    print(f"{name}: {len(table):,} rows")