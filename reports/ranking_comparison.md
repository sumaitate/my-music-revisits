# Ranking comparison

Events count every retained positive-duration PLAY_END. Valid plays last at least 30 seconds. Minutes include all retained event time.

Spearman correlations use average-tie ranks of the actual scores within the union of each pair of top-10 sets. Top-10 ties use the sorted entity key for reproducibility.

entity        left       right  top10_overlap  union_size  spearman
artist      events valid_plays             10          10  0.705170
artist      events     minutes              9          11  0.481818
artist valid_plays     minutes              9          11  0.788157
 track      events valid_plays              9          11  0.733487
 track      events     minutes              8          12  0.388792
 track valid_plays     minutes              9          11  0.727273
