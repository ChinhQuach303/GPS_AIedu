# GPS-Agent EMNLP Revision 8

This package is a local preview/Overleaf-ready source package for the GPS-Agent EMNLP system paper.

## Submit with official style
For the actual EMNLP submission, create a project from the official ACL/EMNLP template on Overleaf and copy `main.tex`, `figures/`, and `tables/` into that project. The bundled `acl.sty` is included only so the preview compiles in this sandbox.

## What Revision 8 fixed

- Rewrote the paper for a more scientific, less repetitive style.
- Added citation-backed framing in Related Work and Discussion.
- Replaced the old question-bank statement with a recovered-answer audit: 45/45 answer keys are recoverable from raw solution text.
- Separated answer-key coverage from option/formula typesetting repair.
- Kept IRR as a negative diagnostic, not a contribution.
- Added local paper audit checks for stale claims, venue-label mistakes, and repeated long phrases.
- Preserved conservative claims: interaction control only, no durable learning-outcome claim.

## Compile

```bash
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
```

Current preview: 7 pages, no undefined references, no repeated-line-number bug.
