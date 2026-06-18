#!/usr/bin/env -S uv run python
import json
import os
import sys
from datetime import datetime

# Set up project path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WIKI_DIR = os.path.join(PROJECT_ROOT, "docs", "wiki")

def generate_report():
    results_file = os.path.join(PROJECT_ROOT, "testing", "verification_results.json")
    if not os.path.exists(results_file):
        print(f"Error: Results file {results_file} not found.")
        return

    with open(results_file, "r") as f:
        data = json.load(f)

    results = data.get("results", {})
    date_str = data.get("date", datetime.now().isoformat())

    # 1. Create/Update Implementation Roadmap Parent Page
    roadmap_page_path = os.path.join(WIKI_DIR, "09-Implementation-Roadmap.md")
    with open(roadmap_page_path, "w") as f:
        f.write("# Implementation Roadmap\n\n")
        f.write(f"**Last Status Update:** {date_str}\n\n")
        f.write("This roadmap tracks the implementation progress and verification status of all supported exchanges.\n\n")
        f.write("| Exchange | Sandbox Status | Live Status | Detailed Results |\n")
        f.write("|----------|----------------|-------------|------------------|\n")
        
        for exchange in sorted(results.keys()):
            ex_data = results[exchange]
            
            # Handle old format if any
            if isinstance(ex_data, list):
                ex_data = {"sandbox": ex_data, "live": []}
            
            # Calculate summary status for both
            def get_summary(entries):
                if not entries: return "⚪ Pending", "⚪"
                pass_count = sum(1 for r in entries if r['status'] == "PASS")
                total_count = len(entries)
                icon = "🟢" if pass_count == total_count else "🟡" if pass_count > 0 else "🔴"
                return f"{icon} {pass_count}/{total_count}", icon

            sandbox_summary, s_icon = get_summary(ex_data.get("sandbox", []))
            live_summary, l_icon = get_summary(ex_data.get("live", []))
                
            f.write(f"| {exchange.upper()} | {sandbox_summary} | {live_summary} | [View Details](Exchange-Result-{exchange.capitalize()}) |\n")

    # 2. Create Individual Exchange Pages
    for exchange in results.keys():
        ex_page_name = f"Exchange-Result-{exchange.capitalize()}.md"
        ex_page_path = os.path.join(WIKI_DIR, ex_page_name)
        
        ex_data = results[exchange]
        if isinstance(ex_data, list):
            ex_data = {"sandbox": ex_data, "live": []}

        with open(ex_page_path, "w") as f:
            f.write(f"# Exchange Implementation Status: {exchange.upper()}\n\n")
            f.write(f"**Last Updated:** {date_str}\n\n")
            
            for env in ["sandbox", "live"]:
                f.write(f"## {env.capitalize()} Environment\n\n")
                entries = ex_data.get(env, [])
                if not entries:
                    f.write("*No data for this environment.*\n\n")
                    continue
                    
                f.write("| Feature | Sub-Feature | Status | Implementation Details |\n")
                f.write("|---------|-------------|--------|------------------------|\n")
                
                for r in entries:
                    status_icons = {"PASS": "✅ Verified", "FAIL": "❌ Error", "UNSUPPORTED": "🛠️ In Progress", "UNTESTED": "⚪ Pending"}
                    status_str = status_icons.get(r['status'], r['status'])
                    details = r['message']
                    if r['error'] and r['status'] == "FAIL":
                        details += f" (Error: {r['error']})"
                    
                    f.write(f"| {r['feature']} | {r['sub_feature']} | {status_str} | {details} |\n")
                f.write("\n")
            
            f.write("\n[Back to Roadmap](09-Implementation-Roadmap)\n")

    print(f"Wiki report generated in {WIKI_DIR}")

if __name__ == "__main__":
    generate_report()
