"""Shared display and model settings."""
LISTENER_NAME = "Sumaitat"
TIMEZONE = "America/New_York"
TZ_LABEL = "ET"
SHRINKAGE_K = 5
BLOCK_WEIGHTS = {"text": 1.00, "categorical": 0.85, "behavior": 1.25}
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
BUCKETS = ["00-04", "04-08", "08-12", "12-16", "16-20", "20-24"]
BUCKET_LABELS = dict(zip(BUCKETS, ["12–4 AM", "4–8 AM", "8 AM–12 PM", "12–4 PM", "4–8 PM", "8 PM–12 AM"]))
