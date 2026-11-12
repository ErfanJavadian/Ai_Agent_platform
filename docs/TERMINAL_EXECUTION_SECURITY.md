# Terminal and code execution security

## Objective
Give agents coding and command-line capabilities without allowing model-generated commands unrestricted access to the platform host.

## Required architecture
Agent → Tool Gateway → Policy Check → Execution Service → Isolated Project Workspace → Result and Artifact Store.

The agent runtime must never call a host shell directly. The execution service is a separate trust boundary.

## Workspace isolation
A project workspace must not expose platform host files, other projects, user home directories, environment secrets by default, container runtime sockets, cloud metadata endpoints, privileged devices, or host process namespaces.

## Execution controls
- Command and executable allowlists where practical.
- Explicit working directory and wall-clock timeout.
- CPU, memory, process-count, and disk quotas.
- Bounded stdout and stderr capture.
- Network disabled by default; explicit egress policy when needed.
- Non-root execution and controlled writable workspace.
- Dependency and artifact scanning.
- Cleanup of ephemeral environments.
- Audit records for actor, command, policy decision, duration, and exit status.

## Approval policy
Require human approval for privileged commands, network access beyond policy, credential use, destructive operations, deployment, and external side effects. Approval cannot be inferred from an agent message.

## MVP strategy
Start with a local adapter that runs only in a genuine isolated container or equivalent sandbox. If a secure sandbox is unavailable, disable arbitrary shell execution and expose only narrowly scoped deterministic tools. Never fall back to unrestricted host execution.

## YouTube workflow example
A future YouTube agent may use the execution service for approved media-processing scripts, caption processing, conversion, and packaging. It must enforce licensing and rights for audio, footage, images, and fonts. Uploading or publishing requires authorized channel access and approval.
