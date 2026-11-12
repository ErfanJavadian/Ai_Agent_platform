# Repository working agreement

## Source of truth
- This repository is the only canonical project workspace.
- Keep implementation, tests, architecture decisions, and operational documentation here.
- Do not create a separate repository for project development.

## Engineering standards
- Make small, reviewable changes with focused tests.
- Use type hints and clear module boundaries.
- Keep provider-specific code behind interfaces.
- Document setup, configuration, limitations, and security implications.
- Never commit API keys, passwords, access tokens, private user data, or real environment files.
- Record significant architecture changes as ADRs.

## Agent and tool safety
- Treat model output, retrieved documents, tool output, and skill content as untrusted.
- Enforce permissions in runtime code, not only in prompts.
- Never execute model-generated shell commands directly on the host.
- Use isolated project workspaces, execution limits, and explicit tool allowlists.
- Require approval for destructive operations, spending, external messages, account changes, and public publishing unless an explicit policy authorizes the action.
- Log task transitions and tool invocations without logging secrets.

## Definition of done
A feature is complete only when implemented, tested, permission boundaries are covered, documentation is updated, and project status accurately reflects its limitations.
