#!/usr/bin/env -S uv run python
import sys
import os

# Add project root to path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Handle bitmango package mapping if needed (for standalone)
if "bitmango" not in sys.modules:
    import importlib.util
    # Try to find bitmango-cli
    for p in [os.path.join(base_dir, "bitmango-free", "bitmango-cli"), os.path.join(base_dir, "bitmango-cli")]:
        if os.path.exists(os.path.join(p, "__init__.py")):
            spec = importlib.util.spec_from_file_location("bitmango", os.path.join(p, "__init__.py"))
            bitmango = importlib.util.module_from_spec(spec)
            sys.modules["bitmango"] = bitmango
            spec.loader.exec_module(bitmango)
            if os.path.dirname(p) not in sys.path:
                sys.path.insert(0, os.path.dirname(p))
            break

def main():
    try:
        from bitmango.tutorial_engine import run_help
        
        print("\n" + "="*80)
        print("BitMango Trade CLI - Professional Live Demo".center(80))
        print("="*80 + "\n")

        # Core high-impact flow for the README animation
        flow = [
            "entry",
            "account",
            "stop",
            "risk",
            "report"
        ]

        for cmd_to_help in flow:
            run_help(cmd_to_help)

        print("\n" + "="*80)
        print("Walkthrough Complete - Hardened, Reliable, Professional".center(80))
        print("="*80 + "\n")

    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during walkthrough: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
