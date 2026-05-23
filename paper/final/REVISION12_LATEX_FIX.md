# Revision 12 - LaTeX encoding fix

This revision fixes the Overleaf/pdfLaTeX errors:

- `Command \ocircumflex unavailable in encoding T1`
- `Command \ecircumflex unavailable in encoding T1`
- `Command \abreve unavailable in encoding T1`
- `Command \uhorn unavailable in encoding T1`
- `Command \ohorn unavailable in encoding T1`

Root cause: Vietnamese text in the qualitative table was being typeset under T1 encoding by pdfLaTeX. The fix keeps the document in pdfLaTeX-compatible mode, loads T5 support, and wraps Vietnamese snippets with `\viet{...}` so those cells use Vietnamese font encoding only where needed.

The paper now compiles with pdfLaTeX and no encoding errors.
