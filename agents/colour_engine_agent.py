"""
=============================================================
agents/colour_engine_agent.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This is Agent 3 — the Colour Engine. It is the MOST CRITICAL
  agent because outfit quality depends entirely on colour harmony.

  It uses Python's built-in 'colorsys' library to do real
  colour wheel mathematics. No downloads needed.

  It includes an inner class called ColourWheel with 5 methods:
    1. complementary      — colour directly opposite on the wheel
    2. analogous          — 2 colours 30° either side
    3. triadic            — 2 colours 120° away
    4. monochromatic      — 4 tints and shades of the same hue
    5. split_complementary— 2 colours near the complement

  It also applies SKIN UNDERTONE RULES:
    WARM → ochre, terracotta, olive, gold, rust, peach, camel
    COOL → cobalt, emerald, rose, silver, lavender, burgundy
    NEUTRAL → 2 warm palettes + 1 cool palette

  Returns: 3 named palette options (Option A, Option B, Option C)
=============================================================
"""

import colorsys  # built-in Python library for HSL ↔ RGB colour math


# =============================================================
# CLASS: ColourWheel
# Does all the mathematical colour-wheel calculations.
# Works with HEX colour codes (like #FF5733).
# =============================================================
class ColourWheel:
    """
    A mathematical colour wheel — uses HSL (Hue, Saturation, Lightness)
    to calculate harmonious colour pairings.

    Hue is measured in degrees (0–360) around a circle:
      0° = Red, 60° = Yellow, 120° = Green,
      180° = Cyan, 240° = Blue, 300° = Magenta
    """

    # ─────────────────────────────────────────────────────────
    # HELPER: hex_to_hsl  — converts #RRGGBB → (H, S, L)
    # ─────────────────────────────────────────────────────────
    def hex_to_hsl(self, hex_colour):
        """
        Converts a HEX colour string (e.g. '#C67C5A') into
        HSL values: Hue (0-360), Saturation (0-1), Lightness (0-1).
        We use HSL because it matches how humans perceive colour.
        """
        hex_colour = hex_colour.lstrip("#")  # remove the '#' symbol

        # Convert hex pairs to 0-255 RGB integers
        r = int(hex_colour[0:2], 16)  # red channel (0-255)
        g = int(hex_colour[2:4], 16)  # green channel (0-255)
        b = int(hex_colour[4:6], 16)  # blue channel (0-255)

        # Normalise to 0-1 range (colorsys expects this)
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0

        # Convert RGB to HLS using Python's built-in colorsys
        # Note: colorsys returns (H, L, S) — not (H, S, L)!
        h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)

        hue_degrees = h * 360.0  # convert 0-1 hue to 0-360 degrees

        return hue_degrees, s, l  # return (Hue in degrees, Saturation, Lightness)

    # ─────────────────────────────────────────────────────────
    # HELPER: hsl_to_hex  — converts (H, S, L) → #RRGGBB
    # ─────────────────────────────────────────────────────────
    def hsl_to_hex(self, hue_degrees, saturation, lightness):
        """
        Converts HSL values back into a HEX colour string.
        hue_degrees: 0 to 360
        saturation:  0.0 to 1.0
        lightness:   0.0 to 1.0
        Returns: '#RRGGBB' string
        """
        # Wrap hue around the colour wheel (e.g. 380° becomes 20°)
        hue_degrees = hue_degrees % 360

        # Normalise hue to 0-1 range for colorsys
        h_norm = hue_degrees / 360.0

        # Convert HLS back to RGB using colorsys
        # Note: colorsys uses HLS order (not HSL)
        r_norm, g_norm, b_norm = colorsys.hls_to_rgb(h_norm, lightness, saturation)

        # Convert 0-1 floats back to 0-255 integers
        r = int(round(r_norm * 255))
        g = int(round(g_norm * 255))
        b = int(round(b_norm * 255))

        # Format as HEX string with zero-padding (e.g. 5 → '05')
        return f"#{r:02X}{g:02X}{b:02X}"

    # ─────────────────────────────────────────────────────────
    # METHOD 1: complementary
    # Returns the colour directly opposite (180° away)
    # ─────────────────────────────────────────────────────────
    def complementary(self, base_hex):
        """
        The complementary colour is exactly opposite on the colour wheel.
        Example: Terracotta orange → Teal blue (opposite)
        Returns: 1 HEX colour string
        """
        h, s, l = self.hex_to_hsl(base_hex)
        complement_hue = (h + 180) % 360  # go exactly halfway around the wheel
        return self.hsl_to_hex(complement_hue, s, l)

    # ─────────────────────────────────────────────────────────
    # METHOD 2: analogous
    # Returns 2 colours sitting 30° either side of the base
    # ─────────────────────────────────────────────────────────
    def analogous(self, base_hex):
        """
        Analogous colours are neighbours on the colour wheel.
        They harmonise because they share similar undertones.
        Example: Orange base → Yellow-orange and Red-orange on either side
        Returns: list of 2 HEX colour strings [left_neighbour, right_neighbour]
        """
        h, s, l = self.hex_to_hsl(base_hex)
        left_hue  = (h - 30) % 360  # 30° to the left
        right_hue = (h + 30) % 360  # 30° to the right
        return [
            self.hsl_to_hex(left_hue,  s, l),
            self.hsl_to_hex(right_hue, s, l),
        ]

    # ─────────────────────────────────────────────────────────
    # METHOD 3: triadic
    # Returns 2 colours each 120° away from the base
    # ─────────────────────────────────────────────────────────
    def triadic(self, base_hex):
        """
        Triadic colours form a triangle on the colour wheel.
        Very bold and vibrant — good for statement looks.
        Example: Red base → Blue and Yellow (the classic triadic)
        Returns: list of 2 HEX colour strings
        """
        h, s, l = self.hex_to_hsl(base_hex)
        triad_1 = (h + 120) % 360  # one third around the wheel
        triad_2 = (h + 240) % 360  # two thirds around the wheel
        return [
            self.hsl_to_hex(triad_1, s, l),
            self.hsl_to_hex(triad_2, s, l),
        ]

    # ─────────────────────────────────────────────────────────
    # METHOD 4: monochromatic
    # Returns 4 tints and shades of the same hue
    # ─────────────────────────────────────────────────────────
    def monochromatic(self, base_hex):
        """
        Monochromatic means 'one colour' — same hue, different lightness.
        Creates a sophisticated, tonal look — very on-trend for 2026.
        Returns: list of 4 HEX colour strings (2 lighter, 2 darker)
        """
        h, s, l = self.hex_to_hsl(base_hex)

        # Clamp lightness between 0.1 and 0.9 to avoid pure black/white
        def clamp(value):
            return max(0.1, min(0.9, value))

        return [
            self.hsl_to_hex(h, s, clamp(l + 0.25)),  # much lighter tint
            self.hsl_to_hex(h, s, clamp(l + 0.12)),  # light tint
            self.hsl_to_hex(h, s, clamp(l - 0.12)),  # dark shade
            self.hsl_to_hex(h, s, clamp(l - 0.25)),  # much darker shade
        ]

    # ─────────────────────────────────────────────────────────
    # METHOD 5: split_complementary
    # Two colours flanking the direct complement
    # ─────────────────────────────────────────────────────────
    def split_complementary(self, base_hex):
        """
        Split complementary is a softer version of complementary.
        Instead of the exact opposite, you take two colours either
        side of the complement — more balanced and elegant.
        Returns: list of 2 HEX colour strings
        """
        h, s, l = self.hex_to_hsl(base_hex)
        split_1 = (h + 150) % 360  # 30° before the complement
        split_2 = (h + 210) % 360  # 30° after the complement
        return [
            self.hsl_to_hex(split_1, s, l),
            self.hsl_to_hex(split_2, s, l),
        ]


# =============================================================
# SKIN UNDERTONE RULES
# These map skin undertones to colours that naturally complement them.
# Based on Indian fashion styling expertise.
# =============================================================
SKIN_UNDERTONE_RULES = {
    "warm": {
        "favoured_colours": ["Ochre", "Terracotta", "Olive Green", "Gold", "Rust", "Peach", "Camel", "Warm Red"],
        "favoured_hex":     ["#CC7722", "#C67C5A", "#556B2F", "#D4AF37", "#B7410E", "#FFCBA4", "#C19A6B", "#C0392B"],
        "metals":           "Gold or Rose Gold",
        "rationale":        "Warm undertones harmonise with earthy, golden, and amber tones. These colours draw out the natural warmth in your complexion.",
    },
    "cool": {
        "favoured_colours": ["Cobalt Blue", "Emerald Green", "Rose", "Silver", "Lavender", "Burgundy", "Icy Pink"],
        "favoured_hex":     ["#0047AB", "#046307", "#FF007F", "#C0C0C0", "#B57EDC", "#800020", "#FFB3C6"],
        "metals":           "Silver or Platinum or White Gold",
        "rationale":        "Cool undertones come alive with jewel tones and crisp shades. Blue, green, and rose tones make your skin glow.",
    },
    "neutral": {
        "favoured_colours": ["Ivory", "Navy", "Sage Green", "Dusty Rose", "Terracotta", "Cobalt Blue"],
        "favoured_hex":     ["#FFFFF0", "#000080", "#B2AC88", "#C9A898", "#C67C5A", "#0047AB"],
        "metals":           "Gold, Silver, or Rose Gold — all work beautifully",
        "rationale":        "Neutral undertones are the most flexible — both warm earthy tones and cool jewel tones work. You can wear almost anything!",
    },
}


# =============================================================
# CLASS: ColourEngineAgent
# Generates 3 palette options using the ColourWheel math above
# =============================================================
class ColourEngineAgent:
    """
    Agent 3: Generates 3 colour palettes (Option A, B, C)
    tailored to the user's skin undertone and the base colour.
    """

    def __init__(self):
        """Create an instance of the ColourWheel to use in calculations."""
        self.wheel = ColourWheel()  # our mathematical colour calculator

    # ─────────────────────────────────────────────────────────
    # HELPER: _hex_to_name_guess
    # A simple lookup to get a human-readable name from a HEX code
    # ─────────────────────────────────────────────────────────
    def _hex_to_name_guess(self, hex_code):
        """
        Tries to find a fashion-friendly name for a computed HEX colour.
        If not found, returns the HEX code itself as the name.
        """
        # Dictionary of known HEX codes → fashion colour names
        known = {
            "#C67C5A": "Terracotta",   "#0047AB": "Cobalt Blue",
            "#B2AC88": "Sage Green",   "#FFFFF0": "Ivory",
            "#800020": "Burgundy",     "#046307": "Emerald Green",
            "#FF6B6B": "Coral",        "#FFDB58": "Mustard Yellow",
            "#FFCBA4": "Peach",        "#B57EDC": "Lavender",
            "#B7410E": "Rust",         "#000080": "Navy",
            "#FFB6C1": "Blush Pink",   "#C19A6B": "Camel",
            "#D4AF37": "Gold",         "#000000": "Black",
            "#FFFFFF": "White",        "#8B4513": "Chestnut Brown",
            "#C0C0C0": "Silver",       "#B76E79": "Rose Gold",
        }
        # Return the name if found, otherwise use the HEX code itself
        return known.get(hex_code.upper(), hex_code)

    # ─────────────────────────────────────────────────────────
    # METHOD: run — THE MAIN ENTRY POINT
    # ─────────────────────────────────────────────────────────
    def run(self, base_hex, skin_undertone="warm", harmony_preference="Surprise Me"):
        """
        Generates 3 full palette dictionaries.

        base_hex:           HEX code of the primary colour (e.g. '#C67C5A')
        skin_undertone:     'warm', 'cool', or 'neutral'
        harmony_preference: from GUI — 'Complementary', 'Analogous',
                            'Triadic', 'Monochromatic', or 'Surprise Me'

        Returns: list of 3 dicts, each with:
            harmony_type, primary_colour, primary_hex,
            secondary_colour, secondary_hex,
            accent_colour, accent_hex,
            colour_rationale
        """
        print(f"  🎨 Colour Engine: Generating palettes for {base_hex} ({skin_undertone} undertone)...")

        # Get the skin undertone rules for this user
        undertone_rules = SKIN_UNDERTONE_RULES.get(skin_undertone, SKIN_UNDERTONE_RULES["neutral"])
        metal           = undertone_rules["metals"]
        base_rationale  = undertone_rules["rationale"]

        # The primary colour name (best effort lookup)
        primary_name = self._hex_to_name_guess(base_hex)

        # ── Calculate all possible harmony colours ─────────────
        comp_hex            = self.wheel.complementary(base_hex)
        analogue_hexes      = self.wheel.analogous(base_hex)
        triadic_hexes       = self.wheel.triadic(base_hex)
        mono_hexes          = self.wheel.monochromatic(base_hex)
        split_comp_hexes    = self.wheel.split_complementary(base_hex)

        # Convert computed HEX codes to readable names
        comp_name        = self._hex_to_name_guess(comp_hex)
        analogue_names   = [self._hex_to_name_guess(h) for h in analogue_hexes]
        triadic_names    = [self._hex_to_name_guess(h) for h in triadic_hexes]
        mono_names       = [self._hex_to_name_guess(h) for h in mono_hexes]
        split_comp_names = [self._hex_to_name_guess(h) for h in split_comp_hexes]

        # ── Option A: Determined by harmony_preference ─────────
        if harmony_preference == "Complementary":
            option_a = {
                "harmony_type":      "Complementary",
                "primary_colour":    primary_name,
                "primary_hex":       base_hex,
                "secondary_colour":  comp_name,
                "secondary_hex":     comp_hex,
                "accent_colour":     "Gold" if skin_undertone == "warm" else "Silver",
                "accent_hex":        "#D4AF37" if skin_undertone == "warm" else "#C0C0C0",
                "colour_rationale":  (
                    f"{primary_name} and {comp_name} sit directly opposite each other on the colour wheel, "
                    f"creating a bold, high-contrast pairing that commands attention. "
                    f"Perfect for occasions where you want to stand out with intention. "
                    f"{base_rationale} Complete with {metal} jewellery."
                ),
            }
        elif harmony_preference == "Monochromatic":
            option_a = {
                "harmony_type":     "Monochromatic",
                "primary_colour":   primary_name,
                "primary_hex":      base_hex,
                "secondary_colour": mono_names[0],
                "secondary_hex":    mono_hexes[0],
                "accent_colour":    mono_names[3],
                "accent_hex":       mono_hexes[3],
                "colour_rationale": (
                    f"A tonal palette built entirely around {primary_name} — lighter and darker shades "
                    f"of the same hue create a look of understated, quiet luxury. "
                    f"This is the hallmark of a well-edited wardrobe. "
                    f"{base_rationale} Pair with {metal} jewellery."
                ),
            }
        else:
            # Default Option A = Analogous (for Analogous, Triadic, or Surprise Me)
            option_a = {
                "harmony_type":     "Analogous",
                "primary_colour":   primary_name,
                "primary_hex":      base_hex,
                "secondary_colour": analogue_names[0],
                "secondary_hex":    analogue_hexes[0],
                "accent_colour":    analogue_names[1],
                "accent_hex":       analogue_hexes[1],
                "colour_rationale": (
                    f"{primary_name} anchors this palette, with {analogue_names[0]} "
                    f"and {analogue_names[1]} flanking it on the colour wheel. "
                    f"Analogous palettes feel harmonious and effortless — they never clash. "
                    f"{base_rationale} Beautiful with {metal} accents."
                ),
            }

        # ── Option B: Always Triadic ───────────────────────────
        option_b = {
            "harmony_type":     "Triadic",
            "primary_colour":   primary_name,
            "primary_hex":      base_hex,
            "secondary_colour": triadic_names[0],
            "secondary_hex":    triadic_hexes[0],
            "accent_colour":    triadic_names[1],
            "accent_hex":       triadic_hexes[1],
            "colour_rationale": (
                f"This palette forms a perfect triangle on the colour wheel: "
                f"{primary_name}, {triadic_names[0]}, and {triadic_names[1]}. "
                f"Triadic combinations are vibrant and playful — ideal for Festive occasions "
                f"or Navratri where bold expression is celebrated. "
                f"Keep the primary colour dominant (60%), use the triadic pair as accents (20% + 20%). "
                f"Styled best with {metal} jewellery."
            ),
        }

        # ── Option C: Split Complementary — sophisticated balance
        option_c = {
            "harmony_type":     "Split Complementary",
            "primary_colour":   primary_name,
            "primary_hex":      base_hex,
            "secondary_colour": split_comp_names[0],
            "secondary_hex":    split_comp_hexes[0],
            "accent_colour":    split_comp_names[1],
            "accent_hex":       split_comp_hexes[1],
            "colour_rationale": (
                f"Split complementary is the sophisticated stylist's choice: "
                f"instead of the jarring directness of pure complementary, "
                f"{primary_name} is paired with {split_comp_names[0]} and {split_comp_names[1]}, "
                f"which sit either side of its complement. The result is visually rich "
                f"without feeling aggressive. Ideal for Wedding guest or Reception looks. "
                f"Works beautifully with {metal} jewellery."
            ),
        }

        # Bundle the 3 options together and return them
        palettes = [option_a, option_b, option_c]

        print(f"  ✅ Generated 3 palettes: {option_a['harmony_type']} | Triadic | Split Complementary")
        return palettes  # return the list of 3 palette dicts
