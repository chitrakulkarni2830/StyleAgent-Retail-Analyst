"""
search_agent.py — Web Search & Trend Scraping Agent
Mock search API that simulates scraping Pinterest, Myntra, Ajio, TataCLiQ, FabIndia
for 2026 fashion trends. Falls back to curated trend data.
"""

from __future__ import annotations
import json
import random
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
#  CURATED 2026 TREND DATABASE (Mock Scraping Results)
# ═══════════════════════════════════════════════════════════════

TREND_DATABASE_2026 = {
    "spring_2026": {
        "trending_colors": ["Peach Fuzz", "Electric Indigo", "Mint", "Lavender", "Coral"],
        "key_fabrics": ["Organza", "Chanderi Silk", "Linen", "Chiffon"],
        "must_have_silhouette": ["A-Line", "Pre-Draped", "Crop & Flare"],
        "trending_patterns": ["Floral Embroidery", "Geometric Prints", "Pastel Ombré"],
        "source_summary": "Spring/Summer 2026 sees a return to soft femininity with pastels and lightweight fabrics. Indo-Western fusion is at its peak.",
    },
    "summer_2026": {
        "trending_colors": ["Electric Indigo", "Coral", "Mint", "White", "Peach"],
        "key_fabrics": ["Linen", "Cotton", "Georgette", "Organza"],
        "must_have_silhouette": ["Relaxed", "Straight", "A-Line"],
        "trending_patterns": ["Block Print", "Bandhani Revival", "Tropical"],
        "source_summary": "Summer 2026 champions breathable fabrics and bold pops of color. Handloom is making a luxury comeback.",
    },
    "autumn_2026": {
        "trending_colors": ["Cobalt Blue", "Emerald Green", "Mustard Yellow", "Deep Wine", "Teal"],
        "key_fabrics": ["Silk", "Velvet", "Jacquard", "Raw Silk"],
        "must_have_silhouette": ["Structured", "Draped", "Anarkali"],
        "trending_patterns": ["Zardozi", "Mirror Work", "Banarasi Weave"],
        "source_summary": "Autumn 2026 marks a resurgence of jewel tones and rich textiles. Velvet and Jacquard dominate evening wear.",
    },
    "winter_2026": {
        "trending_colors": ["Maroon", "Emerald Green", "Gold", "Royal Purple", "Navy Blue"],
        "key_fabrics": ["Velvet", "Pashmina", "Banarasi Silk", "Kanjeevaram Silk"],
        "must_have_silhouette": ["Structured", "Draped", "Flared"],
        "trending_patterns": ["Zari Embroidery", "Brocade", "Sequin Panels"],
        "source_summary": "Winter 2026 is all about opulence. Wedding season drives demand for heavy silks, velvets, and statement jewelry.",
    },
}

# Occasion-specific trend overlays
OCCASION_TREND_OVERLAY = {
    "wedding": {
        "extra_colors": ["Gold", "Red", "Maroon"],
        "extra_fabrics": ["Kanjeevaram Silk", "Banarasi Silk"],
        "extra_silhouettes": ["Structured", "Draped"],
    },
    "sangeet": {
        "extra_colors": ["Electric Indigo", "Gold", "Black"],
        "extra_fabrics": ["Sequin Georgette", "Velvet"],
        "extra_silhouettes": ["Pre-Draped", "Slim Fit"],
    },
    "diwali": {
        "extra_colors": ["Gold", "Maroon", "Emerald Green"],
        "extra_fabrics": ["Silk", "Velvet"],
        "extra_silhouettes": ["Straight", "A-Line"],
    },
    "haldi": {
        "extra_colors": ["Mustard Yellow", "Coral", "Peach"],
        "extra_fabrics": ["Chiffon", "Cotton"],
        "extra_silhouettes": ["Relaxed", "A-Line"],
    },
    "corporate": {
        "extra_colors": ["Navy Blue", "Charcoal", "Ivory"],
        "extra_fabrics": ["Wool Blend", "Cotton Blend"],
        "extra_silhouettes": ["Structured", "Slim Fit"],
    },
    "date_night": {
        "extra_colors": ["Black", "Deep Wine", "Cobalt Blue"],
        "extra_fabrics": ["Silk", "Velvet"],
        "extra_silhouettes": ["Slim Fit", "Pre-Draped"],
    },
}


# ═══════════════════════════════════════════════════════════════
#  MOCK WEB SCRAPING RESULTS (Pinterest, Myntra, Ajio etc.)
# ═══════════════════════════════════════════════════════════════

MOCK_WEB_RESULTS = {
    "pinterest": {
        "source": "Pinterest Trends",
        "trending_tags": ["#IndianBridalFashion2026", "#FestiveEthnic", "#IndoWesternFusion",
                          "#SareeGoals", "#Sherwani2026", "#MinimalistEthnic"],
        "top_colors": ["Cobalt Blue", "Sage Green", "Terracotta", "Electric Indigo"],
        "top_silhouettes": ["Pre-Draped Saree", "Concept Lehenga", "Bandhgala Suit"],
    },
    "myntra": {
        "source": "Myntra Bestsellers",
        "top_categories": ["Ethnic Kurtas", "Designer Sarees", "Fusion Wear"],
        "price_range": "₹2,000 - ₹50,000",
        "trending_brands": ["FabIndia", "Biba", "W", "Manyavar", "Raw Mango"],
    },
    "ajio": {
        "source": "Ajio Indie Collection",
        "focus": "Handloom Revival",
        "trending_fabrics": ["Chanderi", "Tussar", "Khadi", "Ikat"],
        "price_range": "₹1,500 - ₹25,000",
    },
    "tatacliq": {
        "source": "Tata CLiQ Luxury",
        "focus": "Premium Ethnic",
        "trending_brands": ["Sabyasachi", "Anita Dongre", "Tarun Tahiliani", "Ritu Kumar"],
        "price_range": "₹15,000 - ₹2,00,000",
    },
    "fabindia": {
        "source": "FabIndia New Arrivals",
        "focus": "Sustainable Ethnic",
        "trending_fabrics": ["Organic Cotton", "Handloom Silk", "Natural Dyes"],
        "price_range": "₹1,500 - ₹15,000",
    },
}


class MockSearchAPI:
    """Simulates web search for fashion trends."""

    @staticmethod
    def search(query: str) -> dict:
        """Search for fashion trends. Returns mock results based on query keywords."""
        query_lower = query.lower()
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "trends": {},
        }

        # Match relevant web sources
        for source_key, source_data in MOCK_WEB_RESULTS.items():
            results["sources"].append(source_data)

        # Match seasonal trends
        for season_key, trend_data in TREND_DATABASE_2026.items():
            season_name = season_key.split("_")[0]
            if season_name in query_lower or "2026" in query_lower:
                results["trends"] = trend_data
                break

        if not results["trends"]:
            # Default to current season
            month = datetime.now().month
            if month in (3, 4, 5):
                results["trends"] = TREND_DATABASE_2026["spring_2026"]
            elif month in (6, 7, 8):
                results["trends"] = TREND_DATABASE_2026["summer_2026"]
            elif month in (9, 10, 11):
                results["trends"] = TREND_DATABASE_2026["autumn_2026"]
            else:
                results["trends"] = TREND_DATABASE_2026["winter_2026"]

        return results


class WebScraper:
    """Simulates web scraping of fashion retail sites."""

    @staticmethod
    def scrape_trends(sources: list[str] = None, budget: float = 50000) -> dict:
        """Scrape fashion trends from multiple sources."""
        if not sources:
            sources = list(MOCK_WEB_RESULTS.keys())

        results = {
            "scraped_at": datetime.now().isoformat(),
            "source_count": len(sources),
            "budget_filter": budget,
            "aggregated_trends": {
                "top_colors": [],
                "top_fabrics": [],
                "top_brands": [],
            },
        }

        for src in sources:
            data = MOCK_WEB_RESULTS.get(src, {})
            if "top_colors" in data:
                results["aggregated_trends"]["top_colors"].extend(data["top_colors"])
            if "trending_brands" in data:
                results["aggregated_trends"]["top_brands"].extend(data["trending_brands"])
            if "trending_fabrics" in data:
                results["aggregated_trends"]["top_fabrics"].extend(data["trending_fabrics"])

        # Deduplicate
        for key in results["aggregated_trends"]:
            results["aggregated_trends"][key] = list(dict.fromkeys(results["aggregated_trends"][key]))

        return results


def get_occasion_trends(occasion: str, season: str = "") -> dict:
    """Get combined seasonal + occasion-specific trends."""
    # Base seasonal trends
    if not season:
        month = datetime.now().month
        if month in (3, 4, 5):
            season = "spring"
        elif month in (6, 7, 8):
            season = "summer"
        elif month in (9, 10, 11):
            season = "autumn"
        else:
            season = "winter"

    base = TREND_DATABASE_2026.get(f"{season}_2026", TREND_DATABASE_2026["autumn_2026"])
    overlay = OCCASION_TREND_OVERLAY.get(occasion.lower(), {})

    combined = {
        "trending_colors": list(dict.fromkeys(
            overlay.get("extra_colors", []) + base["trending_colors"]
        )),
        "key_fabrics": list(dict.fromkeys(
            overlay.get("extra_fabrics", []) + base["key_fabrics"]
        )),
        "must_have_silhouette": list(dict.fromkeys(
            overlay.get("extra_silhouettes", []) + base["must_have_silhouette"]
        )),
        "source_summary": base["source_summary"],
        "season": f"{season.capitalize()} 2026",
    }

    return combined
