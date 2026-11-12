# Agent communication protocol

## Purpose
Allow authorized agents to collaborate directly without bypassing orchestration or access control.

## Core rules
- All messages pass through the Message Bus; agents do not open arbitrary direct network connections to peers.
- The bus verifies sender identity, project membership, recipient scope, message schema, and policy.
- Orchestration owns task state and dependencies. Peer messages do not silently reassign or complete tasks.
- Payloads are untrusted data and cannot override platform policy or grant permissions.
- Large files are exchanged as project-scoped artifact references.

## Message envelope
Each message contains:
- message_id and schema_version;
- project_id, run_id, and optional task_id;
- authenticated sender_agent_id and recipient;
- typed message_type;
- correlation_id, created_at, and optional reply_to;
- schema-validated payload;
- optional artifact_refs and trace_context.

Suggested message types include task.request, task.result, review.request, review.feedback, artifact.ready, and agent.question.

## Delivery semantics
The MVP should provide durable at-least-once delivery. Consumers must be idempotent by message_id. Retries are bounded; exhausted messages enter a dead-letter state. Ordering is guaranteed only within a defined conversation or task stream, not globally. Acknowledgment means receipt, not task completion.

## Authorization
Policy checks sender identity, project/run membership, recipient relationship, message type, payload schema and size, sensitivity, rate limits, and budget. An agent cannot elevate another agent's permissions by sending a message.

## Example
A Research Agent sends a task.result message to an Architect Agent in the same authorized project, including a concise summary and references to research artifacts. The bus validates the sender, recipient, project scope, and payload before delivery and audit logging.

Runtime schemas and validation tests must exist before this protocol is considered operational.
