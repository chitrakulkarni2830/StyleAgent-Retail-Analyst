"""
customer_persona_agent.py — Agent B: The 'Identity' Layer
Queries purchase_history and browsing_logs to calculate the user's "Style DNA".
Tags users as archetypes and identifies their dominant preferences.
"""

from __future__ import annotations
import sqlite3
import os

from state_schema import StyleState, UserStyleProfile


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "style_engine.db")


class CustomerPersonaAgent:
    """
    The Customer Persona Agent analyzes user behavior to build a Style DNA:
    1. Queries purchase history for dominant colors, fabrics, silhouettes
    2. Analyzes browsing logs for hidden interests
    3. Tags the user with a Style DNA archetype
    4. Updates state.user_style_profile
    """

    def __init__(self):
        self.db_path = DB_PATH

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def run(self, state: StyleState, user_id: int = 1) -> StyleState:
        """
        Execute the Customer Persona pipeline.
        Calculates Style DNA and updates state.user_style_profile.
        """
        state.current_step = "customer_persona"
        print(f"\n👤 CUSTOMER PERSONA — Analyzing User {user_id}...")
        print("─" * 50)

        conn = self._get_conn()

        # Step 1: Get user preferences
        user_prefs = self._get_user_preferences(conn, user_id)
        print(f"  📋 User: {user_prefs.get('name', 'Unknown')}")
        print(f"     Skin Tone: {user_prefs.get('skin_tone', 'neutral')}")
        print(f"     Size: {user_prefs.get('size', 'M')}")

        # Step 2: Analyze purchase history — dominant colors
        color_stats = self._analyze_color_history(conn, user_id)
        print(f"  🎨 Color Analysis:")
        for color, pct in list(color_stats.items())[:5]:
            print(f"     {color}: {pct:.1f}%")

        # Step 3: Analyze purchase history — dominant silhouettes
        silhouette_stats = self._analyze_silhouette_history(conn, user_id)
        print(f"  ✂️  Silhouette Preferences:")
        for style, pct in list(silhouette_stats.items())[:3]:
            print(f"     {style}: {pct:.1f}%")

        # Step 4: Analyze fabric affinity
        fabric_stats = self._analyze_fabric_affinity(conn, user_id)
        print(f"  🧵 Fabric Affinity:")
        for fabric, score in list(fabric_stats.items())[:3]:
            print(f"     {fabric}: {score}")

        # Step 5: Check browsing patterns for hidden interests
        browsing_insights = self._analyze_browsing(conn, user_id)
        if browsing_insights:
            print(f"  👁️  Browsing Insights: Curious about {', '.join(browsing_insights[:3])}")

        # Step 6: Calculate Style DNA
        style_dna = self._calculate_style_dna(color_stats, silhouette_stats, user_prefs)
        print(f"\n  🧬 Style DNA: \"{style_dna}\"")

        # Step 7: Build the profile
        dominant_colors = list(color_stats.keys())[:5] if color_stats else ["Black", "White", "Navy Blue"]
        budget_str = user_prefs.get("budget_range", "5000-30000")
        budget_parts = budget_str.split("-")
        budget_tuple = (float(budget_parts[0]), float(budget_parts[1])) if len(budget_parts) == 2 else (5000, 30000)

        profile = UserStyleProfile(
            user_id=user_id,
            dominant_colors=dominant_colors,
            dominant_colors_pct=color_stats,
            preferred_silhouettes=list(silhouette_stats.keys())[:3] if silhouette_stats else ["Straight", "Classic"],
            preferred_fabrics=list(fabric_stats.keys())[:3] if fabric_stats else ["Cotton", "Linen"],
            style_dna=style_dna or "Minimalist Professional",
            size=user_prefs.get("size", "M"),
            skin_tone=user_prefs.get("skin_tone", "neutral"),
            primary_colors=dominant_colors[:3],
            budget_range=budget_tuple,
        )

        state.user_style_profile = profile
        conn.close()
        print("─" * 50)
        return state

    def _get_user_preferences(self, conn: sqlite3.Connection, user_id: int) -> dict:
        """Fetch stored user preferences."""
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {"name": "Guest", "skin_tone": "neutral", "size": "M", "budget_range": "5000-30000"}

    def _analyze_color_history(self, conn: sqlite3.Connection, user_id: int) -> dict[str, float]:
        """Analyze dominant colors from purchase history."""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT color, COUNT(*) as cnt,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM purchase_history WHERE user_id = ?), 1) as pct
            FROM purchase_history
            WHERE user_id = ?
            GROUP BY color
            ORDER BY cnt DESC
        """, (user_id, user_id))

        return {row["color"]: row["pct"] for row in cursor.fetchall()}

    def _analyze_silhouette_history(self, conn: sqlite3.Connection, user_id: int) -> dict[str, float]:
        """Analyze preferred silhouettes/styles from purchase history."""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT style_tag, COUNT(*) as cnt,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM purchase_history WHERE user_id = ?), 1) as pct
            FROM purchase_history
            WHERE user_id = ?
            GROUP BY style_tag
            ORDER BY cnt DESC
        """, (user_id, user_id))

        return {row["style_tag"]: row["pct"] for row in cursor.fetchall()}

    def _analyze_fabric_affinity(self, conn: sqlite3.Connection, user_id: int) -> dict[str, int]:
        """Analyze fabric preferences from browsing + purchases."""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.fabric, SUM(bl.view_count) as total_views
            FROM browsing_logs bl
            JOIN current_inventory ci ON bl.sku = ci.sku
            WHERE bl.user_id = ?
            GROUP BY ci.fabric
            ORDER BY total_views DESC
        """, (user_id,))

        return {row["fabric"]: row["total_views"] for row in cursor.fetchall()}

    def _analyze_browsing(self, conn: sqlite3.Connection, user_id: int) -> list[str]:
        """Find items the user browses but hasn't purchased — hidden interests."""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.name, ci.color_family, bl.view_count
            FROM browsing_logs bl
            JOIN current_inventory ci ON bl.sku = ci.sku
            WHERE bl.user_id = ?
              AND bl.sku NOT IN (SELECT sku FROM purchase_history WHERE user_id = ?)
            ORDER BY bl.view_count DESC
            LIMIT 5
        """, (user_id, user_id))

        return [f"{row['name']} ({row['color_family']})" for row in cursor.fetchall()]

    def _calculate_style_dna(
        self,
        color_stats: dict[str, float],
        silhouette_stats: dict[str, float],
        user_prefs: dict,
    ) -> str:
        """
        Calculate the Style DNA archetype based on purchase patterns.
        Logic: Analyze dominant colors, silhouettes, and saved preferences.
        """
        # Check if there's a saved Style DNA
        saved_dna = user_prefs.get("saved_style_dna", "")
        if saved_dna:
            return saved_dna

        # Calculate from purchase patterns
        top_colors = list(color_stats.keys())[:3]
        top_styles = list(silhouette_stats.keys())[:2]

        # Scoring heuristics
        traditional_score = 0
        modern_score = 0
        fusion_score = 0
        minimal_score = 0

        traditional_markers = {"Maroon", "Emerald Green", "Gold", "Red", "Royal Purple"}
        neutral_markers = {"Black", "White", "Navy Blue", "Neutral Grey", "Beige", "Ivory"}
        pastel_markers = {"Lavender", "Mint", "Peach", "Pastel Pink", "Coral"}
        traditional_styles = {"Traditional", "Ethnic", "Draped"}
        modern_styles = {"Slim Fit", "Modern", "Classic"}
        fusion_styles = {"Fusion", "Pre-Draped", "Crop"}

        for color in top_colors:
            if color in traditional_markers:
                traditional_score += 2
            if color in neutral_markers:
                minimal_score += 2
            if color in pastel_markers:
                fusion_score += 2

        for style in top_styles:
            if style in traditional_styles:
                traditional_score += 3
            if style in modern_styles:
                modern_score += 3
            if style in fusion_styles:
                fusion_score += 3

        scores = {
            "Bold Traditionalist": traditional_score,
            "Minimalist Professional": minimal_score + modern_score,
            "Fusion Explorer": fusion_score,
            "Ethnic Minimalist": minimal_score + traditional_score // 2,
            "Regal Maximalist": traditional_score + 1 if traditional_score > 5 else 0,
        }

        return max(scores, key=scores.get)
