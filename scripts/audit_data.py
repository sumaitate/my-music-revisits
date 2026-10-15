from music_analytics.paths import make_paths
from music_analytics.read import audit_data

make_paths()

audit = audit_data()

print("Raw audit saved to data/interim/raw_audit.csv")
print(audit[["file", "folder", "kind", "rows_sample"]].to_string(index=False))