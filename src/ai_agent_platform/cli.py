"""Command-line entry point for the local AI Agent Platform."""

import argparse
import sys
from collections.abc import Sequence

from ai_agent_platform.application import build_application
from ai_agent_platform.core.errors import AgentPlatformError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-agent",
        description="Run a configured agent on one task.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", help="run one agent task")
    run_parser.add_argument(
        "--agent",
        default="examples/agents/researcher.json",
        help="path to the agent JSON manifest",
    )
    run_parser.add_argument(
        "--task",
        required=True,
        help="task to send to the agent",
    )
    run_parser.add_argument(
        "--database",
        default="data/agent_platform.sqlite3",
        help="SQLite execution-history database path",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = _build_parser().parse_args(argv)

    if args.command == "run":
        try:
            application = build_application(
                agent_path=args.agent,
                database_path=args.database,
            )
            response = application.run(args.task)
        except AgentPlatformError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2

        print(f"Agent: {response.agent_id}")
        print(f"Provider: {response.provider}")
        print(f"Status: {response.status}")
        print(f"Execution ID: {response.execution_id}")
        print("\n--- Agent output ---")
        print(response.output)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
