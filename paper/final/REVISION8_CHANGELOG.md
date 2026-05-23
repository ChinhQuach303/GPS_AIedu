# Revision 8 changelog

## Paper edits

- Rewrote abstract/introduction/discussion/conclusion to reduce repetition and use a more formal scientific register.
- Added clearer distinctions between human-pilot evidence, simulated controlled comparison, cross-model stress test, and exploratory expanded corpus.
- Clarified that 45/45 answer keys are recoverable from raw solution text; remaining question-bank work is option/formula typography repair.
- Maintained conservative claims: GPS-Agent improves auditable tutoring-process control, not durable learning outcomes.
- Kept IRR negative result as a diagnostic and removed any reliability contribution.

## Code/pipeline edits

- Added `src/evaluation/metrics/question_bank_recovery.py`.
- Updated `scripts/audit_question_bank.py` to recover answer keys from `data/raw/exam_text.txt` rather than relying only on the damaged JSON.
- Added `tests/test_question_bank_recovery.py`.
- Added `scripts/final_paper_audit.py` for stale-claim, venue-label, reference, and repetition checks.

## Verification

- Question-bank recovery: 45/45 answer keys recovered.
- Tests: question-bank recovery and comprehensive metric tests passed.
- Paper audit: passed.
- PDF compile: passed, 7 pages.
