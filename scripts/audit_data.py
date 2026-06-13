import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from music_analytics.read import audit_data

audit = audit_data()

print("Raw audit saved to data/interim/raw_audit.csv")
print(audit[["file", "folder", "kind", "rows_sample"]].to_string(index=False))