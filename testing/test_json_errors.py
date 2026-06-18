import subprocess
import json
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from test_helper import get_bitmango_executable

def run_cli(args):
    """Runs the CLI with given args and returns (stdout, stderr, returncode)."""
    full_cmd = get_bitmango_executable() + args + ["-o", "json"]
    # Ensure uv run is used if bitmango has that shebang, 
    # but subprocess.run with the script path usually respects shebang.
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def test_scenario(name, args, expected_error_substring=None):
    """Runs a test scenario and asserts JSON error output."""
    print(f"Running Test: {name}...", end=" ", flush=True)
    stdout, stderr, code = run_cli(args)
    
    # 1. Check exit code
    if code == 0:
        print("FAIL (Exit code 0)")
        print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
        sys.exit(1)
    
    # 2. Check if stdout is valid JSON
    try:
        # The output might contain logs if verbose is on or by default in some builds.
        # We find the first '{' and last '}' to extract the JSON object.
        start = stdout.find('{')
        end = stdout.rfind('}') + 1
        if start == -1 or end == 0:
            print(f"\nDEBUG: RAW STDOUT: {repr(stdout)}")
            print(f"DEBUG: RAW STDERR: {repr(stderr)}")
            raise ValueError("No JSON object found")
        json_str = stdout[start:end]
        data = json.loads(json_str)
    except Exception as e:
        print(f"FAIL (Invalid JSON: {e}. Raw: '{stdout[:100]}...')")
        sys.exit(1)
    
    # 3. Check for 'error' key
    if "error" not in data:
        print("FAIL (No 'error' key in JSON)")
        print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
        sys.exit(1)
    
    # 4. Check error message content if requested
    if expected_error_substring and expected_error_substring.lower() not in data["error"].lower():
        print(f"FAIL (Error '{data['error']}' does not contain '{expected_error_substring}')")
        print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
        sys.exit(1)
    
    # 5. Check for stdout purity (should not have extra text before/after JSON)
    serialized = json.dumps(data, indent=2)
    if stdout.strip() != serialized:
        # Note: indent=2 might differ from CLI output if CLI uses different spacing,
        # but our CLI uses indent=2. Let's be safe and just check if it's longer.
        if len(stdout.strip()) > len(serialized) + 2: # small buffer for varying line endings
             print(f"FAIL (Stdout contains non-JSON noise)")
             print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
             sys.exit(1)

    print("PASS ✓")
    return True

def main():
    scenarios = [
        ("Missing Exchange", ["account", "--balance"], "exchange is required"),
        ("Invalid Exchange", ["account", "--balance", "--exchange", "nonexistent"], "No specific error handler found"),
        ("Invalid Command", ["nonexistent-command", "--exchange", "simulated"], "Invalid arguments or command"),
        ("Invalid Pair (Phemex)", ["ticker", "--exchange", "phemex", "--pair", "INVALID-PAIR"], "does not have market symbol"),
        ("Auth Failure (Phemex Dummy)", ["account", "--balance", "--exchange", "phemex"], "api_keys"),
        ("Unsupported Command (Simulated)", ["ticker", "--exchange", "simulated", "--invalid-param"], "Invalid arguments or command"),
    ]
    
    passed = 0
    for name, args, error in scenarios:
        if test_scenario(name, args, error):
            passed += 1
            
    print(f"\nSummary: {passed}/{len(scenarios)} tests passed.")
    if passed < len(scenarios):
        sys.exit(1)

if __name__ == "__main__":
    main()
