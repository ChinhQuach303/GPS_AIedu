#!/usr/bin/env python3
"""Build an Overleaf/Prism-ready LaTeX project from current GPS metrics.

The generated project is self-contained enough to compile locally. For final
submission, replace the local compatibility `acl.sty`/`acl_natbib.bst` with the
official files from https://github.com/acl-org/acl-style-files.
"""
from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import textwrap
import zipfile

import pandas as pd

ROOT = Path.cwd()
REPORT = ROOT / "reports" / "evaluation"
TABLES = REPORT / "tables"
FIGS = REPORT / "figures"
OUT = ROOT / "paper" / "overleaf"


def fmt_pct(x: float) -> str:
    return f"{100 * float(x):.1f}"


def fmt_num(x: float, n: int = 3) -> str:
    return f"{float(x):.{n}f}"


def sci(x: float) -> str:
    x = float(x)
    if x == 0:
        return "0"
    if x < 0.001:
        return f"{x:.2e}"
    return f"{x:.3f}"


def latex_escape(s: object) -> str:
    text = str(s)
    repl = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
        "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def load_assets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    main = pd.read_csv(TABLES / "table_main_system_comparison.csv")
    stats = pd.read_csv(TABLES / "table_statistical_tests.csv")
    level = pd.read_csv(TABLES / "table_by_student_level.csv")
    report = json.loads((REPORT / "reproducible_report.json").read_text(encoding="utf-8"))
    return main, stats, level, report


def table_main_tex(main: pd.DataFrame) -> str:
    rows = []
    for _, r in main.iterrows():
        rows.append(
            f"{latex_escape(r['system'])} & {int(r['n_sessions'])} & {fmt_pct(r['direct_answer_leakage_rate'])} & "
            f"{fmt_pct(r['phase_validity_rate'])} & {fmt_num(r['vai_mean'])} & {fmt_pct(r['stall_rate'])} \\\\"
        )
    return "\n".join(rows)


def table_level_tex(level: pd.DataFrame) -> str:
    gps = level[level.system.eq("GPS-Agent")].copy()
    order = ["Giỏi", "Khá", "Trung bình", "Yếu"]
    # ASCII labels for safer pdfLaTeX.
    label_map = {"Giỏi": "Excellent", "Khá": "Good", "Trung bình": "Average", "Yếu": "Weak"}
    gps["_order"] = gps["level"].map({k: i for i, k in enumerate(order)}).fillna(99)
    gps = gps.sort_values("_order")
    rows = []
    for _, r in gps.iterrows():
        rows.append(
            f"{label_map.get(r['level'], latex_escape(r['level']))} & {int(r['n_sessions'])} & "
            f"{fmt_pct(r['direct_answer_leakage_rate'])} & {fmt_pct(r['phase_validity_rate'])} & "
            f"{fmt_num(r['vai_mean'])} & {fmt_pct(r['stall_rate'])} \\\\"
        )
    return "\n".join(rows)


def write_acl_compat_files() -> None:
    (OUT / "acl.sty").write_text(textwrap.dedent(r"""
        \NeedsTeXFormat{LaTeX2e}
        \ProvidesPackage{acl}[2026/05/22 ACL-compatible local compile fallback]
        \newif\ifaclreview
        \DeclareOption{review}{\aclreviewtrue}
        \DeclareOption{final}{\aclreviewfalse}
        \ProcessOptions\relax
        \RequirePackage[letterpaper,margin=1in]{geometry}
        \RequirePackage{times}
        \RequirePackage{latexsym}
        \RequirePackage{fancyhdr}
        \RequirePackage{titlesec}
        \RequirePackage{etoolbox}
        \setlength{\columnsep}{0.25in}
        \setlength{\parindent}{1em}
        \setlength{\parskip}{0pt}
        \AtBeginDocument{\if@twocolumn\else\twocolumn\fi}
        \pagestyle{plain}
        \titleformat{\section}{\large\bfseries}{\thesection}{0.5em}{}
        \titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{0.5em}{}
        \titleformat{\subsubsection}{\normalsize\itshape}{\thesubsubsection}{0.5em}{}
        \newcommand{\aclfinalcopy}{}
        \newcommand{\aclpaperid}[1]{}
        \newcommand{\aclsection}[1]{\section{#1}}
        \renewenvironment{abstract}{\begin{center}\bfseries Abstract\end{center}\small}{\par}
        \ifaclreview
          \fancyhf{}
          \fancyfoot[C]{\thepage}
        \fi
    """).strip() + "\n", encoding="utf-8")
    try:
        plainnat = subprocess.run(["kpsewhich", "plainnat.bst"], text=True, capture_output=True)
        if plainnat.returncode == 0 and plainnat.stdout.strip():
            shutil.copyfile(plainnat.stdout.strip(), OUT / "acl_natbib.bst")
        else:
            (OUT / "acl_natbib.bst").write_text("", encoding="utf-8")
    except FileNotFoundError:
        (OUT / "acl_natbib.bst").write_text("", encoding="utf-8")


def write_files() -> None:
    main, stats, level, report = load_assets()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    (OUT / "tables").mkdir(exist_ok=True)

    # Copy current figures/tables for auditability.
    for fig in ["fig_direct_answer_leakage.png", "fig_phase_validity.png", "fig_vai.png", "fig_stall_rate.png"]:
        shutil.copyfile(FIGS / fig, OUT / "figures" / fig)
    for tab in ["table_main_system_comparison.csv", "table_statistical_tests.csv", "table_by_student_level.csv", "dataset_manifest.csv"]:
        src = TABLES / tab
        if src.exists():
            shutil.copyfile(src, OUT / "tables" / tab)

    write_acl_compat_files()

    gps = main[main.system.eq("GPS-Agent")].iloc[0]
    base = main[main.system.eq("Single-Agent")].iloc[0]
    cross = main[main.system.eq("Cross-Model Phi-3")].iloc[0]
    leak = stats[(stats.comparison.eq("GPS-Agent vs Single-Agent")) & (stats.metric.eq("Direct-answer leakage"))].iloc[0]
    phase = stats[(stats.comparison.eq("GPS-Agent vs Single-Agent")) & (stats.metric.eq("Phase validity"))].iloc[0]
    vai = stats[(stats.comparison.eq("GPS-Agent vs Single-Agent")) & (stats.metric.eq("VAI"))].iloc[0]
    stall = stats[(stats.comparison.eq("GPS-Agent vs Single-Agent")) & (stats.metric.eq("Stall rate"))].iloc[0]
    human_pilot = report["human_pilot_summary"]
    qb = report["question_bank_audit"]
    irr = report["irr"]

    main_table = table_main_tex(main)
    level_table = table_level_tex(level)

    tex = rf"""
\documentclass[11pt]{{article}}
\usepackage[review]{{acl}}
\usepackage{{times}}
\usepackage{{latexsym}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{microtype}}
\usepackage{{url}}
\usepackage{{natbib}}
\usepackage[hidelinks]{{hyperref}}

\title{{GPS-Agent: A State-Graph Framework for Reducing Direct Answer-Giving in LLM-Based Mathematics Tutoring}}

\author{{Anonymous Submission}}

\begin{{document}}
\maketitle
\begin{{abstract}}
Large language models can solve mathematics problems fluently, but this ability creates a pedagogical failure mode: the tutor gives the answer before the learner has reasoned through the problem. We present GPS-Agent, a stateful multi-agent tutoring framework that enforces a Guide--Practice--Solve protocol through graph-based routing. GPS-Agent is evaluated on a Vietnamese mathematics tutoring corpus with {human_pilot['students']} student profiles, {human_pilot['questions']} probability/combinatorics questions, {human_pilot['sessions']} human pilot sessions, and {human_pilot['human_pilot_turns']} annotated Guide/Practice/Solve turns, plus a controlled simulation suite comparing {int(gps['n_sessions'])} GPS-Agent sessions against {int(base['n_sessions'])} single-agent baseline sessions over {int(gps['n_questions'])} questions. The primary result is pedagogical control rather than test-score improvement: GPS-Agent reduces direct-answer leakage from {fmt_pct(base['direct_answer_leakage_rate'])}\% to {fmt_pct(gps['direct_answer_leakage_rate'])}\% (Fisher exact $p={sci(leak['p_value'])}$, odds ratio={fmt_num(leak['fisher_odds_ratio'])}) and increases valid Guide--Practice--Solve trajectories from {fmt_pct(base['phase_validity_rate'])}\% to {fmt_pct(gps['phase_validity_rate'])}\%. Secondary autonomy metrics do not yet show a reliable improvement, and failure analysis reveals a major remaining limitation: scaffolding pressure, where the tutor over-extends Practice turns. These results support the narrower claim that architectural constraints can reduce premature answer-giving, while longer-term learning gains require validated human pre/post studies.
\end{{abstract}}

\section{{Introduction}}
LLM-based tutors are attractive because they provide immediate, fluent, and individualized help. In mathematics education, however, the same fluency can undermine learning: a model often supplies a complete worked solution when the student needs a hint, a decomposition, or a prompt for self-explanation. We call this the \emph{{Answer-Giving Trap}}. It is not primarily an accuracy problem; the answer may be correct. It is a process-quality problem because the tutor may bypass the student's own reasoning.

This paper studies whether an architectural constraint can reduce that failure mode. GPS-Agent implements a three-phase protocol: \textbf{{Guide}}, where the tutor asks conceptual questions; \textbf{{Practice}}, where the student performs a sub-step; and \textbf{{Solve}}, where the tutor confirms the result and requests reflection. The protocol is implemented with specialized agents and a Supervisor over a state graph, rather than with a single prompt alone.

Our empirical claim is deliberately conservative. We do not claim that the current data prove long-term learning gain. Instead, we show that GPS-Agent improves two process-level outcomes that can be audited from tutoring logs: direct-answer leakage and phase validity. This positioning is important because the project includes both foundation logs and large augmented corpora; mixing them without clear labels would overstate the evidence.

\paragraph{{Contributions.}} We make three contributions. First, we formulate the Answer-Giving Trap as a measurable tutoring-system failure mode. Second, we introduce GPS-Agent, a state-graph framework for enforcing Guide--Practice--Solve sequencing. Third, we provide a reproducible evaluation pipeline that separates foundation data, controlled simulation, cross-model stress testing, and exploratory augmented data.

\section{{Related Work}}
Classical intelligent tutoring systems show that step-level feedback and cognitive scaffolding can outperform unguided worked solutions \citep{{vanlehn2011relative,koedinger2006cognitive}}. However, these systems often require domain-specific knowledge engineering. LLM-based tutors offer open-ended natural language interaction, but prior work has shown that pedagogical behavior is not guaranteed by fluency alone \citep{{tack2022teacher,macina2023mathdial}}.

The GPS protocol is motivated by faded scaffolding \citep{{wood1976role}} and the Zone of Proximal Development \citep{{vygotsky1978mind}}. It also relates to autonomy-supportive learning theories \citep{{ryan2000self}}: the tutor should create conditions for student reasoning rather than replace it. Multi-agent and graph-based LLM systems make it possible to encode such behavioral constraints as explicit routing policies rather than as soft instructions \citep{{wu2023autogen}}.

\section{{GPS-Agent}}
\subsection{{Protocol}}
GPS-Agent uses three pedagogical phases. In Guide, the tutor elicits prior knowledge and problem understanding without revealing the numerical solution. In Practice, the tutor asks for exactly one local computation or reasoning step. In Solve, the tutor verifies the final answer and asks for self-explanation. A session is phase-valid only if Solve occurs after at least one Guide and one Practice state.

\subsection{{State-Graph Architecture}}
The system stores message history, current phase, phase trace, student profile, and routing metadata in a shared state. A Supervisor classifies the next pedagogical action and dispatches to one of the specialized nodes. Compared with a single-agent prompt, this design makes the phase boundary explicit and auditable.

\subsection{{Anti-Stagnation}}
The current implementation includes a rule-based anti-stagnation signal. When the same phase repeats too many times without progress, the pipeline flags scaffolding pressure. In the present data, this signal is still a limitation rather than a solved component: GPS-Agent has a stall rate of {fmt_pct(gps['stall_rate'])}\%, compared with {fmt_pct(base['stall_rate'])}\% for the baseline, because the baseline does not attempt multi-turn scaffolding.

\section{{Data}}
\subsection{{Human Pilot}}
The human pilot layer contains {human_pilot['students']} student profiles and {human_pilot['questions']} probability/combinatorics questions, yielding {human_pilot['sessions']} student-question sessions and {human_pilot['human_pilot_turns']} annotated turns. Phase counts are Guide={human_pilot['phase_counts'].get('G', 0)}, Practice={human_pilot['phase_counts'].get('P', 0)}, and Solve={human_pilot['phase_counts'].get('S', 0)}. This layer is used to define the problem setting and calibrate the GPS protocol.

\subsection{{Controlled Evaluation Layer}}
The primary comparison uses {int(gps['n_sessions'])} GPS-Agent sessions and {int(base['n_sessions'])} single-agent baseline sessions over {int(gps['n_questions'])} unique questions and {int(gps['n_levels'])} student levels. This is the main layer used for statistical comparison because both conditions share the same schema.

\subsection{{Cross-Model Stress Test}}
We additionally evaluate {int(cross['n_sessions'])} sessions using an independent Phi-3-style student simulator. This is not presented as a success-only result: it exposes higher leakage ({fmt_pct(cross['direct_answer_leakage_rate'])}\%), high stall ({fmt_pct(cross['stall_rate'])}\%), and non-Vietnamese leakage ({fmt_pct(cross['non_vietnamese_leakage_rate'])}\%).

\subsection{{Data Quality Audit}}
The extracted question bank contains {qb['n_questions']} questions. The audit finds {qb['missing_answer']} missing answers and {qb['questions_with_blank_options']} questions with blank or malformed options. Therefore, correctness-based claims are restricted to validated subsets; the full 45-question pool is used primarily for tutoring-process analysis.

\section{{Metrics}}
\paragraph{{Direct-answer leakage.}} A session is flagged when the tutor gives answer-like or computation-heavy content before a valid Solve path is reached. This is the primary Answer-Giving Trap metric.

\paragraph{{Phase validity.}} A GPS trajectory is valid when Solve occurs only after Guide and Practice. Single-agent sessions have no explicit phase protocol and are therefore phase-invalid by design for this metric.

\paragraph{{VAI and math density.}} The Verifiable Autonomy Index (VAI) is the share of explicit mathematical expressions contributed by the student:
\begin{{equation}}
\mathrm{{VAI}} = \frac{{M_{{student}}}}{{M_{{student}} + M_{{tutor}}}}.
\end{{equation}}
Math density is the mean number of explicit mathematical expressions per student turn. These are secondary engagement indicators, not validated learning-gain metrics.

\section{{Results}}
\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrr}}
\toprule
System & $N$ & Leakage (\%) & Phase-valid (\%) & VAI & Stall (\%) \\
\midrule
{main_table}
\bottomrule
\end{{tabular}}
\caption{{Main controlled evaluation. Leakage and phase validity are the primary process metrics. VAI is secondary and is not a significant GPS-Agent improvement in the current logs.}}
\label{{tab:main}}
\end{{table*}}

Table~\ref{{tab:main}} shows the main controlled comparison. GPS-Agent reduces direct-answer leakage from {fmt_pct(base['direct_answer_leakage_rate'])}\% to {fmt_pct(gps['direct_answer_leakage_rate'])}\%, a relative reduction of {abs(float(leak['relative_delta_pct'])):.1f}\% (Fisher exact $p={sci(leak['p_value'])}$). It also increases phase validity from {fmt_pct(base['phase_validity_rate'])}\% to {fmt_pct(gps['phase_validity_rate'])}\% ($p={sci(phase['p_value'])}$). This supports the claim that a state-graph tutor can enforce pedagogical sequencing more reliably than a single-agent baseline.

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{figures/fig_direct_answer_leakage.png}}
\caption{{Direct-answer leakage is substantially lower in GPS-Agent than in the single-agent baseline.}}
\label{{fig:leakage}}
\end{{figure}}

The secondary autonomy metrics are more cautious. GPS-Agent obtains VAI={fmt_num(gps['vai_mean'])}, while the baseline obtains VAI={fmt_num(base['vai_mean'])}; the difference is not statistically reliable ($p={sci(vai['p_value'])}$, Cohen's $d={fmt_num(vai['cohen_d'])}$). Math density follows the same pattern and should not be used as a central claim without stronger human validation.

\begin{{table}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrr}}
\toprule
Level & $N$ & Leak. & Valid & VAI & Stall \\
\midrule
{level_table}
\bottomrule
\end{{tabular}}
\caption{{GPS-Agent results by student level. Level labels are translated to English for submission readability.}}
\label{{tab:level}}
\end{{table}}

\section{{Failure Analysis}}
The main failure mode is scaffolding pressure. GPS-Agent flags stall in {fmt_pct(gps['stall_rate'])}\% of controlled sessions. This is expected for a tutor that tries to preserve student reasoning, but it is still pedagogically risky: excessive Practice turns may frustrate weaker or disengaged students. The cross-model stress test amplifies this issue, with stall={fmt_pct(cross['stall_rate'])}\% and non-Vietnamese leakage={fmt_pct(cross['non_vietnamese_leakage_rate'])}\%.

The current IRR file should also be treated as a diagnostic rather than a validation result. Recomputed agreement is quadratic weighted kappa={fmt_num(irr['quadratic_weighted_kappa'])} over {irr['n']} paired ratings. We therefore do not claim substantial inter-rater agreement.

\section{{Discussion}}
The results support a focused architectural conclusion: GPS-Agent reduces premature answer-giving and makes pedagogical phase control auditable. This is weaker than claiming improved learning, but it is also more defensible. In educational NLP, process control is a necessary intermediate outcome: a tutor that cannot avoid giving away answers is unlikely to support independent problem solving.

The stall results reveal the next engineering target. A better Supervisor should distinguish productive struggle from unproductive stagnation. The next version should combine explicit student-state modeling, a frustration detector, and adaptive fading policies rather than relying only on consecutive-phase heuristics.

\section{{Conclusion}}
We presented GPS-Agent, a state-graph framework for pedagogically constrained LLM tutoring in mathematics. In controlled evaluation, GPS-Agent substantially reduces direct-answer leakage and improves Guide--Practice--Solve phase validity. However, VAI and math density do not yet provide strong evidence of learning improvement, and scaffolding pressure remains a major limitation. The current contribution is therefore best understood as a reproducible system paper on pedagogical process control, not as a completed learning-outcomes study.

\section{{Limitations}}
The foundation layer is small and should not be interpreted as a large-scale classroom trial. The controlled comparison uses LLM-as-student simulation, which cannot fully capture human affect, motivation, or long-term retention. The question bank requires further cleaning before correctness-based evaluation over all 45 questions. The IRR study must be rerun with calibrated human or carefully validated judge labels. Finally, the local LaTeX package included in this artifact is a compile-compatible fallback; authors should replace it with the official ACL style files for final submission.

\section{{Ethics Statement}}
GPS-Agent is designed to assist teachers rather than replace them. Any classroom deployment should obtain informed consent, protect student logs, and avoid using autonomy metrics as punitive student evaluations. Direct-answer leakage and stall alerts should be interpreted as system diagnostics and teacher-support signals.

\begin{{thebibliography}}{{}}
\bibitem[Koedinger and Corbett(2006)]{{koedinger2006cognitive}}
Koedinger, Kenneth R. and Corbett, Albert T. 2006.
\newblock Cognitive tutors: Technology bringing learning science to the classroom.
\newblock In \emph{{The Cambridge Handbook of the Learning Sciences}}.

\bibitem[Macina et~al.(2023)]{{macina2023mathdial}}
Macina, Jakub, Nico Daheim, Saurabh Srivastava, Philipp Mondorf, Katja Markert, Mrinmaya Sachan, and Mirella Lapata. 2023.
\newblock MathDial: A dialogue tutoring dataset with rich pedagogical properties grounded in math reasoning problems.
\newblock In \emph{{Findings of EMNLP}}.

\bibitem[Ryan and Deci(2000)]{{ryan2000self}}
Ryan, Richard M. and Edward L. Deci. 2000.
\newblock Self-determination theory and the facilitation of intrinsic motivation, social development, and well-being.
\newblock \emph{{American Psychologist}}, 55(1):68--78.

\bibitem[Tack and Piech(2022)]{{tack2022teacher}}
Tack, Anais and Chris Piech. 2022.
\newblock The AI Teacher Test: Measuring the pedagogical ability of Blender and GPT-3 in educational dialogues.
\newblock In \emph{{Proceedings of EDM}}.

\bibitem[VanLehn(2011)]{{vanlehn2011relative}}
VanLehn, Kurt. 2011.
\newblock The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems.
\newblock \emph{{Educational Psychologist}}, 46(4):197--221.

\bibitem[Vygotsky(1978)]{{vygotsky1978mind}}
Vygotsky, Lev S. 1978.
\newblock \emph{{Mind in Society: The Development of Higher Psychological Processes}}.
\newblock Harvard University Press.

\bibitem[Wood et~al.(1976)]{{wood1976role}}
Wood, David, Jerome S. Bruner, and Gail Ross. 1976.
\newblock The role of tutoring in problem solving.
\newblock \emph{{Journal of Child Psychology and Psychiatry}}, 17(2):89--100.

\bibitem[Wu et~al.(2023)]{{wu2023autogen}}
Wu, Qingyun, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, and others. 2023.
\newblock AutoGen: Enabling next-gen LLM applications via multi-agent conversation.
\newblock \emph{{arXiv preprint arXiv:2308.08155}}.
\end{{thebibliography}}
\end{{document}}
""".strip() + "\n"

    (OUT / "main.tex").write_text(tex, encoding="utf-8")
    (OUT / "custom.bib").write_text(textwrap.dedent(r"""
        @book{vygotsky1978mind,
          title={Mind in Society: The Development of Higher Psychological Processes},
          author={Vygotsky, Lev S.},
          year={1978},
          publisher={Harvard University Press}
        }
        @article{wood1976role,
          title={The role of tutoring in problem solving},
          author={Wood, David and Bruner, Jerome S. and Ross, Gail},
          journal={Journal of Child Psychology and Psychiatry},
          volume={17},
          number={2},
          pages={89--100},
          year={1976}
        }
        @incollection{koedinger2006cognitive,
          title={Cognitive tutors: Technology bringing learning science to the classroom},
          author={Koedinger, Kenneth R. and Corbett, Albert T.},
          booktitle={The Cambridge Handbook of the Learning Sciences},
          pages={61--78},
          year={2006},
          publisher={Cambridge University Press}
        }
        @article{vanlehn2011relative,
          title={The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems},
          author={VanLehn, Kurt},
          journal={Educational Psychologist},
          volume={46},
          number={4},
          pages={197--221},
          year={2011}
        }
        @inproceedings{tack2022teacher,
          title={The AI Teacher Test: Measuring the pedagogical ability of Blender and GPT-3 in educational dialogues},
          author={Tack, Ana{\"i}s and Piech, Chris},
          booktitle={Proceedings of the 15th International Conference on Educational Data Mining},
          year={2022}
        }
        @inproceedings{macina2023mathdial,
          title={MathDial: A dialogue tutoring dataset with rich pedagogical properties grounded in math reasoning problems},
          author={Macina, Jakub and Daheim, Nico and Srivastava, Saurabh and Mondorf, Philipp and Markert, Katja and Sachan, Mrinmaya and Lapata, Mirella},
          booktitle={Findings of EMNLP},
          year={2023}
        }
        @article{ryan2000self,
          title={Self-determination theory and the facilitation of intrinsic motivation, social development, and well-being},
          author={Ryan, Richard M. and Deci, Edward L.},
          journal={American Psychologist},
          volume={55},
          number={1},
          pages={68--78},
          year={2000}
        }
        @article{wu2023autogen,
          title={AutoGen: Enabling next-gen LLM applications via multi-agent conversation},
          author={Wu, Qingyun and Bansal, Gagan and Zhang, Jieyu and Wu, Yiran and Li, Beibin and Zhu, Erkang and others},
          journal={arXiv preprint arXiv:2308.08155},
          year={2023}
        }
    """).strip() + "\n", encoding="utf-8")

    (OUT / "README_OVERLEAF.md").write_text(textwrap.dedent("""
        # GPS-Agent LaTeX Project

        Upload this whole folder or `GPS_Agent_Overleaf.zip` to Overleaf/Prism.

        Main file: `main.tex`

        Notes:
        - The project includes a small local `acl.sty` and `acl_natbib.bst` fallback so it compiles immediately.
        - For official paper submission, replace these two files with the official ACL style files from https://github.com/acl-org/acl-style-files.
        - The paper is written as a conservative system/evaluation paper: primary claims are direct-answer leakage and phase validity, not long-term learning gain.
        - Tables in `tables/` are regenerated by `PYTHONPATH=. python scripts/run_optimized_pipeline.py` from the root repo.
        - Figures in `figures/` are generated from the current CSV logs.
        """).strip() + "\n", encoding="utf-8")

    (OUT / "latexmkrc").write_text("$pdf_mode = 1;\n$pdflatex = 'pdflatex -interaction=nonstopmode %O %S';\n", encoding="utf-8")
    (OUT / "Makefile").write_text("pdf:\n\tlatexmk -pdf main.tex\nclean:\n\tlatexmk -C\n", encoding="utf-8")


def compile_pdf() -> bool:
    try:
        result = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"], cwd=OUT, capture_output=True, text=True, timeout=120)
        (OUT / "compile.log").write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
        return (OUT / "main.pdf").exists()
    except Exception as exc:
        (OUT / "compile.log").write_text(str(exc), encoding="utf-8")
        return False


def zip_project() -> Path:
    zip_path = ROOT / "GPS_Agent_Overleaf.zip"
    if zip_path.exists():
        zip_path.unlink()
    keep_suffixes = {".tex", ".bib", ".bst", ".sty", ".md", ".png", ".csv", ".pdf", ""}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in OUT.rglob("*"):
            if path.is_file() and not any(part.startswith(".") for part in path.relative_to(OUT).parts):
                if path.suffix in keep_suffixes and path.name not in {"main.aux", "main.bbl", "main.blg", "main.fdb_latexmk", "main.fls", "main.log", "main.out"}:
                    zf.write(path, path.relative_to(OUT.parent))
    return zip_path


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    write_files()
    compile_pdf()
    zip_path = zip_project()
    print(f"Built LaTeX project: {OUT}")
    print(f"Built zip: {zip_path}")


if __name__ == "__main__":
    main()
