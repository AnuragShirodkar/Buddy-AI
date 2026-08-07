from __future__ import annotations

import argparse
import json
import logging
import sys

from .config import load_settings
from .policy import FinderRobot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ESP AI Finder Robot CLI")
    parser.add_argument("text", nargs="*", help="Command text, e.g. Find my keys")
    parser.add_argument("--status", action="store_true", help="Print last status and exit")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    robot = FinderRobot(load_settings())

    if args.status:
        print(json.dumps({"state": robot.status.state.value, "message": robot.status.message}))
        return 0

    text = " ".join(args.text).strip()
    if not text:
        parser.print_help()
        return 2

    result = robot.handle_command(text)
    # For find missions, wait until thread finishes
    if robot._thread and robot._thread.is_alive():
        robot._thread.join()
        result = robot.status

    print(
        json.dumps(
            {
                "state": result.state.value,
                "goal": result.goal,
                "message": result.message,
                "last_vision": result.last_vision,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
