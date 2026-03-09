"""
main.py — Entry point for the Workload Logger application.

Usage:
    python main.py                              # start session interactively
    python main.py --tray                       # start minimized to system tray
    python main.py --setup                      # register Windows auto-start
    python main.py --participant "Name"         # specify participant ID
    python main.py --task-type "writing"        # specify task type
"""

import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Workload Logger")
    parser.add_argument("--participant", type=str, default="default",
                        help="Participant identifier")
    parser.add_argument("--task-type", type=str, default="free",
                        choices=["free", "typing", "composing", "writing", "qa"],
                        help="Type of task being performed")
    parser.add_argument("--task-name", type=str, default="",
                        help="Optional descriptive task name")
    parser.add_argument("--tray", action="store_true",
                        help="Run minimized to system tray (background mode)")
    parser.add_argument("--setup", action="store_true",
                        help="Register program in Windows auto-start and exit")
    return parser.parse_args()


def run_setup() -> None:
    """Register the program in Windows Task Scheduler for auto-start on login."""
    # TODO: implement in logger/power_manager.py → register_autostart()
    raise NotImplementedError


def run_tray_mode(args: argparse.Namespace) -> None:
    """Start the logger as a background process with a system tray icon."""
    # TODO: wire SessionManager + TrayApp + PowerManager
    raise NotImplementedError


def run_interactive(args: argparse.Namespace) -> None:
    """Start a single foreground session, then show the TLX survey."""
    # TODO: wire EventLogger → WindowAggregator → SessionAggregator → NasaTLXSurvey
    raise NotImplementedError


def main() -> None:
    args = parse_args()

    if args.setup:
        run_setup()
        sys.exit(0)

    if args.tray:
        run_tray_mode(args)
    else:
        run_interactive(args)


if __name__ == "__main__":
    main()
