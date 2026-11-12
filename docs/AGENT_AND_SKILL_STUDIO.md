# Agent and Skill Studio specification

## Goal
Let users create custom agents and attach, remove, configure, and version reusable skills without changing runtime source code for ordinary instruction-based skills.

## Agent definition
An agent definition includes stable ID, name, description, version, mission, bounded responsibilities, instructions, output contract, model settings, pinned skill versions, tool references, memory scope, permission profile, lifecycle status, and evaluation suite. Provider credentials are stored separately from definitions.

## Skill package
A versioned skill package may contain:
- SKILL.md: human-readable instructions.
- manifest.yaml: ID, version, description, compatibility, inputs, outputs, and required capabilities.
- Optional references, examples, and evaluation cases.

A skill is not merely an arbitrary prompt. Executable code must not run just because a skill is installed. Code-backed skills require explicit tool declarations, review, sandbox execution, and permission checks.

## Skill lifecycle
Author or import → validate manifest and package → scan unsafe content → check compatibility → resolve tool requirements → evaluate in restricted environment → activate a pinned version → track updates and support rollback.

## Compatibility
Check input/output schemas, model/context requirements, tool availability and permission, platform API version, memory requirements, and conflicts with installed skills.

A skill must never grant permissions. Permissions are assigned by the platform and project owner independently of skill content.

## Custom agent flow
Create → configure → attach skills → select tools → assign permissions → validate → test → activate.

## Future catalog
A future catalog may support private, organization-shared, and public skills. Publisher identity, integrity checks, version pinning, trust labels, and user review are required for third-party packages.
