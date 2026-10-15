# Replay evaluation

## Protocol

Cutoffs are midnight America/New_York. Training is strictly before each cutoff; targets fall in [cutoff, cutoff + 28 calendar days). Only tracks with a prior valid play are eligible. Targets are all tracks with a valid play in the test window, as specified. Unseen future tracks cannot be returned from the eligible set, but remain in recall and NDCG denominators; eligible targets and unseen targets are reported separately. This imposes an explicit achievable-recall ceiling.

Library snapshot play/skip counts, added_at, and playlist_count/playlist_log are excluded from evaluation features. Numeric neighbor blocks therefore have five columns in evaluation, six in production. Metadata still comes from the export: historical metadata revisions cannot be reconstructed.

The first two windows tune the affinity/completion/exposure blend on the approved 0.25 grid; the last two are held out. The selected weights are {"affinity": 0.5, "completion": 0.5, "exposure": 0.0}. Risk and the outer 0.70 quality / 0.25 friction coefficients are unchanged. Both final-score methods apply readiness and Leave Alone/Unknown Artist exclusions; simple baselines rank the full eligible set. Short recommendation lists are penalized, not padded.

The production default weights remain separately recorded in recommend_settings.json. recommend_score tests those production weights in evaluation mode; tuned_recommend_score separately tests the blend selected on earlier windows. The tuning result does not silently replace production weights or claim an export-snapshot model was backtested.

Recall@k = hits / all test-window valid-play targets; HitRate@k = whether any hit appears; NDCG@k uses binary relevance and logarithmic rank discounts. Artist counts include Unknown Artist as a single label where baselines return it. Standard deviations are sample standard deviations across windows. Random uses seed 42, one draw per window; its variability is across windows, not many random seeds.

## Windows

```
   split                    cutoff                window_end  eligible_tracks  target_tracks  eligible_target_tracks  unseen_future_tracks
  tuning 2025-12-20T00:00:00-05:00 2026-01-17T00:00:00-05:00              595            313                      85                   228
  tuning 2025-12-27T00:00:00-05:00 2026-01-24T00:00:00-05:00              598            381                     112                   269
held_out 2026-01-31T00:00:00-05:00 2026-02-28T00:00:00-05:00              921            148                      83                    65
held_out 2026-02-07T00:00:00-05:00 2026-03-07T00:00:00-05:00              939            168                      87                    81
```

## Held-out results

| Method | k | Recall mean Ã‚Â± SD | HitRate mean Ã‚Â± SD | NDCG mean Ã‚Â± SD | Artists mean Ã‚Â± SD |
|---|---:|---:|---:|---:|---:|
| affinity | 10 | 0.042 Ã‚Â± 0.026 | 1.000 Ã‚Â± 0.000 | 0.681 Ã‚Â± 0.340 | 6.5 Ã‚Â± 0.7 |
| affinity | 25 | 0.103 Ã‚Â± 0.036 | 1.000 Ã‚Â± 0.000 | 0.663 Ã‚Â± 0.218 | 16.5 Ã‚Â± 0.7 |
| affinity | 50 | 0.161 Ã‚Â± 0.068 | 1.000 Ã‚Â± 0.000 | 0.553 Ã‚Â± 0.203 | 29.0 Ã‚Â± 0.0 |
| most_recent | 10 | 0.030 Ã‚Â± 0.025 | 1.000 Ã‚Â± 0.000 | 0.428 Ã‚Â± 0.288 | 9.0 Ã‚Â± 1.4 |
| most_recent | 25 | 0.052 Ã‚Â± 0.040 | 1.000 Ã‚Â± 0.000 | 0.343 Ã‚Â± 0.230 | 19.0 Ã‚Â± 4.2 |
| most_recent | 50 | 0.105 Ã‚Â± 0.014 | 1.000 Ã‚Â± 0.000 | 0.342 Ã‚Â± 0.074 | 34.0 Ã‚Â± 7.1 |
| most_valid_plays | 10 | 0.039 Ã‚Â± 0.021 | 1.000 Ã‚Â± 0.000 | 0.646 Ã‚Â± 0.268 | 8.0 Ã‚Â± 0.0 |
| most_valid_plays | 25 | 0.097 Ã‚Â± 0.035 | 1.000 Ã‚Â± 0.000 | 0.629 Ã‚Â± 0.196 | 17.0 Ã‚Â± 0.0 |
| most_valid_plays | 50 | 0.157 Ã‚Â± 0.045 | 1.000 Ã‚Â± 0.000 | 0.540 Ã‚Â± 0.136 | 31.0 Ã‚Â± 0.0 |
| neighbors_behavior | 10 | 0.006 Ã‚Â± 0.001 | 1.000 Ã‚Â± 0.000 | 0.149 Ã‚Â± 0.100 | 8.5 Ã‚Â± 0.7 |
| neighbors_behavior | 25 | 0.032 Ã‚Â± 0.003 | 1.000 Ã‚Â± 0.000 | 0.197 Ã‚Â± 0.055 | 20.0 Ã‚Â± 0.0 |
| neighbors_behavior | 50 | 0.077 Ã‚Â± 0.016 | 1.000 Ã‚Â± 0.000 | 0.227 Ã‚Â± 0.056 | 32.0 Ã‚Â± 0.0 |
| neighbors_categorical | 10 | 0.029 Ã‚Â± 0.007 | 1.000 Ã‚Â± 0.000 | 0.397 Ã‚Â± 0.057 | 2.0 Ã‚Â± 0.0 |
| neighbors_categorical | 25 | 0.064 Ã‚Â± 0.015 | 1.000 Ã‚Â± 0.000 | 0.386 Ã‚Â± 0.055 | 3.0 Ã‚Â± 0.0 |
| neighbors_categorical | 50 | 0.102 Ã‚Â± 0.027 | 1.000 Ã‚Â± 0.000 | 0.335 Ã‚Â± 0.056 | 5.0 Ã‚Â± 0.0 |
| neighbors_combined | 10 | 0.026 Ã‚Â± 0.011 | 1.000 Ã‚Â± 0.000 | 0.446 Ã‚Â± 0.220 | 4.0 Ã‚Â± 0.0 |
| neighbors_combined | 25 | 0.048 Ã‚Â± 0.009 | 1.000 Ã‚Â± 0.000 | 0.358 Ã‚Â± 0.101 | 12.0 Ã‚Â± 1.4 |
| neighbors_combined | 50 | 0.093 Ã‚Â± 0.022 | 1.000 Ã‚Â± 0.000 | 0.329 Ã‚Â± 0.082 | 22.5 Ã‚Â± 0.7 |
| neighbors_text | 10 | 0.013 Ã‚Â± 0.001 | 1.000 Ã‚Â± 0.000 | 0.144 Ã‚Â± 0.006 | 3.5 Ã‚Â± 0.7 |
| neighbors_text | 25 | 0.031 Ã‚Â± 0.006 | 1.000 Ã‚Â± 0.000 | 0.165 Ã‚Â± 0.039 | 9.5 Ã‚Â± 0.7 |
| neighbors_text | 50 | 0.064 Ã‚Â± 0.006 | 1.000 Ã‚Â± 0.000 | 0.178 Ã‚Â± 0.003 | 13.5 Ã‚Â± 0.7 |
| random | 10 | 0.003 Ã‚Â± 0.004 | 0.500 Ã‚Â± 0.707 | 0.043 Ã‚Â± 0.060 | 9.0 Ã‚Â± 0.0 |
| random | 25 | 0.009 Ã‚Â± 0.004 | 1.000 Ã‚Â± 0.000 | 0.053 Ã‚Â± 0.029 | 21.5 Ã‚Â± 0.7 |
| random | 50 | 0.022 Ã‚Â± 0.003 | 1.000 Ã‚Â± 0.000 | 0.065 Ã‚Â± 0.020 | 42.5 Ã‚Â± 2.1 |
| recommend_score | 10 | 0.033 Ã‚Â± 0.021 | 1.000 Ã‚Â± 0.000 | 0.542 Ã‚Â± 0.311 | 7.5 Ã‚Â± 0.7 |
| recommend_score | 25 | 0.087 Ã‚Â± 0.039 | 1.000 Ã‚Â± 0.000 | 0.557 Ã‚Â± 0.234 | 17.0 Ã‚Â± 0.0 |
| recommend_score | 50 | 0.151 Ã‚Â± 0.054 | 1.000 Ã‚Â± 0.000 | 0.501 Ã‚Â± 0.167 | 28.0 Ã‚Â± 0.0 |
| smoothed_completion | 10 | 0.029 Ã‚Â± 0.007 | 1.000 Ã‚Â± 0.000 | 0.387 Ã‚Â± 0.057 | 8.0 Ã‚Â± 0.0 |
| smoothed_completion | 25 | 0.067 Ã‚Â± 0.010 | 1.000 Ã‚Â± 0.000 | 0.393 Ã‚Â± 0.027 | 18.0 Ã‚Â± 0.0 |
| smoothed_completion | 50 | 0.141 Ã‚Â± 0.039 | 1.000 Ã‚Â± 0.000 | 0.420 Ã‚Â± 0.071 | 31.5 Ã‚Â± 0.7 |
| tuned_recommend_score | 10 | 0.035 Ã‚Â± 0.008 | 1.000 Ã‚Â± 0.000 | 0.541 Ã‚Â± 0.154 | 9.0 Ã‚Â± 0.0 |
| tuned_recommend_score | 25 | 0.083 Ã‚Â± 0.025 | 1.000 Ã‚Â± 0.000 | 0.523 Ã‚Â± 0.155 | 17.5 Ã‚Â± 0.7 |
| tuned_recommend_score | 50 | 0.151 Ã‚Â± 0.045 | 1.000 Ã‚Â± 0.000 | 0.485 Ã‚Â± 0.132 | 27.5 Ã‚Â± 0.7 |

## Interpretation

At k=25, the production-score NDCG is 0.557, the tuned blend is 0.523, most-valid-plays is 0.629, and affinity is 0.663. Compare these descriptive values with their across-window variability; tuning is not evidence of an improvement.

## Neighbor ablation

Text-only, categorical-only, behavior-only, and combined blocks are evaluated against the same replay targets. Each candidate is scored by cosine similarity to the full pre-cutoff history weighted by valid-play counts, excluding its own contribution. This is a historical-profile proxy, not a test of the dashboard's user-selected seeds. No future plays select seeds or weight the profile.

## Limitations

One listener, a short export window, only two held-out windows, and overlapping 28-day windows make these estimates unstable and correlated. They are descriptive, not statistical evidence of general superiority. HitRate can saturate for a single user. Replay is not satisfaction; absence of replay is not dislike. Snapshot metadata and identity resolution remain limitations even though snapshot behavioral features are excluded. Training-window metrics are available in the CSV for audit, not presented as held-out evidence.
