"""Event-rate shrinkage shared by feature engineering and recommendations."""
from music_analytics.config import SHRINKAGE_K


def smoothed_rate(successes, plays, global_rate, k=SHRINKAGE_K):
    """Treat k observations at the global event rate as prior evidence."""
    if k <= 0:
        raise ValueError("k must be positive")
    return (successes + k * global_rate) / (plays + k)
