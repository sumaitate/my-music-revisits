# Before / after headline numbers

All values below were executed against the local raw export. The original code and original parser were reconstructed from Git for the baseline tier audit. No raw data was edited.

| Metric | Before | After | Why |
|---|---|---|---|
| Listening events | 10454 | 10464 | Mixed ISO timestamp precision now parses 10 events previously dropped. |
| Plays (30s+) | 3743 | 3747 | Four of the recovered events meet the 30-second threshold. |
| Minutes | 9900.94 | 9909.94 | The recovered events add 8.9997 minutes; short events still contribute listening time. |
| Listening days | 143 | 143 | Grouping changes from UTC dates to Eastern calendar dates, with recovered timestamps included. |
| Longest day | 2026-01-01 / 331.88 min | 2025-12-31 / 225.24 min | Events near midnight move to their local calendar date. |
| Peak listening time | Wednesday 20-24 EST | Wed 20-24 ET | DST-aware ET replaces fixed EST; the peak is now based on average minutes per calendar weekday. |
| Top 5 artists | ATEEZ (826 events), Spiritual Concepts (381 events), Yves (344 events), XG (256 events), IVE (223 events) | ATEEZ (461 plays), Yves (169 plays), XG (156 plays), Spiritual Concepts (134 plays), aespa (113 plays) | Ranking uses valid plays, with safer metadata matching. |
| Unknown genre: all events | 15.07% | 15.35% | Ambiguous title-only identities are rejected; deterministic metadata tie resolution and recovered events also affect coverage. |
| Unknown genre: valid plays | 8.12% | 7.77% | Same metadata corrections, measured only among 30s+ plays. |
| Unknown duration share | 0.0096% | 0.0096% | One unknown-duration event remains; denominator includes the recovered events. |

## Metadata match rates

The baseline tiers were not stored originally; they were reconstructed from the original non-null precedence rules. The corrected tiers require an accepted artist and reject ambiguous titles.

| Tier | Before | After |
|---|---:|---:|
| exact title+album | 82.56% | 82.55% |
| daily title | 12.56% | 11.41% |
| library title | 0.19% | 0.11% |
| unmatched | 4.69% | 5.93% |

129 events are affected by ambiguous title-only matching. See `data/interim/data_check.json` for counts and rates.

The existing duplicate key remains event ID, timestamp, resolved track key, and duration. The ten extra retained events are explained by parsing, not merge multiplication or a deduplication-rule change. `newly_parsed_events.csv` records their timestamps and durations.
