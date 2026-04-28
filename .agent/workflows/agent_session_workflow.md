# Agent Session Workflow (Beads-driven)

// turbo-all

This workflow defines the mandatory steps an agent must follow at the start, during, and end of every work session in this project.

## Phase 1: Session Initialization (Startup)

1. **Read Core Instructions**: Always read [AGENTS.md](file:///home/chinh303/code/gpsaiedu/GPS_AIedu/AGENTS.md) first to check for any updated rules.
2. **Prime Context**: Run `bd prime` to load the latest issue tracking context and rules.
3. **Identify Work**: Run `bd ready` to find unblocked tasks.
4. **Knowledge Retrieval**: Run `bd memories` (or search for specific keywords) to see if there are any recent insights or "gotchas" from previous sessions.

## Phase 2: Task Execution

1. **Review Task**: Run `bd show <id>` to understand requirements, acceptance criteria, and design decisions.
2. **Claim Task**: Mark the task as in-progress and claim it:
   ```bash
   bd update <id> --claim --status=in_progress
   ```
3. **Decompose (Optional)**: If the task is large, use `bd create` to create sub-tasks and `bd dep add` to link them.
4. **Implement**: 
   - Follow the G.P.S. (Guide-Practice-Solve) scaffolding if applicable.
   - Use `bd remember "Insight description"` to record any non-obvious logic or bugs found.
5. **Quality Check**: Run tests and linters before closing.

## Phase 3: Session Completion (MANDATORY)

**NEVER end a session without these steps.**

1. **Close Completed Tasks**:
   ```bash
   bd close <id1> <id2> ...
   ```
2. **Document Handover**: If work is incomplete, create follow-up issues using `bd create` and link them to the current task.
3. **Sync Beads Data**:
   ```bash
   bd dolt push
   ```
4. **Code Submission**:
   ```bash
   git pull --rebase
   git add .
   git commit -m "feat/fix/refactor: brief description of changes"
   git push
   ```
5. **Final Status**: Run `git status` to ensure everything is up to date with origin.

---
*Note: This workflow is managed by the beads issue tracker. Use `bd` commands for all state changes.*
