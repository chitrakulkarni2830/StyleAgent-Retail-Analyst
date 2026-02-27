"""
indian_fashion_kb.py — Indian Occasion & Style Knowledge Base
Deep knowledge graph of Indian events, regional climate, skin tone guidance,
and occasion-specific styling rules for both men and women.
"""


# ═══════════════════════════════════════════════════════════════
#  OCCASION RULES — Fabric, Color, Jewelry, Formality
# ═══════════════════════════════════════════════════════════════

OCCASION_RULES = {
    # ─── WEDDINGS (Function-Specific) ───
    "haldi": {
        "display_name": "Haldi Ceremony",
        "description": "Light, vibrant, easy to move in — expect turmeric stains!",
        "colors": ["Mustard Yellow", "Coral", "Mint", "White", "Peach"],
        "avoid_colors": ["Black", "Maroon", "Navy Blue"],
        "fabrics_women": ["Chiffon", "Georgette", "Cotton", "Linen"],
        "fabrics_men": ["Cotton", "Linen", "Rayon"],
        "silhouettes_women": ["A-Line", "Anarkali", "Short"],
        "silhouettes_men": ["Straight", "Short", "Relaxed"],
        "jewelry_women": "Floral jewelry (fresh or artificial), minimal gold, bangles",
        "jewelry_men": "None or simple thread bracelet",
        "footwear_women": "Kolhapuris, flat sandals — comfort first",
        "footwear_men": "Kolhapuris, leather sandals",
        "weight": "light",
        "formality": "casual",
        "vibe": "playful",
    },
    "mehendi": {
        "display_name": "Mehendi Ceremony",
        "description": "Vibrant and festive — floral prints welcomed.",
        "colors": ["Green", "Coral", "Peach", "Mustard Yellow", "Lavender"],
        "avoid_colors": ["Black"],
        "fabrics_women": ["Georgette", "Chiffon", "Cotton Silk"],
        "fabrics_men": ["Cotton", "Linen", "Cotton Silk"],
        "silhouettes_women": ["A-Line", "Anarkali", "Flared", "Crop"],
        "silhouettes_men": ["Straight", "Short", "Relaxed"],
        "jewelry_women": "Floral jewelry, statement jhumkas, bangles stacks",
        "jewelry_men": "Simple bracelet or thread",
        "footwear_women": "Embroidered juttis, kolhapuris",
        "footwear_men": "Juttis, kolhapuris",
        "weight": "light",
        "formality": "festive_casual",
        "vibe": "vibrant",
    },
    "sangeet": {
        "display_name": "Sangeet / Cocktail Night",
        "description": "Glamorous, high-shine — sequins and mirror work encouraged.",
        "colors": ["Cobalt Blue", "Electric Indigo", "Gold", "Emerald Green", "Deep Wine", "Black"],
        "avoid_colors": [],
        "fabrics_women": ["Sequin Georgette", "Velvet", "Raw Silk", "Organza"],
        "fabrics_men": ["Silk", "Velvet", "Raw Silk"],
        "silhouettes_women": ["Pre-Draped", "Flared", "A-Line", "Crop"],
        "silhouettes_men": ["Structured", "Slim Fit"],
        "jewelry_women": "Statement pieces — chandelier earrings, cocktail rings, layered necklaces",
        "jewelry_men": "Brooch, cufflinks, premium watch",
        "footwear_women": "Stiletto sandals, embroidered wedge heels",
        "footwear_men": "Mojris with mirror work, suede loafers",
        "weight": "medium",
        "formality": "glamorous",
        "vibe": "party",
    },
    "wedding": {
        "display_name": "Wedding Ceremony (Phera/Nikah)",
        "description": "Traditional, heavy — rich jewel tones and artisanal craftsmanship.",
        "sub_occasions": {
            "day_phera": {
                "note": "Morning ceremony — slightly lighter fabrics acceptable",
                "fabrics_override_women": ["Kanjeevaram Silk", "Chanderi Silk", "Tussar Silk"],
                "fabrics_override_men": ["Silk", "Cotton Silk"],
            },
            "evening_reception": {
                "note": "Evening grandeur — heavy silks and velvet shine here",
                "fabrics_override_women": ["Kanjeevaram Silk", "Banarasi Silk", "Velvet", "Raw Silk"],
                "fabrics_override_men": ["Velvet", "Raw Silk", "Silk"],
            },
        },
        "colors": ["Maroon", "Emerald Green", "Royal Blue", "Gold", "Deep Wine", "Royal Purple", "Red"],
        "avoid_colors": ["White", "Black"],
        "fabrics_women": ["Kanjeevaram Silk", "Banarasi Silk", "Paithani Silk", "Velvet"],
        "fabrics_men": ["Raw Silk", "Velvet", "Silk"],
        "silhouettes_women": ["Draped", "Flared", "A-Line"],
        "silhouettes_men": ["Structured"],
        "jewelry_women": "Full bridal set — Kundan/Polki/Temple, maang tikka, nath, bangles, rani haar",
        "jewelry_men": "Brooch, safa (turban), sarpech, jeweled buttons",
        "footwear_women": "Embroidered wedge heels, embellished sandals",
        "footwear_men": "Embroidered mojris, gold juttis",
        "weight": "heavy",
        "formality": "traditional_formal",
        "vibe": "regal",
    },
    "reception": {
        "display_name": "Wedding Reception",
        "description": "Glamorous yet elegant — indo-western fusion works beautifully.",
        "colors": ["Navy Blue", "Cobalt Blue", "Gold", "Black", "Emerald Green", "Deep Wine", "Pastel Pink"],
        "avoid_colors": [],
        "fabrics_women": ["Silk", "Velvet", "Organza", "Sequin Georgette"],
        "fabrics_men": ["Wool Blend", "Silk", "Velvet"],
        "silhouettes_women": ["Pre-Draped", "Draped", "Flared", "Structured"],
        "silhouettes_men": ["Structured", "Slim Fit"],
        "jewelry_women": "Statement necklace with matching earrings, cocktail ring",
        "jewelry_men": "Premium watch, cufflinks, pocket square",
        "footwear_women": "Stiletto sandals, embroidered heels",
        "footwear_men": "Leather loafers, suede shoes",
        "weight": "medium",
        "formality": "semi_formal",
        "vibe": "elegant",
    },

    # ─── FESTIVALS ───
    "diwali": {
        "display_name": "Diwali",
        "description": "Festival of Lights — rich traditional with a modern touch.",
        "sub_occasions": {
            "morning_puja": {
                "note": "Ethnic Minimalism — light fabrics, understated elegance",
                "fabrics_override_women": ["Chikankari Cotton", "Linen", "Chanderi Silk"],
                "fabrics_override_men": ["Cotton", "Linen", "Khadi"],
                "vibe_override": "serene",
            },
            "evening_celebration": {
                "note": "Regal Traditional — silk and velvet for the main celebration",
                "fabrics_override_women": ["Silk", "Velvet", "Banarasi Silk"],
                "fabrics_override_men": ["Silk", "Velvet", "Jacquard"],
                "vibe_override": "festive_grand",
            },
        },
        "colors": ["Gold", "Maroon", "Emerald Green", "Royal Blue", "Deep Wine", "Cobalt Blue"],
        "avoid_colors": [],
        "fabrics_women": ["Silk", "Velvet", "Georgette", "Chikankari Cotton"],
        "fabrics_men": ["Silk", "Jacquard", "Cotton", "Velvet"],
        "silhouettes_women": ["Straight", "A-Line", "Draped"],
        "silhouettes_men": ["Straight", "Structured"],
        "jewelry_women": "Kundan set for evening, jhumkas for morning, diyas-inspired jewelry",
        "jewelry_men": "Brooch on nehru jacket, or premium watch",
        "footwear_women": "Kolhapuris for morning, juttis or heels for evening",
        "footwear_men": "Mojris for ethnic, loafers for smart casual",
        "weight": "medium",
        "formality": "festive",
        "vibe": "celebratory",
    },
    "eid": {
        "display_name": "Eid",
        "description": "Elegant and refined — pastels for day, rich tones for evening.",
        "colors": ["White", "Ivory", "Mint", "Pastel Pink", "Lavender", "Emerald Green", "Gold"],
        "avoid_colors": [],
        "fabrics_women": ["Georgette", "Silk", "Chiffon", "Cotton"],
        "fabrics_men": ["Cotton", "Silk", "Linen"],
        "silhouettes_women": ["Anarkali", "Straight", "A-Line"],
        "silhouettes_men": ["Straight"],
        "jewelry_women": "Pearl sets, rose gold minimal, crescent motifs",
        "jewelry_men": "Prayer cap, simple ring or bracelet",
        "footwear_women": "Embroidered juttis, block heels",
        "footwear_men": "Leather sandals, juttis",
        "weight": "light",
        "formality": "festive",
        "vibe": "serene_elegant",
    },
    "navratri": {
        "display_name": "Navratri / Garba",
        "description": "Color-coded by day — vibrant, high-energy, mirror work.",
        "colors": ["Red", "Royal Blue", "Mustard Yellow", "Green", "Orange", "Peacock Blue"],
        "avoid_colors": [],
        "fabrics_women": ["Cotton", "Georgette", "Chiffon"],
        "fabrics_men": ["Cotton", "Silk"],
        "silhouettes_women": ["Flared", "A-Line", "Anarkali"],
        "silhouettes_men": ["Straight", "Short"],
        "jewelry_women": "Oxidized silver, mirror work jewelry, heavy jhumkas, bajubandh",
        "jewelry_men": "Bracelet, stud earring (if style permits)",
        "footwear_women": "Kolhapuris, flat juttis — comfort for garba",
        "footwear_men": "Mojris, sport shoes for garba",
        "weight": "light",
        "formality": "festive_casual",
        "vibe": "energetic",
    },
    "ganesh_chaturthi": {
        "display_name": "Ganesh Chaturthi",
        "description": "Traditional Maharashtrian influence — nauvari, cotton elegance.",
        "colors": ["Red", "Gold", "Mustard Yellow", "Orange", "Green"],
        "avoid_colors": [],
        "fabrics_women": ["Cotton", "Silk", "Paithani Silk"],
        "fabrics_men": ["Cotton", "Silk"],
        "silhouettes_women": ["Draped", "Straight", "A-Line"],
        "silhouettes_men": ["Straight"],
        "jewelry_women": "Green glass bangles, nath (nose ring), mogra gajra",
        "jewelry_men": "Simple kurta — no heavy jewelry",
        "footwear_women": "Kolhapuris",
        "footwear_men": "Kolhapuris",
        "weight": "medium",
        "formality": "traditional",
        "vibe": "devotional_festive",
    },

    # ─── MODERN INDIAN LIFESTYLE ───
    "corporate": {
        "display_name": "Corporate / Formal Lunch",
        "description": "Smart Ethnic or Global Indian — structured silhouettes, minimal accessories.",
        "colors": ["Navy Blue", "Black", "Neutral Grey", "Ivory", "Beige", "Charcoal"],
        "avoid_colors": ["Red", "Gold", "Magenta"],
        "fabrics_women": ["Silk", "Wool Blend", "Cotton Blend", "Linen"],
        "fabrics_men": ["Wool Blend", "Cotton", "Linen"],
        "silhouettes_women": ["Straight", "Structured", "Slim Fit"],
        "silhouettes_men": ["Structured", "Slim Fit", "Classic"],
        "jewelry_women": "Minimal — rose gold studs, thin bracelet, structured watch",
        "jewelry_men": "Premium watch, cufflinks, tie pin",
        "footwear_women": "Block heels, structured pumps",
        "footwear_men": "Leather loafers, oxfords",
        "weight": "light",
        "formality": "formal",
        "vibe": "polished",
    },
    "date_night": {
        "display_name": "Date Night / Fine Dining",
        "description": "Chic and sophisticated — pre-draped sarees, tailored blazers.",
        "colors": ["Black", "Deep Wine", "Cobalt Blue", "Navy Blue", "Charcoal", "Emerald Green"],
        "avoid_colors": [],
        "fabrics_women": ["Sequin Georgette", "Silk", "Velvet", "Satin"],
        "fabrics_men": ["Wool Blend", "Silk", "Cotton"],
        "silhouettes_women": ["Pre-Draped", "Structured", "Slim Fit", "Straight"],
        "silhouettes_men": ["Slim Fit", "Mandarin", "Classic"],
        "jewelry_women": "Sculptural silver, baroque pearls, thin gold chains",
        "jewelry_men": "Premium watch, silk pocket square",
        "footwear_women": "Stiletto sandals, nude pumps",
        "footwear_men": "Suede loafers, leather derbies",
        "weight": "medium",
        "formality": "semi_formal",
        "vibe": "intimate",
    },
    "vacation": {
        "display_name": "Vacation / Resort",
        "description": "Breezy and effortless — linens, block prints, resort silhouettes.",
        "sub_occasions": {
            "beach": {
                "note": "Goa / Maldives — light, airy, tropical prints",
                "fabrics_override_women": ["Linen", "Cotton", "Rayon"],
                "fabrics_override_men": ["Linen", "Rayon", "Cotton"],
            },
            "mountain": {
                "note": "Himachal / Kashmir — layerable, warm-toned",
                "fabrics_override_women": ["Pashmina", "Wool Blend", "Khadi"],
                "fabrics_override_men": ["Pashmina", "Wool Blend", "Khadi"],
            },
        },
        "colors": ["White", "Teal", "Peach", "Mint", "Indigo", "Coral"],
        "avoid_colors": ["Black", "Maroon"],
        "fabrics_women": ["Linen", "Cotton", "Rayon"],
        "fabrics_men": ["Linen", "Rayon", "Cotton"],
        "silhouettes_women": ["Relaxed", "A-Line", "Draped"],
        "silhouettes_men": ["Relaxed"],
        "jewelry_women": "Shell jewelry, beaded bracelets, silver anklets",
        "jewelry_men": "Leather bracelet, casual watch",
        "footwear_women": "Flat sandals, espadrilles",
        "footwear_men": "Espadrilles, leather sandals",
        "weight": "light",
        "formality": "casual",
        "vibe": "relaxed",
    },
    "brunch": {
        "display_name": "Brunch / Casual Meet",
        "description": "Easy, modern Indian — kaftan dresses, linen sets.",
        "colors": ["White", "Peach", "Lavender", "Mint", "Teal", "Coral"],
        "avoid_colors": [],
        "fabrics_women": ["Cotton", "Linen", "Rayon"],
        "fabrics_men": ["Cotton", "Linen"],
        "silhouettes_women": ["Relaxed", "A-Line", "Straight"],
        "silhouettes_men": ["Relaxed", "Straight"],
        "jewelry_women": "Minimal — stud earrings, thin bracelet",
        "jewelry_men": "Casual watch",
        "footwear_women": "Flat sandals, slip-ons",
        "footwear_men": "Loafers, white sneakers",
        "weight": "light",
        "formality": "casual",
        "vibe": "laid_back",
    },
}


# ═══════════════════════════════════════════════════════════════
#  REGIONAL CLIMATE MAP — Fabric & Weight recommendations
# ═══════════════════════════════════════════════════════════════

REGIONAL_CLIMATE = {
    "pune": {"climate": "warm_humid", "prefer_light": True, "note": "Lightweight fabrics — Chanderi, Cotton, Linen over heavy silk", "local_craft": "Paithani Silk"},
    "mumbai": {"climate": "tropical", "prefer_light": True, "note": "Breathable fabrics, avoid heavy velvet", "local_craft": "Bandhani"},
    "delhi": {"climate": "extreme", "note": "Heavy in winter (Oct-Feb), light in summer (Mar-Sep)", "local_craft": "Zardozi, Gota Patti"},
    "jaipur": {"climate": "hot_dry", "prefer_light": True, "note": "Block prints, Bandhani, bright colors", "local_craft": "Bandhej, Gota Patti"},
    "chennai": {"climate": "hot_humid", "prefer_light": True, "note": "Kanjeevaram silk is traditional; light cotton for daily", "local_craft": "Kanjeevaram"},
    "bangalore": {"climate": "pleasant", "note": "Versatile — all fabrics work, silk preferred for occasions", "local_craft": "Mysore Silk"},
    "lucknow": {"climate": "warm", "prefer_light": True, "note": "Chikankari is the signature craft", "local_craft": "Chikankari"},
    "kolkata": {"climate": "warm_humid", "prefer_light": True, "note": "Tussar silk, muslin, tant sarees", "local_craft": "Tant, Muslin"},
    "ahmedabad": {"climate": "hot_dry", "prefer_light": True, "note": "Bandhani, Patola, vibrant colors", "local_craft": "Patola, Bandhani"},
    "kashmir": {"climate": "cold", "prefer_light": False, "note": "Pashmina shawls, heavy wool, rich embroidery", "local_craft": "Pashmina, Sozni"},
    "varanasi": {"climate": "warm", "note": "Banarasi silk — the gold standard", "local_craft": "Banarasi Silk"},
    "goa": {"climate": "tropical", "prefer_light": True, "note": "Resort wear — linen, cotton, tropical prints", "local_craft": None},
    "hyderabad": {"climate": "hot", "prefer_light": True, "note": "Pochampally ikat, pearl jewelry culture", "local_craft": "Pochampally Ikat"},
}


# ═══════════════════════════════════════════════════════════════
#  SKIN TONE GUIDE — Metal & Color recommendations
# ═══════════════════════════════════════════════════════════════

SKIN_TONE_GUIDE = {
    "warm": {
        "metals": ["Gold", "Rose Gold", "Copper"],
        "best_colors": ["Emerald Green", "Mustard Yellow", "Coral", "Maroon", "Peach", "Teal", "Olive Green"],
        "avoid_colors": ["Neon", "Icy Blue", "Stark White"],
        "tip": "Warm skin tones glow in earthy and jewel-toned hues. Gold jewelry enhances your natural warmth.",
    },
    "cool": {
        "metals": ["Silver", "Platinum", "White Gold"],
        "best_colors": ["Cobalt Blue", "Lavender", "Mint", "Royal Purple", "Pastel Pink", "Navy Blue", "Electric Indigo"],
        "avoid_colors": ["Orange", "Mustard Yellow", "Olive Green"],
        "tip": "Cool skin tones are complemented by icy pastels and deep blues. Silver and platinum jewelry adds a luminous contrast.",
    },
    "neutral": {
        "metals": ["Gold", "Silver", "Rose Gold", "Mixed Metals"],
        "best_colors": ["Teal", "Deep Wine", "Ivory", "Neutral Grey", "Cobalt Blue", "Emerald Green"],
        "avoid_colors": ["Neon"],
        "tip": "Neutral tones have the versatility to wear almost any color. Mixed metals work beautifully.",
    },
}


# ═══════════════════════════════════════════════════════════════
#  STYLE DNA ARCHETYPES
# ═══════════════════════════════════════════════════════════════

STYLE_DNA_ARCHETYPES = {
    "Bold Traditionalist": {
        "keywords": ["traditional", "heavy", "silk", "gold", "jewel_tones"],
        "description": "Loves rich heritage pieces — Kanjeevaram sarees, heavy Kundan sets, and regal silhouettes.",
        "accent_suggestion": "Try introducing one modern element (a structured clutch or contemporary earring) to keep the look fresh.",
    },
    "Minimalist Professional": {
        "keywords": ["slim_fit", "neutral", "structured", "modern", "clean"],
        "description": "Gravitates toward clean lines, neutral palettes, and understated elegance.",
        "accent_suggestion": "A single statement piece (a Nehru jacket or a bold pocket square) elevates your look without overpowering it.",
    },
    "Fusion Explorer": {
        "keywords": ["indo_western", "pastel", "organza", "modern", "experimental"],
        "description": "Blends Indian aesthetics with global fashion — pre-draped sarees, crop tops with lehengas.",
        "accent_suggestion": "Layer traditional jewelry (jhumkas) with contemporary pieces (minimal chains) for a curated contrast.",
    },
    "Ethnic Minimalist": {
        "keywords": ["chikankari", "linen", "cotton", "subtle", "understated"],
        "description": "Prefers the quiet luxury of handloom fabrics and artisanal craftsmanship.",
        "accent_suggestion": "Let the fabric speak — pair with oxidized silver jewelry and earth-toned accessories.",
    },
    "Regal Maximalist": {
        "keywords": ["velvet", "zardozi", "heavy", "jewelled", "opulent"],
        "description": "Embraces grandeur — velvet sherwanis, heavily embroidered lehengas, statement jewelry.",
        "accent_suggestion": "Balance heavy pieces with one lighter element (a chiffon dupatta instead of a silk one).",
    },
}


# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_occasion_guidance(occasion: str, sub_occasion: str = "", region: str = "", gender: str = "") -> dict:
    """
    Returns complete styling guidance for a given occasion, with optional
    regional and sub-occasion overrides.
    """
    occasion_key = occasion.lower().replace(" ", "_")
    rules = OCCASION_RULES.get(occasion_key)
    if not rules:
        # Fuzzy match
        for key in OCCASION_RULES:
            if occasion_key in key or key in occasion_key:
                rules = OCCASION_RULES[key]
                break
    if not rules:
        rules = OCCASION_RULES.get("date_night")  # safe default

    result = dict(rules)

    # Apply sub-occasion overrides
    if sub_occasion and "sub_occasions" in rules:
        sub_key = sub_occasion.lower().replace(" ", "_")
        for k, v in rules["sub_occasions"].items():
            if sub_key in k or k in sub_key:
                for override_key, override_val in v.items():
                    if override_key.startswith("fabrics_override"):
                        fabric_key = override_key.replace("_override", "")
                        result[fabric_key] = override_val
                    elif override_key.endswith("_override"):
                        base_key = override_key.replace("_override", "")
                        result[base_key] = override_val

    # Apply regional climate adjustments
    if region:
        region_key = region.lower()
        climate_info = REGIONAL_CLIMATE.get(region_key)
        if climate_info:
            result["regional_note"] = climate_info["note"]
            result["local_craft"] = climate_info.get("local_craft")
            if climate_info.get("prefer_light") and result.get("weight") == "heavy":
                result["weight_note"] = f"Consider lighter variants for {region} climate"

    # Filter by gender
    if gender:
        gender_key = gender.lower()
        if gender_key == "male":
            result["fabrics"] = result.get("fabrics_men", [])
            result["silhouettes"] = result.get("silhouettes_men", [])
        elif gender_key == "female":
            result["fabrics"] = result.get("fabrics_women", [])
            result["silhouettes"] = result.get("silhouettes_women", [])

    return result


def get_skin_tone_metals(skin_tone: str) -> list[str]:
    """Returns recommended jewelry metals for a skin tone."""
    guide = SKIN_TONE_GUIDE.get(skin_tone.lower(), SKIN_TONE_GUIDE["neutral"])
    return guide["metals"]


def get_skin_tone_colors(skin_tone: str) -> list[str]:
    """Returns recommended colors for a skin tone."""
    guide = SKIN_TONE_GUIDE.get(skin_tone.lower(), SKIN_TONE_GUIDE["neutral"])
    return guide["best_colors"]


def get_style_dna_info(style_dna: str) -> dict:
    """Returns archetype description and accent suggestion."""
    return STYLE_DNA_ARCHETYPES.get(style_dna, {
        "description": "A unique blend of personal style preferences.",
        "accent_suggestion": "Experiment with contrasting textures and a single pop of color.",
    })


def get_clarifying_questions(occasion: str, gender: str = "") -> list[str]:
    """Generate smart follow-up questions based on occasion (Autofilter Intelligence)."""
    questions = []
    occasion_key = occasion.lower().replace(" ", "_")
    rules = OCCASION_RULES.get(occasion_key, {})

    if "sub_occasions" in rules:
        if occasion_key == "wedding":
            questions.append("Is this for a Day Phera/Muhurta or an Evening Reception?")
        elif occasion_key == "diwali":
            questions.append("Is this for the morning Puja or the evening celebration?")
        elif occasion_key == "vacation":
            questions.append("Is this a beach destination (Goa/Maldives) or a mountain trip (Himachal/Kashmir)?")

    questions.append("Do you have a preferred color palette, or would you like me to suggest one?")

    if gender.lower() == "female":
        questions.append("Would you prefer traditional or modern/fusion styling?")
    elif gender.lower() == "male":
        questions.append("Would you prefer ethnic (kurta/sherwani) or a structured (bandhgala/blazer) look?")

    return questions
