"""
main.py — Pipeline Orchestration & Entry Point
Orchestrates: User Input → Trend Scout → Customer Persona → Wardrobe Architect → Output
With threaded execution for non-blocking GUI updates and feedback loop support.
"""

from __future__ import annotations
import sys
import os

# Ensure scripts directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state_schema import StyleState
from setup_db import initialize_database, DB_PATH
from trend_scout_agent import TrendScoutAgent
from customer_persona_agent import CustomerPersonaAgent
from wardrobe_architect_agent import WardrobeArchitectAgent
from feedback_loop import FeedbackHandler


class StyleOrchestrator:
    """
    Main orchestrator for the multi-agent pipeline.
    Manages state handoff: Trend Scout → Customer Persona → Wardrobe Architect
    """

    def __init__(self):
        self.trend_scout = TrendScoutAgent()
        self.customer_persona = CustomerPersonaAgent()
        self.wardrobe_architect = WardrobeArchitectAgent()
        self.feedback_handler = FeedbackHandler()
        self.state = StyleState()

        # Initialize database if needed
        if not os.path.exists(DB_PATH):
            initialize_database()

    def run_pipeline(
        self,
        user_query: str = "",
        occasion: str = "wedding",
        sub_occasion: str = "",
        gender: str = "female",
        budget: float = 15000,
        region: str = "",
        user_id: int = 1,
    ) -> StyleState:
        """
        Run the full multi-agent pipeline.
        Returns the completed StyleState with curated outfit.
        """
        print("\n" + "═" * 60)
        print("  🎯 STYLE ORCHESTRATOR — Starting Pipeline")
        print("═" * 60)
        print(f"  Query: {user_query}")
        print(f"  Occasion: {occasion} | Gender: {gender} | Budget: ₹{budget:,.0f}")
        if region:
            print(f"  Region: {region}")
        print("═" * 60)

        # Initialize state
        self.state = StyleState(
            occasion=occasion,
            sub_occasion=sub_occasion,
            gender=gender,
            budget=budget,
            region=region,
            user_query=user_query,
        )

        # ── STEP A: Trend Scout ──
        self.state = self.trend_scout.run(self.state)

        # ── STEP B: Customer Persona ──
        self.state = self.customer_persona.run(self.state, user_id=user_id)

        # ── STEP C: Wardrobe Architect ──
        self.state = self.wardrobe_architect.curate(self.state)

        # ── OUTPUT ──
        lookbook = self.wardrobe_architect.format_lookbook(self.state)
        print("\n" + lookbook)

        # Dashboard format
        dashboard = self.state.to_dashboard_format()
        print("\n📊 Dashboard Data:", dashboard)

        return self.state

    def process_feedback(self, feedback_text: str) -> StyleState:
        """
        Process user feedback and re-curate.
        The feedback loop resets appropriate state and re-runs the Wardrobe Architect.
        """
        print("\n" + "═" * 60)
        print("  🔄 FEEDBACK RECEIVED — Re-curating...")
        print("═" * 60)

        self.state, action = self.feedback_handler.process(feedback_text, self.state)

        # Re-run the Wardrobe Architect with updated state
        self.state = self.wardrobe_architect.curate(self.state)

        lookbook = self.wardrobe_architect.format_lookbook(self.state)
        print("\n" + lookbook)

        return self.state

    def get_lookbook(self) -> str:
        """Get the current lookbook as formatted text."""
        return self.wardrobe_architect.format_lookbook(self.state)


def run_demo():
    """Run a demo of the full pipeline."""
    orchestrator = StyleOrchestrator()

    # Demo 1: Sangeet in Pune
    print("\n" + "🌟" * 30)
    print("  DEMO: Sangeet outfit for Pune wedding")
    print("🌟" * 30)

    state = orchestrator.run_pipeline(
        user_query="I need a royal look for my brother's Sangeet in Pune, budget 15k",
        occasion="sangeet",
        gender="female",
        budget=15000,
        region="pune",
        user_id=3,  # Zara — Fusion Explorer
    )

    # Demo 2: Process feedback
    print("\n\n" + "🌟" * 30)
    print("  FEEDBACK: 'Too heavy, I want something lighter'")
    print("🌟" * 30)

    state = orchestrator.process_feedback("Too heavy, I want something lighter")

    # Demo 3: Corporate look for Arjun
    print("\n\n" + "🌟" * 30)
    print("  DEMO: Corporate look for Delhi")
    print("🌟" * 30)

    state = orchestrator.run_pipeline(
        user_query="Need a sharp look for a corporate lunch in Delhi",
        occasion="corporate",
        gender="male",
        budget=12000,
        region="delhi",
        user_id=2,  # Arjun — Minimalist Professional
    )


def main():
    """Entry point — launch GUI or run demo."""
    if "--demo" in sys.argv:
        run_demo()
    else:
        # Launch the GUI
        try:
            from gui_agent import launch_gui
            launch_gui()
        except ImportError as e:
            print(f"GUI dependencies missing: {e}")
            print("Running demo mode instead...")
            print("Install with: pip install customtkinter Pillow")
            run_demo()


if __name__ == "__main__":
    main()
