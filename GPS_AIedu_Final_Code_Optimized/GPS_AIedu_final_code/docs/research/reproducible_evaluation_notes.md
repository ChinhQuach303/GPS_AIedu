# Reproducible Evaluation Notes

This project now separates evidence into four layers:

1. **Foundation / pilot interaction log**: 5 students x 45 questions, stored in `data/processed/GPS_AIedu.csv`.
2. **Controlled evaluation**: `cleaned_massive_results.csv` vs `cleaned_baseline_results.csv`.
3. **Cross-model stress test**: `cross_model_conversations.csv`.
4. **Expanded augmented corpus**: `gps_aiedu_gold_standard.csv`; this should be described as exploratory until independently audited.

Primary paper claims should use deterministic metrics from `src/evaluation/metrics/pedagogy_metrics.py`:

- Direct-answer leakage
- Phase validity
- Stall/scaffolding pressure
- Non-Vietnamese leakage

Secondary metrics:

- VAI
- Math Density
- Reflection completion

Do **not** hard-code IRR values. The current IRR script computes kappa from `data/outputs/irr_scores.csv`. If the observed kappa is low, report it as a limitation or rerun annotation with a better rubric/human raters.

Run:

```bash
PYTHONPATH=. python scripts/generate_conference_assets.py
```

Outputs:

- `reports/emnlp_evaluation/final_stats.txt`
- `reports/emnlp_evaluation/reproducible_report.json`
- `reports/emnlp_evaluation/tables/*.csv`
- `reports/emnlp_evaluation/figures/*.png`
- `data/outputs/research_stats/*.csv|json|md`
