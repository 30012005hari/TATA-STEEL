# Shared Agent Instructions

This workspace may be used by more than one coding agent at the same time,
including Codex and Antigravity. Direct agent-to-agent messaging is not
available, so use the workspace files below as the shared communication layer.

## Required Coordination

Before editing any file:

1. Read `AGENT_COORDINATION.md`.
2. Check whether another agent has marked the target file as actively edited.
3. Update your section in `AGENT_COORDINATION.md` with your task and intended files.

While working:

- Keep edits scoped to your current task.
- Do not overwrite, revert, or delete work from the user or another agent.
- If you must edit a file another agent marked as active, write a note in
  `AGENT_COORDINATION.md` first and explain why.
- Update `AGENT_COORDINATION.md` after meaningful progress, tests, blockers, or
  handoff notes.

After finishing:

- Mark your active files as complete.
- Record validation commands and results.
- Leave a short handoff note for the other agent.

## Shared Files

- `AGENT_COORDINATION.md`: live task status, active files, mailbox, and handoff.
- `AGENTS.md`: standing rules for all agents in this workspace.

## Conflict Rule

If two agents need the same file and the correct merge is unclear, pause and ask
the user instead of guessing.
