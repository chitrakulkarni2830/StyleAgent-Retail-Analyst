"""
=============================================================
scraper/trend_scraper.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This is a standalone script you can run from the terminal
  to fetch the latest 2026 fashion trends and save them to:
    outputs/trend_brief.json

  It is a thin wrapper around the TrendScoutAgent class
  (which lives in agents/trend_scout_agent.py). That agent
  does all the real scraping work — this file just:
    1. Imports and runs it
    2. Prints the result nicely in the terminal

HOW TO RUN (from the project root folder):
  python scraper/trend_scraper.py

OUTPUT:
  - Prints a formatted trend summary to the terminal
  - Saves full data to outputs/trend_brief.json
=============================================================
"""

import os    # built-in: for file path handling
import sys   # built-in: for modifying the Python module search path
import json  # built-in: for printing the JSON output nicely

# ── Make sure Python can find our agents/ folder ──────────────
# When you run this from the command line, Python needs to know where
# the agents/ folder is. This adds the project root to the search path.
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))  # e.g. .../scraper/
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)                  # one level up = project root

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)  # add project root so imports work

# ── Import the TrendScoutAgent from the agents folder ──────────
from agents.trend_scout_agent import TrendScoutAgent  # Agent 1


def run_trend_scraper():
    """
    Runs the TrendScoutAgent and prints the results to the terminal.
    The agent handles all the scraping and fallback logic internally.
    """
    print("\n" + "=" * 55)
    print("  🌐 Style Agent — Trend Scraper")
    print("=" * 55)
    print("  Attempting to scrape 2026 fashion trends...")
    print("  Sources: Vogue India, NYKAA Blog, Elle India")
    print("  Fallback: Built-in 2026 Spring-Summer trend data\n")

    # Create an instance of the Trend Scout Agent
    scout = TrendScoutAgent()

    # Run it — this either fetches live data or uses fallback data
    trend_data = scout.run()  # returns a dictionary of trend info

    # ── Print a human-friendly summary ────────────────────────
    print("\n" + "─" * 55)
    print(f"  📅  Season:  {trend_data.get('season', 'Spring-Summer 2026')}")
    print(f"  📡  Source:  {trend_data.get('source', 'fallback')}")
    print(f"  🗓️   Fetched: {trend_data.get('fetch_date', 'today')}")

    print("\n  🎨  TRENDING COLOURS:")
    for colour in trend_data.get("trending_colours", []):
        # Print the colour name, HEX code, and a brief description
        name = colour.get("name", "Unknown")
        hex_code = colour.get("hex", "#000")
        desc = colour.get("description", "")
        print(f"    • {name:15s}  {hex_code}  — {desc}")

    print("\n  👗  TRENDING OUTFITS:")
    for outfit in trend_data.get("trending_outfits", []):
        print(f"    • {outfit}")

    print("\n  💎  TRENDING JEWELLERY:")
    for jewellery in trend_data.get("trending_jewellery", []):
        print(f"    • {jewellery}")

    print("\n  ✨  TRENDING VIBES:")
    for vibe in trend_data.get("trending_vibes", []):
        print(f"    • {vibe}")

    # ── Show the file path where data was saved ────────────────
    output_path = os.path.join(PROJECT_ROOT, "outputs", "trend_brief.json")
    print(f"\n  💾  Full data saved to: {output_path}")
    print("─" * 55 + "\n")

    return trend_data  # return the dict in case this function is called from another file


# =============================================================
# MAIN — runs when you type: python scraper/trend_scraper.py
# =============================================================
if __name__ == "__main__":
    # This block only runs when the script is called directly
    # (not when it is imported as a module by another file)
    run_trend_scraper()
    print("  ✅ Trend scraper finished.\n")
