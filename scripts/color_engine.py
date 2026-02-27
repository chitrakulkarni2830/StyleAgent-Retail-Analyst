"""
color_engine.py — Advanced Color Theory & Premium Palette Engine
Implements complementary pairings, seasonal palettes, Rule of Three enforcement,
and skin-tone-aware jewelry metal suggestions.
"""

from __future__ import annotations


# ═══════════════════════════════════════════════════════════════
#  COLOR DATABASE — Indian Fashion Color Families with Hex
# ═══════════════════════════════════════════════════════════════

COLOR_DB = {
    # Jewel Tones
    "Emerald Green":    {"hex": "#046307", "family": "jewel", "warmth": "cool", "season": "winter"},
    "Maroon":           {"hex": "#800000", "family": "jewel", "warmth": "warm", "season": "winter"},
    "Royal Blue":       {"hex": "#002366", "family": "jewel", "warmth": "cool", "season": "winter"},
    "Deep Wine":        {"hex": "#722F37", "family": "jewel", "warmth": "warm", "season": "winter"},
    "Royal Purple":     {"hex": "#6A0DAD", "family": "jewel", "warmth": "cool", "season": "winter"},
    "Bottle Green":     {"hex": "#006A4E", "family": "jewel", "warmth": "cool", "season": "winter"},
    "Ruby Red":         {"hex": "#9B111E", "family": "jewel", "warmth": "warm", "season": "winter"},

    # Pastels
    "Pastel Pink":      {"hex": "#FFD1DC", "family": "pastel", "warmth": "warm", "season": "summer"},
    "Lavender":         {"hex": "#B57EDC", "family": "pastel", "warmth": "cool", "season": "summer"},
    "Mint":             {"hex": "#98FF98", "family": "pastel", "warmth": "cool", "season": "summer"},
    "Peach":            {"hex": "#FFDAB9", "family": "pastel", "warmth": "warm", "season": "summer"},
    "Coral":            {"hex": "#FF7F50", "family": "pastel", "warmth": "warm", "season": "summer"},

    # Trending / Bold
    "Cobalt Blue":      {"hex": "#0047AB", "family": "bold", "warmth": "cool", "season": "all"},
    "Electric Indigo":  {"hex": "#6F00FF", "family": "bold", "warmth": "cool", "season": "all"},
    "Teal":             {"hex": "#008080", "family": "bold", "warmth": "cool", "season": "all"},
    "Mustard Yellow":   {"hex": "#E1A95F", "family": "warm", "warmth": "warm", "season": "all"},

    # Neutrals
    "Black":            {"hex": "#000000", "family": "neutral", "warmth": "neutral", "season": "all"},
    "White":            {"hex": "#FFFFFF", "family": "neutral", "warmth": "neutral", "season": "all"},
    "Ivory":            {"hex": "#FFFFF0", "family": "neutral", "warmth": "warm", "season": "all"},
    "Beige":            {"hex": "#F5F5DC", "family": "neutral", "warmth": "warm", "season": "all"},
    "Neutral Grey":     {"hex": "#808080", "family": "neutral", "warmth": "neutral", "season": "all"},
    "Charcoal":         {"hex": "#36454F", "family": "neutral", "warmth": "cool", "season": "all"},
    "Navy Blue":        {"hex": "#000080", "family": "neutral", "warmth": "cool", "season": "all"},

    # Metallics
    "Gold":             {"hex": "#D4AF37", "family": "metallic", "warmth": "warm", "season": "all"},
    "Rose Gold":        {"hex": "#B76E79", "family": "metallic", "warmth": "warm", "season": "all"},
    "Silver":           {"hex": "#C0C0C0", "family": "metallic", "warmth": "cool", "season": "all"},

    # Additional
    "Red":              {"hex": "#D2042D", "family": "bold", "warmth": "warm", "season": "all"},
    "Magenta":          {"hex": "#FF00FF", "family": "bold", "warmth": "warm", "season": "all"},
    "Olive Green":      {"hex": "#556B2F", "family": "earth", "warmth": "warm", "season": "all"},
    "Tan":              {"hex": "#D2B48C", "family": "earth", "warmth": "warm", "season": "all"},
    "Brown":            {"hex": "#8B4513", "family": "earth", "warmth": "warm", "season": "all"},
    "Nude":             {"hex": "#E8CCBF", "family": "neutral", "warmth": "warm", "season": "all"},
    "Indigo":           {"hex": "#3F00FF", "family": "bold", "warmth": "cool", "season": "all"},
}


# ═══════════════════════════════════════════════════════════════
#  COMPLEMENTARY COLOR PAIRINGS — Indian Fashion Context
# ═══════════════════════════════════════════════════════════════

COMPLEMENTARY_PAIRINGS = {
    "Maroon":           ["Gold", "Ivory", "Beige", "Emerald Green"],
    "Emerald Green":    ["Gold", "Maroon", "Ivory", "Ruby Red"],
    "Cobalt Blue":      ["Gold", "Ivory", "Beige", "Silver"],
    "Royal Purple":     ["Gold", "Ivory", "Silver", "Mint"],
    "Navy Blue":        ["Gold", "Ivory", "Rose Gold", "White"],
    "Teal":             ["Mustard Yellow", "Gold", "Coral", "Ivory"],
    "Mustard Yellow":   ["Teal", "Navy Blue", "Ivory", "White"],
    "Black":            ["Gold", "Silver", "Red", "White"],
    "White":            ["Gold", "Navy Blue", "Cobalt Blue", "Black"],
    "Ivory":            ["Gold", "Maroon", "Emerald Green", "Navy Blue"],
    "Deep Wine":        ["Gold", "Ivory", "Beige", "Rose Gold"],
    "Pastel Pink":      ["Silver", "Ivory", "Mint", "Gold"],
    "Lavender":         ["Silver", "Ivory", "Gold", "Mint"],
    "Mint":             ["Gold", "Coral", "Ivory", "Lavender"],
    "Peach":            ["Gold", "Ivory", "Teal", "White"],
    "Coral":            ["Gold", "Teal", "Ivory", "Mint"],
    "Red":              ["Gold", "Ivory", "Black", "Beige"],
    "Gold":             ["Maroon", "Emerald Green", "Navy Blue", "Black"],
    "Electric Indigo":  ["Silver", "Gold", "Ivory", "White"],
    "Bottle Green":     ["Gold", "Ivory", "Rose Gold", "Beige"],
}


# ═══════════════════════════════════════════════════════════════
#  SEASONAL PALETTES
# ═══════════════════════════════════════════════════════════════

SEASONAL_PALETTES = {
    "summer_day": {
        "label": "Summer Day / Morning Wedding",
        "colors": ["Lavender", "Mint", "Peach", "Pastel Pink", "Ivory", "White"],
        "metals": ["Rose Gold", "Silver"],
    },
    "winter_night": {
        "label": "Winter Night / Grand Reception",
        "colors": ["Emerald Green", "Maroon", "Deep Wine", "Royal Blue", "Royal Purple"],
        "metals": ["Gold", "Antique Gold"],
    },
    "monsoon_festive": {
        "label": "Monsoon / Navratri / Ganesh Chaturthi",
        "colors": ["Red", "Mustard Yellow", "Cobalt Blue", "Teal", "Coral"],
        "metals": ["Gold", "Oxidized Silver"],
    },
    "autumn_elegant": {
        "label": "Autumn / Diwali / Eid",
        "colors": ["Gold", "Maroon", "Deep Wine", "Emerald Green", "Cobalt Blue"],
        "metals": ["Gold", "Rose Gold"],
    },
    "spring_fresh": {
        "label": "Spring / Haldi / Mehendi",
        "colors": ["Mustard Yellow", "Coral", "Mint", "Peach", "Lavender"],
        "metals": ["Rose Gold", "Gold"],
    },
}


# ═══════════════════════════════════════════════════════════════
#  PALETTE STRATEGY ENGINE
# ═══════════════════════════════════════════════════════════════

OCCASION_PALETTE_MAP = {
    "wedding":      "analogous",
    "reception":    "complementary",
    "sangeet":      "complementary",
    "haldi":        "monochromatic",
    "mehendi":      "analogous",
    "diwali":       "complementary",
    "eid":          "analogous",
    "navratri":     "complementary",
    "corporate":    "monochromatic",
    "date_night":   "complementary",
    "vacation":     "analogous",
    "brunch":       "monochromatic",
}


def get_palette_strategy(occasion: str, vibe: str = "") -> str:
    """Determine the color palette strategy for an occasion."""
    strategy = OCCASION_PALETTE_MAP.get(occasion.lower(), "complementary")
    # Vibe overrides
    if vibe in ("party", "glamorous", "energetic"):
        strategy = "complementary"
    elif vibe in ("serene", "polished", "laid_back"):
        strategy = "monochromatic"
    return strategy


def get_complementary_colors(primary_color: str, count: int = 2) -> list[str]:
    """Get complementary accent colors for a primary color."""
    pairings = COMPLEMENTARY_PAIRINGS.get(primary_color, [])
    return pairings[:count]


def _get_color_mood(color_name: str) -> str:
    """Classify an existing color in the DB into one of our 4 UI Moods."""
    info = COLOR_DB.get(color_name, {})
    family = info.get("family", "neutral")
    if family == "pastel":
        return "Pastel"
    elif family in ("earth", "warm"):
        return "Earthy"
    elif family in ("jewel", "bold"):
        return "Vibrant"
    else:
        return "Neutral"


def get_secondary_colors(primary_hex: str, strategy: str, requested_mood: str = "Any") -> list[str]:
    """Given a primary color hex and strategy, return 2 recommended secondary hex codes masked by mood."""
    color_name = None
    for name, info in COLOR_DB.items():
        if info["hex"].lower() == primary_hex.lower():
            color_name = name
            break

    if not color_name:
        return ["#D4AF37", "#FFFFF0"]  # Default: Gold + Ivory

    def _matches_mood(c_name: str) -> bool:
        if requested_mood == "Any" or requested_mood == "Neutral":
            return True # Neutral requested means don't strictly ban things if we run out, or Any
        return _get_color_mood(c_name) == requested_mood or _get_color_mood(c_name) == "Neutral"

    if strategy == "monochromatic":
        # Return shades within the same warmth, prioritizing the requested mood
        warmth = COLOR_DB[color_name]["warmth"]
        matches = [
            info["hex"] for name, info in COLOR_DB.items()
            if info["warmth"] == warmth and name != color_name and _matches_mood(name)
        ]
        return matches[:2] if len(matches) >= 2 else ["#D4AF37", "#FFFFF0"]

    elif strategy == "complementary":
        comps = COMPLEMENTARY_PAIRINGS.get(color_name, ["Gold", "Ivory"])
        matches = [COLOR_DB[c]["hex"] for c in comps if c in COLOR_DB and _matches_mood(c)]
        # Fallback if mood masking strips all complementary colors
        if not matches:
             matches = [COLOR_DB[c]["hex"] for c in comps if c in COLOR_DB]
        return matches[:2] if len(matches) >= 2 else ["#D4AF37", "#FFFFF0"]

    else:  # analogous
        warmth = COLOR_DB[color_name]["warmth"]
        family = COLOR_DB[color_name]["family"]
        matches = [
            info["hex"] for name, info in COLOR_DB.items()
            if (info["warmth"] == warmth or info["family"] == family)
            and name != color_name and _matches_mood(name)
        ]
        if not matches:
            matches = [
                info["hex"] for name, info in COLOR_DB.items()
                if (info["warmth"] == warmth or info["family"] == family)
                and name != color_name
            ]
        return matches[:2] if len(matches) >= 2 else ["#D4AF37", "#FFFFF0"]


def get_jewelry_metal(skin_tone: str, occasion: str = "") -> str:
    """Recommend jewelry metal based on skin tone and occasion context."""
    occasion_key = occasion.lower()
    if occasion_key in ("wedding", "diwali", "reception") and skin_tone != "cool":
        return "Gold"
    metal_map = {
        "warm": "Gold",
        "cool": "Silver",
        "neutral": "Rose Gold",
    }
    return metal_map.get(skin_tone.lower(), "Gold")


def suggest_accent_color(base_neutral: str, trending_color: str) -> dict:
    """
    Bridge Logic: Suggest how to introduce a trending color as an accent
    on a neutral base the user already likes.
    """
    if trending_color in COLOR_DB:
        trend_hex = COLOR_DB[trending_color]["hex"]
    else:
        trend_hex = "#0047AB"  # default cobalt

    if base_neutral in COLOR_DB:
        base_hex = COLOR_DB[base_neutral]["hex"]
    else:
        base_hex = "#808080"

    return {
        "accent_color": trending_color,
        "accent_hex": trend_hex,
        "base_color": base_neutral,
        "base_hex": base_hex,
        "suggestion": (
            f"Use {base_neutral} as your foundation piece, then introduce "
            f"{trending_color} as an accent — through a dupatta, pocket square, "
            f"jewelry, or a single statement accessory. This creates an elevated look "
            f"without departing from your comfort zone."
        ),
    }


def validate_rule_of_three(colors: list[str]) -> dict:
    """
    Enforce the 'Rule of Three' — max 3 distinct colors for a premium outfit.
    Returns validation result and suggestions.
    """
    unique = list(dict.fromkeys(colors))  # preserve order, remove dupes
    neutrals = [c for c in unique if COLOR_DB.get(c, {}).get("family") == "neutral"]
    non_neutrals = [c for c in unique if c not in neutrals]

    if len(non_neutrals) <= 3:
        return {
            "valid": True,
            "colors": unique,
            "message": f"✓ {len(non_neutrals)} distinct colors — curated and premium.",
        }
    else:
        keep = non_neutrals[:2] + neutrals[:1]
        drop = [c for c in non_neutrals[2:]]
        return {
            "valid": False,
            "colors": keep,
            "dropped": drop,
            "message": (
                f"⚠ {len(non_neutrals)} colors detected. Reducing to 3 for a curated feel. "
                f"Dropping: {', '.join(drop)}"
            ),
        }


def get_color_hex(color_name: str) -> str:
    """Lookup hex code for a color name."""
    info = COLOR_DB.get(color_name)
    return info["hex"] if info else "#808080"


def get_seasonal_palette(season: str) -> dict:
    """Get the recommended seasonal color palette."""
    key_map = {
        "summer": "summer_day",
        "winter": "winter_night",
        "monsoon": "monsoon_festive",
        "autumn": "autumn_elegant",
        "spring": "spring_fresh",
    }
    key = key_map.get(season.lower(), "autumn_elegant")
    return SEASONAL_PALETTES.get(key, SEASONAL_PALETTES["autumn_elegant"])


def get_stylists_tip(primary_color: str, strategy: str, occasion: str) -> str:
    """Generate a professional stylist tip for the outfit."""
    tips = {
        "complementary": (
            f"💡 Stylist's Tip: The {primary_color} base creates a striking canvas. "
            f"I've paired it with complementary tones to create visual interest — "
            f"perfect for a {occasion.replace('_', ' ')} where you want to stand out elegantly."
        ),
        "analogous": (
            f"💡 Stylist's Tip: This tonal palette centered around {primary_color} creates "
            f"a sophisticated, seamless flow. The analogous colors blend without competing — "
            f"ideal for the {occasion.replace('_', ' ')} setting."
        ),
        "monochromatic": (
            f"💡 Stylist's Tip: A monochromatic approach anchored in {primary_color} "
            f"is the hallmark of quiet luxury. The varying shades add depth while maintaining "
            f"an effortlessly polished look for your {occasion.replace('_', ' ')}."
        ),
    }
    return tips.get(strategy, tips["complementary"])
