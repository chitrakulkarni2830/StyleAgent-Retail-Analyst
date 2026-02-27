"""
trend_scout_agent.py — Agent A: The 'Inspiration' Layer
Identifies top fashion trends for the current season using search APIs
and cross-references with Ollama reasoning. Outputs a structured TrendBrief.
"""

from __future__ import annotations
import json
from datetime import datetime

from state_schema import StyleState, TrendBrief
from search_agent import MockSearchAPI, WebScraper, get_occasion_trends
from ollama_client import get_client


class TrendScoutAgent:
    """
    The Trend Scout researches current fashion trends by:
    1. Searching the web (mock) for seasonal trends
    2. Cross-referencing with occasion-specific overlays
    3. Using Ollama to reason about trend relevance
    4. Outputting a structured TrendBrief
    """

    def __init__(self):
        self.search_api = MockSearchAPI()
        self.web_scraper = WebScraper()
        self.ollama = get_client()

    def run(self, state: StyleState) -> StyleState:
        """
        Execute the Trend Scout pipeline.
        Updates state.trend_brief with structured trend data.
        """
        state.current_step = "trend_scout"
        print("\n🔍 TREND SCOUT — Researching fashion trends...")
        print("─" * 50)

        # Step 1: Determine the season
        season = self._determine_season()
        occasion = state.occasion or "general"

        # Step 2: Search for trends
        print(f"  📡 Searching: 'Top Fashion Trends {season.capitalize()} 2026 {occasion}'")
        search_results = self.search_api.search(
            f"Top Fashion Trends {season} 2026 Indian {occasion}"
        )

        # Step 3: Scrape web sources
        print(f"  🌐 Scraping: Pinterest, Myntra, Ajio, TataCLiQ, FabIndia...")
        scrape_results = self.web_scraper.scrape_trends(budget=state.budget)

        # Step 4: Get occasion-specific trend overlays
        combined_trends = get_occasion_trends(occasion, season)
        print(f"  🎯 Trends found for: {occasion.replace('_', ' ').title()}")

        # Step 5: Use Ollama to reason about trend relevance
        user_prefs = None
        if state.user_style_profile:
            user_prefs = {
                "style_dna": state.user_style_profile.style_dna,
                "preferred_colors": state.user_style_profile.dominant_colors,
            }

        trend_analysis = self.ollama.reason_about_trends(
            combined_trends, occasion, user_prefs
        )
        print(f"  🧠 Trend Analysis: {trend_analysis[:100]}...")

        # Step 6: Build the TrendBrief
        trend_brief = TrendBrief(
            trending_colors=combined_trends["trending_colors"][:5],
            key_fabrics=combined_trends["key_fabrics"][:4],
            must_have_silhouette=combined_trends["must_have_silhouette"][:3],
            season=combined_trends["season"],
            year=2026,
            source_summary=trend_analysis,
        )

        state.trend_brief = trend_brief
        print(f"\n  ✅ Trend Brief Ready:")
        print(f"     Colors  → {', '.join(trend_brief.trending_colors)}")
        print(f"     Fabrics → {', '.join(trend_brief.key_fabrics)}")
        print(f"     Shapes  → {', '.join(trend_brief.must_have_silhouette)}")
        print("─" * 50)

        return state

    def _determine_season(self) -> str:
        """Determine current season based on month."""
        month = datetime.now().month
        if month in (3, 4, 5):
            return "spring"
        elif month in (6, 7, 8):
            return "summer"
        elif month in (9, 10, 11):
            return "autumn"
        else:
            return "winter"

    def get_secondary_trends(self, state: StyleState) -> list[str]:
        """
        Get secondary trend colors for the feedback loop.
        When user rejects first recommendation, use these.
        """
        if not state.trend_brief:
            return ["Gold", "Ivory", "Beige"]

        all_colors = state.trend_brief.trending_colors
        # Return the trends beyond the top 3 (positions 3-5)
        secondary = all_colors[3:] if len(all_colors) > 3 else all_colors[1:]
        return secondary if secondary else ["Gold", "Ivory", "Beige"]
