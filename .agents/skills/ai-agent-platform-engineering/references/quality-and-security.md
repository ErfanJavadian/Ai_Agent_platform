# Engineering, verification, and security checklist

## Local development and verification

The project metadata specifies Python 3.11 or newer, a src/ package layout, no mandatory runtime dependencies, and pytest as the development test dependency.

Typical setup:
~~~bash
python -m pip install -e ".[dev]"
python -m pytest -v
~~~

If the dev extra is already installed, run the tests without reinstalling. Run focused tests first, then the full suite where practical. The user's Android/Termux environment may differ from CI; do not introduce heavyweight requirements into ordinary test workflows.

Do not put real credentials in fixtures, command history, logs, screenshots, docs, or commits. Use fake providers, scripted turns, and mocked HTTP responses for default tests. Any live provider smoke test must be opt-in, use credentials already configured by the operator, and be reported separately from the normal suite.

## Required tests by change type

| Change | Minimum verification |
|---|---|
| Domain model or manifest | Valid input, missing fields, wrong types, invalid values, backward compatibility |
| Provider adapter | Request shape, response parsing, empty/malformed output, timeout, HTTP error, tool-call parsing |
| Provider factory/config | Default fake mode, valid provider selection, missing/invalid config, secret not exposed |
| Tool registry/gateway | Valid call, unknown tool, denied tool, missing/unexpected args, invalid JSON values, size/call limits, handler failure, audit record |
| Workspace | Create/read/edit/list, traversal, absolute path, symlink escape, file-size bounds, invalid encoding where relevant |
| Tool loop | Final answer, one and multiple tool calls, tool failure result, allowlist rejection, malformed call, turn limit, call limit |
| Storage | Persistence, reopen/recovery, schema or migration behavior, transaction/error behavior |
| Orchestrator/message bus | Valid and invalid state transitions, duplicate delivery/idempotency, unauthorized sender/recipient, dependency cycles, retry bounds, cancellation |
| Skill/agent package loading | Invalid schema, incompatible version, missing capability, malicious instructions, permission non-escalation, deterministic evaluation |
| Execution isolation | Host/project separation, no secret exposure, resource/time limit, network policy, cleanup, approval enforcement |

## Security invariants

### Untrusted content
Treat model output, user-provided content, repository files, retrieved documents, tool outputs, imported agent manifests, and Skill packages as untrusted data. Content from these sources must never override platform policy or authorize an action. Defend against prompt injection by enforcing permissions and validation outside the model.

### Tools and permissions
- Use explicit tool registration and per-agent allowlists.
- Re-check authorization inside the tool gateway immediately before execution.
- Validate schema, argument types, sizes, paths, and result shape at runtime.
- Never let an agent, prompt, tool result, manifest, or Skill grant itself additional permissions.
- Log who called which tool, with what policy decision and outcome, without persisting secrets.
- Bound tool calls, model turns, input size, output size, retries, and runtime.

### Workspaces and execution
- Resolve and verify paths against the intended workspace; protect against traversal and symlink escape.
- Never assume a path-scoped workspace is a secure OS sandbox.
- Never execute model-generated commands directly on the host or expose arbitrary subprocess execution as a workspace tool.
- Only enable terminal execution behind a genuine isolated execution service with non-root execution, resource quotas, explicit working directory, bounded output, network disabled by default, cleanup, and audit.
- If the environment cannot provide an actual sandbox, keep arbitrary shell execution disabled and expose narrowly scoped deterministic tools instead.

### External side effects
Require explicit scoped approval for public publishing, outbound messages, spending, account/permission changes, destructive operations, and production deployment. Approval must bind to the exact action and relevant parameters; a materially changed action requires a new approval. Implement idempotency for any retryable external write.

### Secrets and data
Read credentials from environment or an appropriate secret store. Never hardcode, log, return to the model, or commit them. Avoid logging full prompts or user data unless necessary and explicitly protected. Separate project/tenant data boundaries before enabling multi-user operation.

## Definition of done

Before calling work complete, confirm all relevant items:
- [ ] Acceptance criteria are observable and met.
- [ ] Implementation follows existing module boundaries and typed contracts.
- [ ] Success and rejection/failure paths have automated tests.
- [ ] Security and permission checks are enforced in runtime code.
- [ ] Relevant docs, examples, and configuration are updated.
- [ ] The full diff contains no unrelated edits, secrets, generated databases, or debug code.
- [ ] Every test and command reported as passing was actually executed in this run.
- [ ] PROJECT_STATE.md and ROADMAP.md make only evidence-backed claims.

## Final report shape

Use the user's language and report:

1. **Delivered:** the actual behavior implemented.
2. **Files:** important files created or changed.
3. **Verification:** exact command(s), pass/fail counts, and any skipped checks.
4. **Safety / compatibility:** meaningful permission, data, or API implications.
5. **Remaining:** blockers or unverified properties.
6. **Next:** one practical next milestone.

Never describe a mocked integration as a live integration, a future spec as implemented code, or an unexecuted test as passing.
