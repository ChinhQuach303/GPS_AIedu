# Expanded Corpus Exploratory Statistics

This file is generated from `data/processed/expanded_exploratory_corpus.csv`, but the corpus should be described as an expanded/augmented behavioral corpus, not as a human-validated gold standard.

## Quality audit
- Rows: 2824
- Independence_Index > 1: 24
- Groups: {'GPS': 1577, 'Non-GPS': 1247}

## Group summary
| Group   |   n_sessions |   avg_independence_raw |   ii_gt_1 |   avg_independence_bounded |   avg_math_density |   avg_gps_fidelity |   avg_estimated_post_score |
|:--------|-------------:|-----------------------:|----------:|---------------------------:|-------------------:|-------------------:|---------------------------:|
| GPS     |         1577 |                 0.2921 |        24 |                     0.2866 |             5.026  |             0.5283 |                    64.75   |
| Non-GPS |         1247 |                 0      |         0 |                     0      |             2.5557 |             0.1    |                    62.6704 |

## Exploratory tests
| comparison     | metric                           |   gps_mean |   nongps_mean |     p_value |   cohen_d | interpretation                        |
|:---------------|:---------------------------------|-----------:|--------------:|------------:|----------:|:--------------------------------------|
| GPS vs Non-GPS | Estimated_Post_Score (heuristic) |      64.75 |       62.6704 | 1.34239e-05 |  0.161611 | exploratory_only_not_learning_outcome |
