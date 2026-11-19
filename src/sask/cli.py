"""Command line entry point. Subcommands are stubs until later milestones."""

from __future__ import annotations

import argparse
import sys

from sask import __version__

# name -> (help text, positional argument name or None)
COMMANDS: dict[str, tuple[str, str | None]] = {
    "scan": ("run all stages and write the report", "path"),
    "context": ("build context.json for a repo", "path"),
    "discover": ("run scanners and the agent pass", "run"),
    "validate": ("reproduce findings in the sandbox", "run"),
    "remediate": ("propose and re-test patches", "run"),
    "report": ("emit report.json and report.md", "run"),
    "apply": ("apply a proposed patch to the working tree", "finding_id"),
    "mcp": ("run the MCP server", None),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sask", description=__doc__)
    parser.add_argument("--version", action="version", version=f"sask {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    for name, (help_text, arg) in COMMANDS.items():
        p = sub.add_parser(name, help=help_text)
        if arg:
            p.add_argument(arg)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help(sys.stderr)
        return 2
    print(f"sask {args.command}: not implemented", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
