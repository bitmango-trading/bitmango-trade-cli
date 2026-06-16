#!/usr/bin/env -S uv run python
import sys
import os
import subprocess

# Add project root to path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

def main():
    try:
        print("\n" + "="*80)
        print("BitMango Trade CLI - Professional Live Demo".center(80))
        print("="*80 + "\n")

        # Core high-impact flow for the README animation
        # Since commentary is suppressed in README_DEMO mode, we can show more steps
        flow = [
            "entry",
            "account",
            "stop",
            "kill-switch",
            "report"
        ]

        help_script = os.path.join(base_dir, "bitmango-help")

        for cmd_to_help in flow:
            subprocess.run([sys.executable, help_script, cmd_to_help])

        print("\n" + "="*80)
        print("Walkthrough Complete - Hardened, Reliable, Professional".center(80))
        print("="*80 + "\n")

    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")

if __name__ == "__main__":
    main()
