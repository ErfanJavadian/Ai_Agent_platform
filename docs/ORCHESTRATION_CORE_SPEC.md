# Orchestration core specification

## Responsibilities
The Orchestrator is the control plane for project execution. It plans and coordinates work but does not need to proxy every peer conversation.

It must accept goals and constraints; create reviewable plans; resolve agents, skills, tools, and policies; create tasks with owners and dependencies; dispatch ready tasks; track state, attempts, deadlines, and budgets; support pause, resume, cancel, and escalation; collect artifacts and outcomes; trigger QA and review; and close runs with a verifiable report.

## Task state machine
Allowed states: draft, ready, queued, running, blocked, waiting_approval, succeeded, failed, cancelled.

Transitions must be explicit and validated. Terminal states are succeeded, failed, and cancelled. A blocked task includes a reason and resolution condition.

## Task record
Minimum fields: task, project, and run IDs; bounded title and description; accountable agent; input artifacts; dependency IDs; required skills and tools; permission and approval requirements; state and attempt count; timestamps; output artifact references; result summary, errors, and evaluation status.

## Scheduling and retries
Only tasks with satisfied dependencies and valid permissions are runnable. Retry only transient failures with bounded attempts and backoff. Do not retry non-idempotent external actions without an idempotency strategy. Preserve failed attempts. Detect dependency cycles. Enforce concurrency and usage budgets.

## Collaboration
Agents exchange requests, questions, results, and review feedback through the message bus. The Orchestrator remains authoritative for task assignment, state, dependencies, and cancellation. Shared artifacts are referenced through the artifact service.

## Human approval gates
Require approval for public publishing, audience messaging, spending, account or permission changes, destructive operations, and production deployment. Approval is scoped to a specific action and expires if the action materially changes.

## MVP acceptance criteria
- Create a run containing at least two dependent tasks.
- Dispatch a ready task and persist its state.
- Allow two authorized agents to exchange a typed message.
- Reject unauthorized messages and tool calls.
- Persist outcomes and artifact references.
- Pause and resume without losing state.
- Test state transitions and dependency handling deterministically.
