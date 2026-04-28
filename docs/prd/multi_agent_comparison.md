# PRD: Comparative Study of Single-Agent vs Multi-Agent GPS Architectures

## Problem Statement
The current Single-Agent GPS implementation combines intent classification and pedagogical execution within shared LangGraph nodes. This coupling can lead to "Cognitive Overload" in the LLM, manifesting as repetitive loops, language drift (hallucinations), or incorrect state transitions during complex mathematical reasoning tasks (e.g., Question 43). This limits the scalability and precision of the pedagogical interventions required for a high-quality research study.

## Solution
Implement a **Multi-Agent Supervisor** architecture using LangGraph to decouple **Intent Classification** from **Pedagogical Execution**. 
- **Intent Agent:** Specialized in identifying the student's current state and required GPS tag (G, P, S).
- **Pedagogy Agent:** Specialized in generating high-quality mathematical guidance based on the assigned tag.
- **Supervisor Agent:** Orchestrates the flow and manages context.

A rigorous A/B test will be performed by running both architectures against the same 45-question bank and 5 student personas to measure improvements in fidelity, resilience, and efficiency.

## User Stories
1. **As a researcher**, I want to see a side-by-side comparison of Intent Accuracy to prove the Multi-Agent system is more precise.
2. **As a researcher**, I want to measure the "Stuck Rate" (sessions reaching 20 turns) to see if Multi-Agent is more resilient.
3. **As a developer**, I want to optimize the Intent Agent's prompt separately from the Pedagogy Agent to improve performance without affecting tone.
4. **As an analyst**, I want to compare the token usage efficiency vs. pedagogical quality trade-off.
5. **As a conference presenter**, I want statistical proof (p-values) that Multi-Agent GPS is superior for complex scaffolding.
6. **As a student**, I want a tutor that understands my specific confusion better due to dedicated intent analysis.

## Implementation Decisions
- **Framework:** LangGraph (Supervisor Pattern).
- **Modules to build:**
    - `src/ai/multi_agent_gps.py`: The new graph implementation.
    - `src/analysis/architecture_comparison.py`: The evaluation harness.
- **State Management:** Unified `AgentState` shared across specialized agents.
- **LLM Strategy:** Use the same `qwen2.5:7b` for both to ensure a fair "Architecture-only" comparison.

## Testing Decisions
- **Fidelity Check:** Random sampling of 50 turns to verify GPS tag accuracy.
- **Resilience Check:** Stress test on "Hard" questions (Q31-Q45) to monitor loop occurrences.
- **Performance:** Tracking of response latency (Multi-agent is expected to be slower but better).

## Out of Scope
- Comparison with non-GPS (Control) groups.
- Changes to the React frontend UI.
- Switching to external API models (staying with local Ollama).
