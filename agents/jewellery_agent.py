"""
=============================================================
agents/jewellery_agent.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This is Agent 5 — the Jewellery Agent.
  Its job is to match a complete Jewellery Kit to each outfit.

  It receives:
    - outfit_items: the items chosen by the Wardrobe Architect
    - skin_undertone: from the Persona Agent (warm/cool/neutral)
    - occasion: e.g. 'wedding', 'date_night', 'office'

  It applies two rules:
    1. METAL TONE RULE:
       Warm undertone  → Gold or Rose Gold
       Cool undertone  → Silver or Platinum or White Gold
       Neutral         → Offer both options

    2. NECKLINE MATCHING RULE:
       V-neck           → Pendant necklace or drop earrings
       High neck        → Statement earrings only (skip necklace)
       Off-shoulder     → Ear cuffs or chandelier earrings
       Boat neck        → Collar necklace or choker
       All other necks → Standard pairing from jewellery_inventory

  For every outfit, it returns a COMPLETE Jewellery Kit:
    - Earrings
    - Necklace (or "Skip" with reason)
    - Bangles or Bracelets
    - Rings
    - Maang Tikka (only for Ethnic / Indo-Western vibes)
    - Optional Extras (waist belt, anklet, brooch)
  Plus: Styling Tips (2) + Fragrance Note
=============================================================
"""

import sqlite3   # built-in for database queries
import os        # built-in for file paths

# ── Path to the database file ─────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "inventory.db")

# ── Metal tone rules based on skin undertone ──────────────────
METAL_RULES = {
    "warm":    ["Gold", "Rose Gold"],        # warm skin glows with gold tones
    "cool":    ["Silver", "Platinum"],       # cool skin shines with silver tones
    "neutral": ["Gold", "Silver", "Rose Gold"],  # neutral can wear anything!
}

# ── Fragrance families by vibe and occasion ───────────────────
FRAGRANCE_MAP = {
    "Ethnic":       "Warm oud and sandalwood — the traditional Indian harmony of ancient woods and spice. Choose an attar (ittar) for authenticity at wedding or festival occasions.",
    "Modern":       "Fresh citrus or aquatic florals — light, clean, and professional. Works beautifully for office wear or first dates without being overpowering.",
    "Boho":         "Earthy patchouli with bergamot and amber — a freely-wandering fragrance for a freely-wandering spirit.",
    "Indo-Western": "Floral-musky blend: rose and jasmine anchored with a warm musk. Bridges the two worlds of your aesthetic perfectly.",
    "Classic":      "Classic powdery florals or crisp green chypres — the eternal sophistication of Chanel No.5 territory.",
    "Formal":       "Woody-citrus or ozonic florals — authoritative and clean. Commands a boardroom without competing for attention.",
    "Casual":       "Light fruity florals or a simple fresh-cut grass ozonic — effortless and approachable for everyday settings.",
    "Streetwear":   "Unexpected and bold — try an unconventional unisex fragrance: leather with violet, or smoked wood with pink pepper.",
}


# =============================================================
# CLASS: JewelleryAgent
# =============================================================
class JewelleryAgent:
    """
    Agent 5: Matches a full jewellery kit (6 pieces + styling tips)
    to each outfit based on skin undertone, occasion, and neckline.
    """

    def __init__(self):
        """Set up the agent — nothing complex needed here."""
        pass

    # ─────────────────────────────────────────────────────────
    # HELPER: _get_db_connection
    # ─────────────────────────────────────────────────────────
    def _get_db_connection(self):
        """Opens inventory.db for jewellery queries."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # enables row["column_name"] access
        return conn

    # ─────────────────────────────────────────────────────────
    # HELPER: _decide_metal
    # Picks the right metal based on skin undertone
    # ─────────────────────────────────────────────────────────
    def _decide_metal(self, skin_undertone):
        """
        Returns the best metal(s) for this skin undertone.
        e.g. "warm" → "Gold" as the primary choice
        """
        metals = METAL_RULES.get(skin_undertone, ["Gold"])  # default to Gold
        return metals[0]  # return the first / primary preferred metal

    # ─────────────────────────────────────────────────────────
    # HELPER: _apply_neckline_rule
    # Adjusts jewellery choices based on the outfit's neckline
    # ─────────────────────────────────────────────────────────
    def _apply_neckline_rule(self, neckline, metal, occasion):
        """
        Returns a necklace recommendation string based on the neckline.
        For some necklines we recommend skipping the necklace entirely.
        """
        neckline_lower = neckline.lower() if neckline else "open"

        if "high" in neckline_lower or "mandarin" in neckline_lower:
            # High necklines already create visual interest — necklace competes
            return f"Skip — the high neckline provides its own visual frame. Redirect attention with statement earrings instead."

        elif "off" in neckline_lower or "shoulder" in neckline_lower:
            # Bare shoulders need no necklace — the collarbone area is already the focus
            return f"Skip — the off-shoulder neckline draws attention to your collarbone, which is jewellery enough. Let your ear cuffs or chandelier earrings do the speaking."

        elif "v" in neckline_lower:
            # V-neck naturally creates a downward line — a pendant follows it beautifully
            return f"Delicate {metal} pendant necklace on a fine chain (16-18 inch) to follow the natural V-line and elongate the neckline."

        elif "boat" in neckline_lower or "collar" in neckline_lower:
            # Boat necks have a horizontal line — a choker or collar necklace echoes it
            return f"Slim {metal} choker or collar necklace — the horizontal line of the boat neck calls for a necklace at the same level to create a graphic frame."

        else:
            # Default: suggest a standard necklace appropriate to the occasion
            if occasion in ("wedding", "reception", "sangeet"):
                return f"Statement {metal} necklace — layered or kundan for wedding occasions where more is always right."
            else:
                return f"Paired {metal} necklace — a simple chain or minimalist pendant that complements without competing."

    # ─────────────────────────────────────────────────────────
    # HELPER: _query_jewellery_db
    # Searches jewellery_inventory for a specific piece type
    # ─────────────────────────────────────────────────────────
    def _query_jewellery_db(self, cursor, jewellery_type, metal, occasion, skin_undertone):
        """
        Finds a jewellery piece from the database matching the type,
        metal preference, occasion, and skin undertone suitability.
        Falls back progressively if no exact match is found.
        """
        # Try exact match first: type + metal + occasion + skin tone
        cursor.execute("""
            SELECT * FROM jewellery_inventory
            WHERE lower(jewellery_type) = ?
              AND lower(metal) = ?
              AND lower(occasion_tags) LIKE ?
              AND (lower(skin_undertone_fit) = ? OR lower(skin_undertone_fit) = 'all')
            ORDER BY RANDOM()
            LIMIT 1
        """, (
            jewellery_type.lower(),
            metal.lower(),
            f"%{occasion.lower()}%",
            skin_undertone.lower()
        ))

        row = cursor.fetchone()
        if row:
            return dict(row)  # found an exact match!

        # Fallback: type + occasion only (ignore metal and skin tone filter)
        cursor.execute("""
            SELECT * FROM jewellery_inventory
            WHERE lower(jewellery_type) = ?
              AND lower(occasion_tags) LIKE ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (jewellery_type.lower(), f"%{occasion.lower()}%"))

        row = cursor.fetchone()
        return dict(row) if row else None

    # ─────────────────────────────────────────────────────────
    # HELPER: _build_styling_tips
    # Returns 2 occasion-specific actionable styling tips
    # ─────────────────────────────────────────────────────────
    def _build_styling_tips(self, occasion, vibe, metal):
        """
        Creates 2 specific, actionable styling tips for this outfit.
        These are the kind of tips a real personal stylist would give.
        """
        tip_library = {
            "wedding": [
                f"Keep your {metal.lower()} jewellery pieces within the same finish — either all matte or all high-polish — so they read as a coordinated set rather than a random collection.",
                "Pin your dupatta at the shoulder with a decorative pin rather than tucking it — it allows the fabric to drape freely and you will look more effortless in photographs.",
            ],
            "office": [
                "If your earrings are statement pieces, wear your hair up so they are fully visible — they can substitute for a necklace entirely.",
                "Apply your fragrances before you put on your outfit to avoid any staining on the fabric — especially important for light-coloured pieces.",
            ],
            "date_night": [
                "Let your jewellery be the finishing touch, not the distraction — if your outfit is already detailed, choose simpler pieces. If it is minimal, let the jewellery speak.",
                f"Stack two or three thin {metal.lower()} rings on one hand for an effortlessly curated look without trying too hard.",
            ],
            "sangeet": [
                f"Keep your hair pinned up to let your chandelier earrings or jhumkas take centre stage — earrings at shoulder length need the frame of an open neckline.",
                "Choose jewellery you can dance in — avoid long chains that can snag and heavy tikkas that shift during movement.",
            ],
            "festival": [
                "Oxidised silver and semi-precious stones are the perfect festival companions — they look rich but you won't panic if they get bumped in a crowd.",
                "Layer bangles in sets of odd numbers (3, 5, 7) for a more curated, intentional look.",
            ],
        }

        # Return occasion-specific tips or universal fallback tips
        return tip_library.get(occasion.lower(), [
            f"Choose {metal.lower()} as your primary metal and stay consistent — mixing metal tones requires real expertise to look intentional rather than accidental.",
            "Less is almost always more with jewellery — if you are uncertain, remove the last piece you put on.",
        ])

    # ─────────────────────────────────────────────────────────
    # METHOD: run — THE MAIN ENTRY POINT
    # ─────────────────────────────────────────────────────────
    def run(self, outfits, skin_undertone, occasion, vibe):
        """
        Matches a full Jewellery Kit to each of the 3 outfits.

        outfits:       list of 3 outfit dicts from WardrobeArchitectAgent
        skin_undertone: 'warm', 'cool', or 'neutral'
        occasion:       e.g. 'wedding', 'office', 'date_night'
        vibe:           e.g. 'Ethnic', 'Modern'

        Returns: list of 3 jewellery kit dicts (one per outfit)
        """
        print(f"  💎 Jewellery Agent: Matching jewellery for {skin_undertone} undertone at {occasion}...")

        # Get the preferred metal for this skin tone
        metal = self._decide_metal(skin_undertone)

        # Detect neckline from the main outfit piece name
        # We look for neckline keywords in the item names
        neckline_keywords = {
            "v-neck": "v-neck", "v neck": "v-neck",
            "high": "high-neck", "mandarin": "high-neck",
            "off-shoulder": "off-shoulder", "off shoulder": "off-shoulder",
            "boat": "boat-neck", "collar": "boat-neck",
        }

        conn   = self._get_db_connection()
        cursor = conn.cursor()

        jewellery_kits = []  # collect completed kits for all 3 outfits

        for outfit_index, outfit in enumerate(outfits):
            # ── Detect neckline from outfit item names ────────────
            detected_neckline = "open"  # default

            # Look at every item name in this outfit for neckline clues
            for slot_name, item_data in (outfit.get("items") or {}).items():
                if item_data and isinstance(item_data, dict):
                    item_name_lower = item_data.get("name", "").lower()
                    for keyword, neckline_type in neckline_keywords.items():
                        if keyword in item_name_lower:
                            detected_neckline = neckline_type
                            break  # stop looking once we found a match

            # ── Apply neckline rule for necklace ──────────────────
            necklace_recommendation = self._apply_neckline_rule(detected_neckline, metal, occasion)

            # ── Query database for each jewellery piece type ──────
            earrings = self._query_jewellery_db(cursor, "Earrings", metal, occasion, skin_undertone)
            bangles  = self._query_jewellery_db(cursor, "Bangles", metal, occasion, skin_undertone)
            ring     = self._query_jewellery_db(cursor, "Ring", metal, occasion, skin_undertone)

            # Maang Tikka — only for ethnic and indo-western vibes
            tikka = None
            if vibe.lower() in ("ethnic", "indo-western", "ethnic royale"):
                tikka = self._query_jewellery_db(cursor, "Tikka", metal, occasion, skin_undertone)

            # Optional Extras — only for high-occasion vibes
            extras = None
            if occasion.lower() in ("wedding", "sangeet", "reception"):
                extras = self._query_jewellery_db(cursor, "Extras", metal, occasion, skin_undertone)

            # ── Build styling tips and fragrance note ────────────
            styling_tips   = self._build_styling_tips(occasion, vibe, metal)
            fragrance_note = FRAGRANCE_MAP.get(vibe, FRAGRANCE_MAP["Modern"])

            # ── Format each jewellery piece into a clean string ───
            def format_piece(db_row):
                """Converts a database row into a readable jewellery description."""
                if not db_row:
                    return "No matching piece found — opt for a simple metal chain as a safe universal choice"
                return (
                    f"{db_row['item_name']} | "
                    f"{db_row['metal']} | "
                    f"Price: ₹{db_row['price']:,.0f}"
                )

            # ── Assemble the complete Jewellery Kit ───────────────
            kit = {
                "outfit_number": outfit.get("outfit_number", outfit_index + 1),
                "preferred_metal": metal,
                "earrings":  format_piece(earrings),

                # Necklace is guided by the neckline rule, not always a DB query
                "necklace":  necklace_recommendation,

                "bangles":   format_piece(bangles),
                "rings":     format_piece(ring),

                # Tikka only included for Ethnic/Indo-Western vibes
                "maang_tikka": format_piece(tikka) if tikka else "Skip — not applicable for this vibe/occasion combination",

                # Extras only included for weddings/reception
                "optional_extras": format_piece(extras) if extras else "Carry a small handkerchief tucked into your bag — elegant and practical",

                "styling_tips":   styling_tips,     # list of 2 tip strings
                "fragrance_note": fragrance_note,   # one fragrance family description
            }

            jewellery_kits.append(kit)
            print(f"  ✅  Jewellery Kit {outfit_index + 1} assembled (Metal: {metal})")

        conn.close()  # close the database connection

        print(f"  ✅ All {len(jewellery_kits)} jewellery kits ready!")
        return jewellery_kits  # return the list of 3 kit dicts
