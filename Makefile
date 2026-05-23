.PHONY: test metrics audit-question-bank audit-paper paper

test:
	PYTHONPATH=. python -m pytest -q

metrics:
	PYTHONPATH=. python scripts/run_full_metrics_emnlp_pipeline.py

audit-question-bank:
	PYTHONPATH=. python scripts/audit_question_bank.py

audit-paper:
	PYTHONPATH=. python scripts/final_paper_audit.py paper/emnlp_final/main.tex

paper:
	cd paper/emnlp_final && latexmk -pdf main.tex
