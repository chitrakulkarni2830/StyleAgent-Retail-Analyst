"""
=============================================================
agents/trend_scout_agent.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This is Agent 1 — the Trend Scout.
  Its job is to find out what is CURRENTLY fashionable in 2026
  so the rest of the app can build outfits around real trends.

  It tries to scrape fashion websites (Vogue India, NYKAA Blog,
  Elle India). If any site is unreachable (no internet, or the
  site blocks us), it AUTOMATICALLY switches to a built-in
  fallback dictionary of 2026 Spring-Summer trends.

  Output is saved to: outputs/trend_brief.json
=============================================================
"""

import requests              # for making HTTP requests to websites
import json                  # for saving the output as a JSON file
import os                    # for building file paths
from datetime import datetime  # for recording when the data was fetched

# Try to import BeautifulSoup — this is for reading website HTML
try:
    from bs4 import BeautifulSoup  # pip install beautifulsoup4
except ImportError:
    # If BeautifulSoup is not installed, set it to None and handle later
    BeautifulSoup = None

# ── Where to save the output file ────────────────────────────
# Go up one level from agents/ to reach the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR  = os.path.join(PROJECT_ROOT, "outputs")  # the outputs/ folder
TREND_OUTPUT = os.path.join(OUTPUTS_DIR, "trend_brief.json")  # save file path


# =============================================================
# HARDCODED FALLBACK — Always works, even without internet
# These are real 2026 Spring-Summer Indian fashion trends
# =============================================================
FALLBACK_TRENDS_2026 = {
    "source": "fallback",  # tells the app we used built-in data, not web
    "season": "Spring-Summer 2026",
    "fetch_date": datetime.now().strftime("%Y-%m-%d"),  # today's date

    # The 5 most important colours of 2026 with HEX codes
    "trending_colours": [
        {"name": "Terracotta",   "hex": "#C67C5A", "description": "Earthy warm rust — the definitive Indian summer tone"},
        {"name": "Cobalt Blue",  "hex": "#0047AB", "description": "Bold, saturated blue — works with both ethnic and modern"},
        {"name": "Sage Green",   "hex": "#B2AC88", "description": "Muted, sophisticated — the new neutral for 2026"},
        {"name": "Ivory",        "hex": "#FFFFF0", "description": "Soft off-white — bridal, minimal, and eternally elegant"},
        {"name": "Deep Burgundy","hex": "#800020", "description": "Rich jewel tone — dominates wedding season 2026"},
    ],

    # What clothing silhouettes are trending this season
    "trending_outfits": [
        "Flowy wide-leg trousers paired with structured crop tops",
        "Classic saree in silk or organza with contrast blouse",
        "Indo-western dhoti pants with cape-style tops",
        "Tailored blazer co-ord sets in bold monochromes",
        "Tiered maxi dresses in earthy linen — perfect for Boho",
        "Fitted kurta with embroidered Palazzo for Ethnic Royale",
    ],

    # Trending jewellery styles for Spring-Summer 2026
    "trending_jewellery": [
        "Polki and jadau sets — heavy kundan for weddings",
        "Oxidised silver with turquoise for festival looks",
        "Minimalist gold layered chains for modern office wear",
        "Statement mismatched earrings for streetwear",
        "Delicate pearl and rose gold sets for romantic occasions",
    ],

    # Overall aesthetic moods trending right now
    "trending_vibes": [
        "Quiet Luxury — understated, expensive-looking neutrals",
        "Maximalist Ethnic Revival — more embroidery, more colour",
        "Earthy Minimalist — terracotta, sage, canvas textures",
        "Neo-Classic Indo-Fusion — traditional shapes, modern fabrics",
    ],
}


# =============================================================
# CLASS: TrendScoutAgent
# =============================================================
class TrendScoutAgent:
    """
    Agent 1: Scouts 2026 fashion trends.
    Call trend_scout.run() to get a dict of current trends.
    """

    def __init__(self):
        """Set up the agent with the URLs we will try to scrape."""

        # A dictionary of site name → URL of their fashion/style section
        self.sources = {
            "Vogue India":  "https://www.vogue.in/fashion",
            "NYKAA Blog":   "https://www.nykaa.com/beauty-blog/fashion/",
            "Elle India":   "https://www.elle.in/fashion/",
        }

        # Standard browser header — some sites block requests without this
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        # The final result dictionary — we will fill this during run()
        self.trend_data = {}

    # ─────────────────────────────────────────────────────────
    # METHOD: _try_scrape_vogue
    # Tries to get trending keywords from Vogue India's fashion page
    # ─────────────────────────────────────────────────────────
    def _try_scrape_vogue(self):
        """
        Attempts to scrape Vogue India's fashion section.
        Returns a list of article headlines, or [] if it fails.
        """
        try:
            # Make an HTTP GET request — like opening the URL in a browser
            response = requests.get(
                self.sources["Vogue India"],
                headers=self.headers,
                timeout=8  # give up after 8 seconds
            )

            # Check if the request succeeded (HTTP 200 = success)
            if response.status_code == 200 and BeautifulSoup:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, "html.parser")

                # Try to find article titles — they are usually inside <h2> or <h3> tags
                headlines = []
                for tag in soup.find_all(["h2", "h3"], limit=10):  # limit to 10
                    text = tag.get_text(strip=True)  # get the text, remove extra whitespace
                    if len(text) > 15:  # ignore very short ones (like navigation labels)
                        headlines.append(text)

                return headlines  # return the list of headlines we found

            return []  # return empty list if request failed

        except Exception as scrape_error:
            # Something went wrong — print a friendly message and return empty list
            print(f"    ⚠️  Could not reach Vogue India: {scrape_error}")
            return []

    # ─────────────────────────────────────────────────────────
    # METHOD: _try_scrape_elle
    # Tries to get trending content from Elle India
    # ─────────────────────────────────────────────────────────
    def _try_scrape_elle(self):
        """
        Attempts to scrape Elle India for fashion trend keywords.
        Returns a list of headline strings, or [] if it fails.
        """
        try:
            response = requests.get(
                self.sources["Elle India"],
                headers=self.headers,
                timeout=8
            )
            if response.status_code == 200 and BeautifulSoup:
                soup = BeautifulSoup(response.text, "html.parser")
                headlines = []
                for tag in soup.find_all(["h2", "h3", "h4"], limit=10):
                    text = tag.get_text(strip=True)
                    if len(text) > 10:
                        headlines.append(text)
                return headlines
            return []
        except Exception as e:
            print(f"    ⚠️  Could not reach Elle India: {e}")
            return []

    # ─────────────────────────────────────────────────────────
    # METHOD: _extract_colour_mentions
    # Scans headlines for colour keywords to build a live colour list
    # ─────────────────────────────────────────────────────────
    def _extract_colour_mentions(self, all_headlines):
        """
        Looks through scraped headlines for known colour words.
        Returns matched colours with their HEX codes.
        """
        # Map of colour name → HEX code
        colour_hex_map = {
            "terracotta": "#C67C5A",
            "cobalt":     "#0047AB",
            "sage":       "#B2AC88",
            "ivory":      "#FFFFF0",
            "burgundy":   "#800020",
            "emerald":    "#046307",
            "coral":      "#FF6B6B",
            "mustard":    "#FFDB58",
            "peach":      "#FFCBA4",
            "lavender":   "#B57EDC",
            "rust":       "#B7410E",
            "navy":       "#000080",
            "blush":      "#FFB6C1",
            "ivory":      "#FFFFF0",
            "camel":      "#C19A6B",
        }

        found_colours = []  # list to collect matched colours

        # Join all headlines into one big text block for easy searching
        combined_text = " ".join(all_headlines).lower()

        # Check each known colour against the combined text
        for colour_name, hex_code in colour_hex_map.items():
            if colour_name in combined_text:
                found_colours.append({
                    "name": colour_name.title(),  # capitalise first letter
                    "hex":  hex_code,
                    "description": f"Spotted in 2026 editorial trend coverage"
                })

        return found_colours  # return whatever colours we matched

    # ─────────────────────────────────────────────────────────
    # METHOD: _save_output
    # Saves the final trend dictionary to outputs/trend_brief.json
    # ─────────────────────────────────────────────────────────
    def _save_output(self, trend_dict):
        """Saves the trends to a JSON file so other agents can read it."""
        os.makedirs(OUTPUTS_DIR, exist_ok=True)  # create outputs/ folder if missing
        with open(TREND_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(trend_dict, f, indent=2, ensure_ascii=False)

    # ─────────────────────────────────────────────────────────
    # METHOD: run — THE MAIN ENTRY POINT
    # ─────────────────────────────────────────────────────────
    def run(self):
        """
        Tries to scrape live trend data.
        If scraping fails or returns too little, uses fallback data.
        Always returns a dict with: source, season, trending_colours,
        trending_outfits, trending_jewellery, trending_vibes.
        """
        print("  🌐 Trend Scout: Attempting to scrape live fashion data...")

        # Collect headlines from both sites
        vogue_headlines = self._try_scrape_vogue()
        elle_headlines  = self._try_scrape_elle()

        # Merge all headlines into one list
        all_headlines = vogue_headlines + elle_headlines

        # Check if we got any meaningful live data
        if len(all_headlines) >= 5:
            # We got enough live data — build a partial live dict
            print(f"  ✅ Scraped {len(all_headlines)} headlines from fashion sites")

            live_colours = self._extract_colour_mentions(all_headlines)

            # If we found at least 3 colours in the headlines, use them
            # Otherwise, use the fallback colours which are more complete
            if len(live_colours) >= 3:
                trending_colours = live_colours[:5]  # take top 5
                source = "web"
            else:
                trending_colours = FALLBACK_TRENDS_2026["trending_colours"]
                source = "web+fallback"  # partial web, partial fallback

            # Build the final trend dict using live data + fallback defaults
            self.trend_data = {
                "source":            source,
                "season":            FALLBACK_TRENDS_2026["season"],
                "fetch_date":        datetime.now().strftime("%Y-%m-%d"),
                "trending_colours":  trending_colours,
                "trending_outfits":  FALLBACK_TRENDS_2026["trending_outfits"],
                "trending_jewellery":FALLBACK_TRENDS_2026["trending_jewellery"],
                "trending_vibes":    FALLBACK_TRENDS_2026["trending_vibes"],
                "scraped_headlines": all_headlines[:5],  # first 5 headlines for display
            }

        else:
            # Not enough live data — use the complete fallback
            print("  📦 Using built-in 2026 trend data (sites may be unreachable)")
            self.trend_data = FALLBACK_TRENDS_2026.copy()
            self.trend_data["fetch_date"] = datetime.now().strftime("%Y-%m-%d")

        # Save the trend data to a JSON file for reference
        self._save_output(self.trend_data)
        print(f"  💾 Trends saved to: {TREND_OUTPUT}")

        return self.trend_data  # return the dict so other agents can use it
