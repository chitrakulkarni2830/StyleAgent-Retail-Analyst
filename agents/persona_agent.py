"""
=============================================================
agents/persona_agent.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This is Agent 2 — the Customer Persona Agent.
  Its job is to look at what this user has bought and browsed,
  then assign them ONE of 8 Style Personas.

  It reads 3 SQLite tables:
    - purchase_history  (what they actually bought)
    - browsing_logs     (what they looked at online)
    - user_profile      (their basic info: size, skin tone, budget)

  Then it computes a profile and assigns one personality label
  like "Ethnic Royale" or "Minimalist Professional".

  This profile is then used by the Colour Engine and
  Wardrobe Architect to personalise outfit choices.
=============================================================
"""

import sqlite3   # built-in Python library for database work
import os        # for building file paths

# ── Path to the SQLite database file ──────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "inventory.db")


# =============================================================
# CLASS: PersonaAgent
# =============================================================
class PersonaAgent:
    """
    Agent 2: Reads purchase + browsing data, builds a user persona.
    Call persona_agent.run(user_id) to get the persona dict back.
    """

    def __init__(self):
        """Set up the list of all 8 possible Style Personas."""

        # Each persona has: a name, the vibes it maps to, and a description
        # The agent will assign the one that best matches purchase patterns
        self.persona_definitions = {
            "Ethnic Royale": {
                "vibes":       ["Ethnic"],           # loves ethnic wear
                "description": "You gravitate towards the grandeur of traditional Indian fashion. Banarasi silks, rich embroidery, and handcrafted jewellery speak your language. You dress to honour culture and command attention at every occasion.",
            },
            "Indo-Western Fusion": {
                "vibes":       ["Indo-Western"],
                "description": "You live between two worlds — traditional Indian silhouettes with modern cuts and unexpected fabrics. Dhoti trousers with a blazer. A saree with a belt. You are never quite one thing, and that is your superpower.",
            },
            "Minimalist Professional": {
                "vibes":       ["Modern", "Formal", "Classic"],
                "description": "Clean lines, quality fabrics, and a restrained palette define your wardrobe. You believe the best outfit says a lot by showing very little. Every piece you own earns its place.",
            },
            "Maximalist Diva": {
                "vibes":       ["Ethnic", "Indo-Western"],
                "description": "More is more, and you know it. You layer prints, stack jewellery, and mix textures with an unselfconscious joy. You don't dress to blend in — you dress to be remembered.",
            },
            "Classic Elegance": {
                "vibes":       ["Classic", "Formal"],
                "description": "Timeless over trendy, every time. You invest in pieces that will look just as beautiful in ten years. Your wardrobe is an edited collection of the truly essential.",
            },
            "Boho Free Spirit": {
                "vibes":       ["Boho", "Casual"],
                "description": "You dress as if every day could be a music festival or a marketplace in Jaipur. Earthy tones, flowing fabrics, and jewellery that tells a story — your style is effortlessly eclectic.",
            },
            "Street Smart Casual": {
                "vibes":       ["Streetwear", "Casual"],
                "description": "Comfortable does not mean basic for you. You blend sporty silhouettes with designer pieces, and you always look like you accidentally stumbled out of a fashion editorial.",
            },
            "Power Dresser": {
                "vibes":       ["Formal", "Modern"],
                "description": "You walk into rooms and people notice. Your wardrobe is armour — structured blazers, sharp trousers, and jewellery that carries authority. You dress with intention and it shows.",
            },
        }

    # ─────────────────────────────────────────────────────────
    # METHOD: _get_db_connection
    # Opens a connection to the SQLite database
    # ─────────────────────────────────────────────────────────
    def _get_db_connection(self):
        """
        Opens a connection to inventory.db.
        conn.row_factory = sqlite3.Row makes results behave like dicts.
        """
        conn = sqlite3.connect(DB_PATH)        # open the database file
        conn.row_factory = sqlite3.Row         # so we can use row["column_name"]
        return conn

    # ─────────────────────────────────────────────────────────
    # METHOD: _get_user_profile
    # Reads the user's basic info from the user_profile table
    # ─────────────────────────────────────────────────────────
    def _get_user_profile(self, cursor, user_id):
        """Fetches one row from user_profile for the given user_id."""
        cursor.execute(
            "SELECT * FROM user_profile WHERE user_id = ?",
            (user_id,)  # the comma makes this a tuple — required by sqlite3
        )
        row = cursor.fetchone()  # fetchone() returns the first matching row, or None
        return dict(row) if row else {}  # convert Row object to a plain Python dict

    # ─────────────────────────────────────────────────────────
    # METHOD: _analyse_purchases
    # Looks at all purchase history rows and finds patterns
    # ─────────────────────────────────────────────────────────
    def _analyse_purchases(self, cursor, user_id):
        """
        Reads purchase_history and computes:
        - top 3 most purchased colours
        - top 3 most purchased vibes (Ethnic, Modern, etc.)
        - average order value (how much they spend on average)
        - preferred fabrics based on what they've bought most
        """
        # Fetch all purchase rows for this user
        cursor.execute(
            "SELECT colour, vibe, price, fabric, category FROM purchase_history WHERE user_id = ?",
            (user_id,)
        )
        rows = cursor.fetchall()  # fetchall() returns a list of all matching rows

        if not rows:
            # No purchase history found — return safe defaults
            return {
                "most_purchased_colours": ["Ivory", "Black", "Navy"],
                "most_purchased_vibes":   ["Modern"],
                "average_order_value":    5000,
                "preferred_fabrics":      ["Cotton", "Silk", "Georgette"],
                "most_bought_category":   "Dress",
            }

        # ── Count how many times each colour appears ──────────
        colour_count   = {}  # dictionary: colour → how many times bought
        vibe_count     = {}  # dictionary: vibe → how many times bought
        fabric_count   = {}  # dictionary: fabric → how many times bought
        category_count = {}  # dictionary: category → how many times bought
        total_spent    = 0   # running total for average calculation

        for row in rows:
            # Colour counting
            colour = row["colour"]
            colour_count[colour] = colour_count.get(colour, 0) + 1

            # Vibe counting
            vibe = row["vibe"]
            vibe_count[vibe] = vibe_count.get(vibe, 0) + 1

            # Fabric counting
            fabric = row["fabric"]
            fabric_count[fabric] = fabric_count.get(fabric, 0) + 1

            # Category counting
            category = row["category"]
            category_count[category] = category_count.get(category, 0) + 1

            # Add to total spent
            total_spent += row["price"]

        # Sort each dictionary by count (highest first) and take top items
        top_colours   = sorted(colour_count,   key=colour_count.get,   reverse=True)[:3]
        top_vibes     = sorted(vibe_count,     key=vibe_count.get,     reverse=True)[:2]
        top_fabrics   = sorted(fabric_count,   key=fabric_count.get,   reverse=True)[:3]
        top_category  = sorted(category_count, key=category_count.get, reverse=True)[0]

        # Calculate average order value
        average_spend = round(total_spent / len(rows), 2)

        return {
            "most_purchased_colours": top_colours,
            "most_purchased_vibes":   top_vibes,
            "average_order_value":    average_spend,
            "preferred_fabrics":      top_fabrics,
            "most_bought_category":   top_category,
        }

    # ─────────────────────────────────────────────────────────
    # METHOD: _analyse_browsing
    # Looks at browsing logs to find wishlist saving patterns
    # ─────────────────────────────────────────────────────────
    def _analyse_browsing(self, cursor, user_id):
        """
        Reads browsing_logs to find:
        - categories the user spends the most time looking at
        - which colours appear in their wishlist
        """
        cursor.execute(
            "SELECT category, colour, saved_to_wishlist, time_spent_seconds "
            "FROM browsing_logs WHERE user_id = ?",
            (user_id,)
        )
        rows = cursor.fetchall()

        if not rows:
            return {"most_browsed_category": "Dress", "wishlist_colours": []}

        category_time_map = {}  # track total time spent per category
        wishlist_colours  = []  # colours from items saved to wishlist

        for row in rows:
            # Count time spent per category
            cat = row["category"]
            category_time_map[cat] = category_time_map.get(cat, 0) + row["time_spent_seconds"]

            # If item was wishlisted, note the colour
            if row["saved_to_wishlist"] == 1:
                wishlist_colours.append(row["colour"])

        # Find the category with the most total browse time
        most_browsed = max(category_time_map, key=category_time_map.get)

        return {
            "most_browsed_category": most_browsed,
            "wishlist_colours": wishlist_colours,
        }

    # ─────────────────────────────────────────────────────────
    # METHOD: _assign_persona
    # Looks at the computed vibes and picks the best-matching persona
    # ─────────────────────────────────────────────────────────
    def _assign_persona(self, most_purchased_vibes, average_order_value):
        """
        Picks the ONE persona that best matches the user's purchase vibe pattern.
        Falls back to "Minimalist Professional" if nothing matches well.
        """
        best_persona_name = "Minimalist Professional"  # default
        best_match_count  = 0  # how many vibe matches did we find?

        for persona_name, persona_info in self.persona_definitions.items():
            # Count how many of the user's top vibes match this persona's vibes
            match_count = sum(
                1 for vibe in most_purchased_vibes
                if vibe in persona_info["vibes"]
            )
            if match_count > best_match_count:
                best_match_count  = match_count
                best_persona_name = persona_name  # update our best match

        # Special case: if they spend a lot of money, they might be a Maximalist Diva
        if average_order_value > 12000 and "Ethnic" in most_purchased_vibes:
            best_persona_name = "Maximalist Diva"

        return best_persona_name

    # ─────────────────────────────────────────────────────────
    # METHOD: run — THE MAIN ENTRY POINT
    # ─────────────────────────────────────────────────────────
    def run(self, user_id=1):
        """
        Reads database data, computes the user persona, and returns
        a complete profile dictionary.

        user_id: which user to analyse (default is 1 = Priya Sharma)
        Returns: dict with all persona info
        """
        print("  👤 Persona Agent: Analysing your style history...")

        # Open the database connection
        conn   = self._get_db_connection()
        cursor = conn.cursor()

        # Gather data from all 3 tables
        profile    = self._get_user_profile(cursor, user_id)
        purchases  = self._analyse_purchases(cursor, user_id)
        browsing   = self._analyse_browsing(cursor, user_id)

        # Close the connection — always good practice
        conn.close()

        # Assign the style persona based on purchase patterns
        persona_name = self._assign_persona(
            purchases["most_purchased_vibes"],
            purchases["average_order_value"]
        )

        # Decide which colours to AVOID based on skin undertone
        skin_tone     = profile.get("skin_undertone", "warm")
        avoided_map   = {
            "warm":    ["Slate Grey", "Icy Blue", "Ash"],  # warm skin tones avoid very cool greys
            "cool":    ["Mustard Yellow", "Rust", "Camel"],  # cool tones avoid very warm earthy tones
            "neutral": ["Neon Green", "Fluorescent Yellow", "Hot Pink"],  # neutrals avoid neons
        }
        avoided_colours = avoided_map.get(skin_tone, ["Neon Green"])

        # Build the final persona profile dictionary
        persona_profile = {
            "user_id":            user_id,
            "name":               profile.get("name", "Valued Customer"),
            "persona_name":       persona_name,
            "persona_description": self.persona_definitions[persona_name]["description"],
            "favourite_colours":  (
                purchases["most_purchased_colours"]
                + browsing["wishlist_colours"]
            )[:5],  # top 5 colours combined from purchases + wishlist
            "avoided_colours":    avoided_colours,
            "body_type":          profile.get("body_type", "Hourglass"),
            "skin_undertone":     skin_tone,  # warm / cool / neutral
            "size":               profile.get("size", "M"),
            "budget_min":         profile.get("budget_min", 2000),
            "budget_max":         profile.get("budget_max", 20000),
            "preferred_fabrics":  purchases["preferred_fabrics"],
            "average_order_value": purchases["average_order_value"],
            "most_browsed_category": browsing["most_browsed_category"],
        }

        print(f"  ✅ Persona assigned: {persona_name}")
        return persona_profile  # return the dict for other agents to use
