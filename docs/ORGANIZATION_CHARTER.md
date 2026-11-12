# Organization charter

## Mission
Build and operate a reusable organization of specialized AI agents that collaborates to deliver verified project outcomes.

## Operating model
- The Orchestrator owns project plans, task assignment, dependencies, run state, budgets, and escalation.
- Specialist agents own bounded areas of expertise and may communicate directly through the governed message bus.
- Shared project services provide artifact references, memory, tools, and execution workspaces.
- Policy enforcement applies to every tool call and external side effect, regardless of which agent initiated it.
- Human operators define goals, grant permissions, resolve ambiguity, and approve consequential actions.

Direct agent communication is not unrestricted peer access. The message bus authenticates senders, checks recipient and project scope, validates message types, and records audit events.

## Initial roles
| Role | Responsibility |
|---|---|
| CEO / Mission Agent | Converts user intent into measurable outcomes |
| Orchestrator | Plans, schedules, tracks dependencies, retries, and escalates |
| Product Agent | Requirements, user stories, acceptance criteria |
| Research Agent | Evidence gathering and synthesis |
| Architect Agent | System design and technical decisions |
| Developer Agents | Bounded code implementation |
| Data / AI Agent | Data pipelines, model integration, evaluation |
| Security Agent | Threat modeling and security review |
| QA Agent | Tests and defect reports |
| Independent Reviewer | Reviews deliverables against acceptance criteria |

The first runtime should implement only a small number of roles. Add roles only when they have distinct tools, contracts, tests, and measurable responsibilities.

## Example teams
Engineering: Product → Research → Architecture → Development → QA → Independent Review → Human acceptance.

YouTube: Strategy → Topic research → Script → Visual/audio production → Editing → Metadata → Compliance review → Approval → Authorized publishing → Analytics.

## Accountability
Every task has one accountable owner. Agents report evidence, artifact references, assumptions, and blockers. Agents cannot grant themselves permissions. Reviewers should not be the sole authors of reviewed artifacts. The system records contributing agents, model/provider, skill versions, tools, and artifacts.
