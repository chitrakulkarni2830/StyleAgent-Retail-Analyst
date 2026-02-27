"""
feedback_loop.py — Refinement & Feedback Handler
Processes user feedback (reject, change color, too heavy, cheaper, etc.)
and triggers re-curation by updating the StyleState.
"""

from __future__ import annotations
import re
from state_schema import StyleState


# ═══════════════════════════════════════════════════════════════
#  FEEDBACK KEYWORDS & RULES
# ═══════════════════════════════════════════════════════════════

FEEDBACK_PATTERNS = {
    "too_heavy": {
        "keywords": ["too heavy", "lighter", "lightweight", "breathable", "less heavy", "too warm"],
        "action": "swap_to_lighter_fabric",
        "description": "Swap to lighter fabric alternatives",
    },
    "too_bright": {
        "keywords": ["too bright", "more subtle", "toned down", "muted", "less vibrant", "pastel"],
        "action": "shift_to_neutral_palette",
        "description": "Shift to analogous/monochromatic palette",
    },
    "cheaper": {
        "keywords": ["cheaper", "less expensive", "budget", "affordable", "low cost", "too expensive"],
        "action": "reduce_budget",
        "description": "Lower budget tier and re-filter",
    },
    "bolder": {
        "keywords": ["bolder", "more vibrant", "brighter", "pop of color", "stand out", "louder"],
        "action": "shift_to_bold_palette",
        "description": "Shift to complementary/bold palette",
    },
    "change_color": {
        "keywords": ["make it", "change to", "prefer", "in red", "in blue", "in green", "more blue", "more red"],
        "action": "change_primary_color",
        "description": "Change the primary color of the outfit",
    },
    "more_traditional": {
        "keywords": ["more traditional", "more ethnic", "heavier", "more indian", "classic look"],
        "action": "shift_to_traditional",
        "description": "Shift to heavier traditional options",
    },
    "more_modern": {
        "keywords": ["more modern", "fusion", "indo-western", "contemporary", "western"],
        "action": "shift_to_modern",
        "description": "Shift to modern/fusion options",
    },
    "reject": {
        "keywords": ["don't like", "no", "reject", "try again", "something else", "different"],
        "action": "full_re_curate",
        "description": "Full re-curation with secondary trends",
    },
}

# Color extraction patterns
COLOR_NAMES = [
    "red", "blue", "green", "yellow", "black", "white", "gold", "silver",
    "maroon", "navy", "teal", "coral", "peach", "lavender", "mint", "pink",
    "purple", "orange", "ivory", "beige", "cobalt", "emerald", "wine",
]

COLOR_MAP = {
    "red": "Red", "blue": "Cobalt Blue", "green": "Emerald Green",
    "yellow": "Mustard Yellow", "black": "Black", "white": "White",
    "gold": "Gold", "silver": "Silver", "maroon": "Maroon",
    "navy": "Navy Blue", "teal": "Teal", "coral": "Coral",
    "peach": "Peach", "lavender": "Lavender", "mint": "Mint",
    "pink": "Pastel Pink", "purple": "Royal Purple", "orange": "Coral",
    "ivory": "Ivory", "beige": "Beige", "cobalt": "Cobalt Blue",
    "emerald": "Emerald Green", "wine": "Deep Wine",
}


class FeedbackHandler:
    """
    Processes user feedback and updates StyleState for re-curation.
    Keyword-based detection triggers specific state modifications.
    """

    def process(self, feedback_text: str, state: StyleState) -> tuple[StyleState, str]:
        """
        Process feedback and return updated state + action description.
        Returns (updated_state, action_description)
        """
        feedback_lower = feedback_text.lower().strip()
        state.feedback_history.append(feedback_text)

        # Detect feedback type
        matched_action = None
        for pattern_name, pattern_info in FEEDBACK_PATTERNS.items():
            for keyword in pattern_info["keywords"]:
                if keyword in feedback_lower:
                    matched_action = pattern_info
                    break
            if matched_action:
                break

        if not matched_action:
            matched_action = FEEDBACK_PATTERNS["reject"]

        action = matched_action["action"]
        description = matched_action["description"]

        print(f"\n🔄 FEEDBACK LOOP — Detected: {description}")
        print(f"   Action: {action}")

        # Execute the action
        if action == "swap_to_lighter_fabric":
            state = self._swap_lighter(state)
        elif action == "shift_to_neutral_palette":
            state = self._shift_neutral(state)
        elif action == "reduce_budget":
            state = self._reduce_budget(state)
        elif action == "shift_to_bold_palette":
            state = self._shift_bold(state)
        elif action == "change_primary_color":
            color = self._extract_color(feedback_lower)
            state = self._change_color(state, color)
            description += f" → {color}" if color else ""
        elif action == "shift_to_traditional":
            state = self._shift_traditional(state)
        elif action == "shift_to_modern":
            state = self._shift_modern(state)
        elif action == "full_re_curate":
            state = self._full_re_curate(state)

        # Mark rejected SKUs
        if state.final_recommendation:
            for item in state.final_recommendation.outfit_items:
                if item.sku not in state.rejected_skus:
                    state.rejected_skus.append(item.sku)

        # Reset for re-curation
        state.reset_for_refinement()

        return state, description

    def _swap_lighter(self, state: StyleState) -> StyleState:
        """Swap fabric preferences to lighter alternatives."""
        if state.trend_brief:
            light_fabrics = ["Chiffon", "Georgette", "Cotton", "Linen", "Chanderi Silk", "Organza"]
            state.trend_brief.key_fabrics = light_fabrics[:4]
        return state

    def _shift_neutral(self, state: StyleState) -> StyleState:
        """Shift palette to more subtle/neutral colors."""
        if state.trend_brief:
            neutral_pastels = ["Ivory", "Lavender", "Mint", "Peach", "Beige"]
            state.trend_brief.trending_colors = neutral_pastels
        return state

    def _reduce_budget(self, state: StyleState) -> StyleState:
        """Reduce budget by 30%."""
        state.budget = state.budget * 0.7
        print(f"   Budget adjusted to: ₹{state.budget:,.0f}")
        return state

    def _shift_bold(self, state: StyleState) -> StyleState:
        """Shift palette to bolder colors."""
        if state.trend_brief:
            bold_colors = ["Cobalt Blue", "Emerald Green", "Red", "Electric Indigo", "Magenta"]
            state.trend_brief.trending_colors = bold_colors
        return state

    def _change_color(self, state: StyleState, color: str) -> StyleState:
        """Change primary trending color."""
        if color and state.trend_brief:
            state.trend_brief.trending_colors = [color] + [
                c for c in state.trend_brief.trending_colors if c != color
            ][:4]
        return state

    def _shift_traditional(self, state: StyleState) -> StyleState:
        """Shift to heavier, traditional options."""
        if state.trend_brief:
            state.trend_brief.key_fabrics = ["Kanjeevaram Silk", "Banarasi Silk", "Velvet", "Raw Silk"]
            state.trend_brief.must_have_silhouette = ["Draped", "Structured", "Flared"]
        return state

    def _shift_modern(self, state: StyleState) -> StyleState:
        """Shift to modern/fusion options."""
        if state.trend_brief:
            state.trend_brief.key_fabrics = ["Organza", "Sequin Georgette", "Cotton Blend", "Linen"]
            state.trend_brief.must_have_silhouette = ["Pre-Draped", "Slim Fit", "Crop"]
        return state

    def _full_re_curate(self, state: StyleState) -> StyleState:
        """Full re-curation — use secondary trends."""
        if state.trend_brief and len(state.trend_brief.trending_colors) > 2:
            # Rotate colors: move primary to back
            colors = state.trend_brief.trending_colors
            state.trend_brief.trending_colors = colors[2:] + colors[:2]
        return state

    def _extract_color(self, text: str) -> str:
        """Extract a color name from feedback text."""
        for color_keyword in COLOR_NAMES:
            if color_keyword in text:
                return COLOR_MAP.get(color_keyword, "Cobalt Blue")
        return ""
