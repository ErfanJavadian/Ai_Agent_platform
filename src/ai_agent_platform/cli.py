"""Command-line entry point for the local AI Agent Platform."""

import argparse
import sys
from collections.abc import Sequence

from ai_agent_platform.agents.loader import load_agent
from ai_agent_platform.application import build_application
from ai_agent_platform.chat import run_chat
from ai_agent_platform.core.errors import AgentPlatformError
from ai_agent_platform.providers.factory import create_provider


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-agent",
        description="Run an agent task or start an interactive personal chat.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    run_parser = commands.add_parser("run", help="run one agent task")
    run_parser.add_argument("--agent", default="examples/agents/researcher.json",
                            help="path to the agent JSON manifest")
    run_parser.add_argument("--task", required=True, help="task to send to the agent")
    run_parser.add_argument("--database", default="data/agent_platform.sqlite3",
                            help="SQLite execution-history database path")

    chat_parser = commands.add_parser("chat", help="start an interactive conversation")
    chat_parser.add_argument(
        "--agent",
        default="examples/agents/erfan_personal_assistant.json",
        help="path to the chat assistant JSON manifest",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = _build_parser().parse_args(argv)

    try:
        if args.command == "chat":
            agent = load_agent(args.agent)
            provider = create_provider()
            run_chat(provider, agent)
            return 0

        if args.command == "run":
            application = build_application(
                agent_path=args.agent,
                database_path=args.database,
            )
            response = application.run(args.task)
            print(f"Agent: {response.agent_id}")
            print(f"Provider: {response.provider}")
            print(f"Status: {response.status}")
            print(f"Execution ID: {response.execution_id}")
            print("\n--- Agent output ---")
            print(response.output)
            return 0
    except AgentPlatformError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
