"""
=============================================================
workflow/crewai_crew.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This file defines a CrewAI crew — think of it as assigning
  JOB TITLES and RESPONSIBILITIES to each agent.

  CrewAI is an AI orchestration framework. It gives each agent:
    - A ROLE (their job title)
    - A GOAL (what they are trying to achieve)
    - A BACKSTORY (their "character" — helps the AI reason better)
    - A TASK (the specific work to do right now)

  Then it runs them all in sequence and combines the results.

  NOTE: CrewAI works best when using an LLM (like Ollama llama3).
  If CrewAI is not installed or Ollama is not running, this module
  provides a fallback that uses our LangGraph pipeline instead.

HOW TO USE:
  from workflow.crewai_crew import run_crew
  result = run_crew(user_input_dict)
=============================================================
"""

import os    # built-in: for file path building
import sys   # built-in: for modifying the module search path

# ── Add the project root to Python's search path ──────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)  # so "from agents.xxx import ..." works

# ── Try to import CrewAI ──────────────────────────────────────
# CrewAI is an optional framework — we fall back if not installed
try:
    from crewai import Agent, Task, Crew, Process  # the CrewAI framework
    CREWAI_AVAILABLE = True
    print("  ✅ CrewAI imported successfully")
except ImportError:
    CREWAI_AVAILABLE = False  # CrewAI not installed
    print("  ⚠️  CrewAI not found — run_crew() will use the LangGraph fallback")

# ── Import all 5 agent classes ─────────────────────────────────
from agents.trend_scout_agent        import TrendScoutAgent
from agents.persona_agent            import PersonaAgent
from agents.colour_engine_agent      import ColourEngineAgent
from agents.wardrobe_architect_agent import WardrobeArchitectAgent
from agents.jewellery_agent          import JewelleryAgent


# =============================================================
# FUNCTION: build_crew
# Creates 5 CrewAI Agents and 5 CrewAI Tasks, then returns a Crew
# =============================================================
def build_crew(user_input_dict: dict):
    """
    Creates and returns a CrewAI Crew configured with all 5 agents.
    Each agent has a role, goal, backstory, and task.

    user_input_dict: the user's selections from the GUI
    Returns: a Crew object ready to run
    """
    if not CREWAI_AVAILABLE:
        raise ImportError("CrewAI is not installed. Use run_crew() which handles the fallback.")

    # ── Extract user context from the input ──────────────────
    occasion = user_input_dict.get("occasion", "wedding")
    vibe     = user_input_dict.get("vibe", "Ethnic")
    size     = user_input_dict.get("size", "M")

    # =============================================================
    # DEFINE 5 CREWAI AGENT OBJECTS
    # Each "Agent" here is a CrewAI descriptor — NOT the same as
    # our Python agent classes above. CrewAI wraps them with LLM power.
    # =============================================================

    trend_agent = Agent(
        role        = "Fashion Trend Analyst for India 2026",
        goal        = (
            "Discover and report the most current 2026 Spring-Summer fashion trends "
            "from Indian fashion media sources. Identify trending colours with HEX codes, "
            "trending silhouettes, jewellery styles, and overall season vibes."
        ),
        backstory   = (
            "You are a veteran fashion editor who has covered Indian fashion weeks "
            "for 15 years. You have an infallible eye for what is about to become the "
            "next big thing, and your colour trend forecasts are trusted by every major "
            "Indian designer house. You read Vogue India, Elle India, and NYKAA editorial "
            "every morning before your first cup of chai."
        ),
        verbose     = True,           # print agent thoughts as it works
        allow_delegation = False,     # this agent works alone, no passing work to others
    )

    persona_agent = Agent(
        role        = "Personal Style Profiler and Customer Analyst",
        goal        = (
            "Analyse the customer's complete purchase history and browsing behaviour "
            "to build a precise, accurate style persona. Identify the correct persona "
            "from 8 defined archetypes and compute the customer's true colour preferences, "
            "fabric preferences, and budget range from real data."
        ),
        backstory   = (
            "You started your career as a retail data analyst at a leading fashion e-commerce "
            "platform in Mumbai. You understand that what people BUY tells the truth, while "
            "what they BROWSE reveals their aspirational self. You specialise in bridging that "
            "gap to create styling profiles that feel uncannily accurate."
        ),
        verbose     = True,
        allow_delegation = False,
    )

    colour_agent = Agent(
        role        = "Certified Colour Theory Expert and Wardrobe Colour Consultant",
        goal        = (
            "Generate 3 beautifully harmonious colour palettes — Option A, B, and C — "
            "using scientific colour wheel mathematics and Indian skin undertone rules. "
            "Each palette must include a primary, secondary, and accent colour with HEX codes, "
            "plus a written rationale explaining WHY it works."
        ),
        backstory   = (
            "You trained as a colour theorist at the National Institute of Fashion Technology "
            "and then went on to consult for Bollywood costume departments and Indian bridal "
            "stylists. You can explain the relationship between cobalt blue and warm skin tones "
            "in a way that even a complete beginner understands immediately. Your palettes are "
            "mathematically precise AND emotionally resonant."
        ),
        verbose     = True,
        allow_delegation = False,
    )

    wardrobe_agent = Agent(
        role        = "Senior Wardrobe Stylist and Outfit Architect",
        goal        = (
            "Build 3 complete, ready-to-wear outfit recommendations — one per colour palette. "
            "Every outfit must include: top, bottom or dress, outerwear, footwear, and bag. "
            "Every item description must be written at Gold Standard quality — "
            "specific fabric, silhouette, cut, and fit — never vague."
        ),
        backstory   = (
            "You have dressed leading actors and socialites for major occasions across India. "
            "You refuse to recommend an 'outfit' that isn't truly COMPLETE — you always think "
            "from head to toe. You know that a beautiful kurta without the right footwear is "
            "an incomplete thought. Your descriptions are detailed enough to walk into any store "
            "and find exactly what you mean."
        ),
        verbose     = True,
        allow_delegation = False,
    )

    jewellery_agent = Agent(
        role        = "Fine Jewellery Stylist and Accessories Expert",
        goal        = (
            "Match a complete Jewellery Kit — earrings, necklace, bangles, rings, "
            "optional tikka and extras — to each of the 3 outfits. Apply the skin undertone "
            "metal rule (warm = gold, cool = silver) and the neckline rule strictly. "
            "Also provide 2 styling tips and a fragrance recommendation per outfit."
        ),
        backstory   = (
            "You grew up around your family's jewellery business in Rajasthan, studying "
            "how different metals and stones interact with different skin tones in real light — "
            "not just on screen. You've advised clients from Mehendi ceremonies to black-tie "
            "galas. Your jewellery kits are always complete, always intentional, and always "
            "written in a language the client can actually understand and act on."
        ),
        verbose     = True,
        allow_delegation = False,
    )

    # =============================================================
    # DEFINE 5 CREWAI TASK OBJECTS
    # Each Task tells an Agent EXACTLY what to do and what to return.
    # =============================================================

    task_trend = Task(
        description     = (
            f"Scout the latest 2026 Spring-Summer fashion trends for Indian women's wear. "
            f"Scrape Vogue India, Elle India, and NYKAA fashion pages. "
            f"Return a JSON-like summary with: trending_colours (5 colours with HEX codes), "
            f"trending_outfits (5 silhouette descriptions), trending_jewellery (3 styles), "
            f"trending_vibes (3 mood descriptors), and the data source (web or fallback)."
        ),
        expected_output = (
            "A Python dictionary with keys: source, season, fetch_date, trending_colours, "
            "trending_outfits, trending_jewellery, trending_vibes."
        ),
        agent           = trend_agent,  # this task is assigned to the Trend Agent
    )

    task_persona = Task(
        description     = (
            f"Build a complete style persona profile for user ID 1 (Priya Sharma). "
            f"Read her purchase_history, browsing_logs, and user_profile from the SQLite database. "
            f"Assign ONE of these 8 personas based on her top vibes: "
            f"Minimalist Professional, Maximalist Diva, Boho Free Spirit, Classic Elegance, "
            f"Street Smart Casual, Ethnic Royale, Indo-Western Fusion, Power Dresser. "
            f"Return: persona_name, favourite_colours, avoided_colours, body_type, "
            f"skin_undertone, budget_min, budget_max, size, preferred_fabrics."
        ),
        expected_output = (
            "A Python dictionary with all persona fields including persona_name, "
            "skin_undertone, budget range, and top colour preferences."
        ),
        agent           = persona_agent,
    )

    task_colour = Task(
        description     = (
            f"Generate 3 colour palettes for the user's skin undertone (from persona profile). "
            f"Use real colour wheel mathematics: complementary, analogous, triadic, "
            f"monochromatic, and split complementary harmony methods. "
            f"The user is attending a {occasion} with a {vibe} vibe. "
            f"Label palettes Option A, Option B, Option C. "
            f"Each palette must include: harmony_type, primary_colour + HEX, "
            f"secondary_colour + HEX, accent_colour + HEX, and a colour_rationale."
        ),
        expected_output = "A Python list of 3 palette dictionaries, labelled Option A, B, C.",
        agent           = colour_agent,
    )

    task_wardrobe = Task(
        description     = (
            f"Build 3 complete outfits — one per colour palette — for a {occasion} occasion "
            f"with a {vibe} vibe. Size: {size}. "
            f"Query the current_inventory SQLite table for real items matching vibe, occasion, "
            f"size, and budget. "
            f"Each outfit must include: Top or Dress, Bottom, Outerwear, Footwear, and Bag. "
            f"Write every item description at Gold Standard quality — specific fabric, "
            f"silhouette, cut, and price. Include WHY_THIS_WORKS (3 sentences) and "
            f"2 OCCASION_NOTES per outfit."
        ),
        expected_output = "A Python list of 3 fully populated outfit dictionaries.",
        agent           = wardrobe_agent,
    )

    task_jewellery = Task(
        description     = (
            f"Create a complete Jewellery Kit for each of the 3 outfits. "
            f"The occasion is {occasion}, vibe is {vibe}. "
            f"Apply the metal rule from skin undertone (warm = gold, cool = silver, neutral = both). "
            f"Apply the neckline rule (V-neck = pendant, high-neck = skip necklace, etc.). "
            f"Each kit must include: EARRINGS, NECKLACE (or skip with reason), "
            f"BANGLES, RINGS, MAANG TIKKA (for ethnic/indo-western only), OPTIONAL EXTRAS. "
            f"Add 2 STYLING TIPS and a FRAGRANCE NOTE per kit."
        ),
        expected_output = "A Python list of 3 complete jewellery kit dictionaries.",
        agent           = jewellery_agent,
    )

    # =============================================================
    # CREATE THE CREW — bundle agents + tasks + run order
    # =============================================================
    crew = Crew(
        agents  = [trend_agent, persona_agent, colour_agent, wardrobe_agent, jewellery_agent],
        tasks   = [task_trend, task_persona, task_colour, task_wardrobe, task_jewellery],
        process = Process.sequential,  # run tasks one after another (not all at once)
        verbose = True,                # print CrewAI's internal reasoning steps
    )

    return crew  # return the fully configured crew


# =============================================================
# FUNCTION: run_crew — THE MAIN ENTRY POINT
# =============================================================
def run_crew(user_input_dict: dict) -> dict:
    """
    Attempts to run the full CrewAI crew pipeline.
    If CrewAI is not available or fails, falls back to the
    LangGraph pipeline in workflow/langgraph_state.py.

    user_input_dict: dict of user selections from the GUI
    Returns: a state dict with all agent outputs
    """
    print("\n" + "=" * 55)
    print("  🚀 CrewAI Crew Starting...")
    print("=" * 55)

    if CREWAI_AVAILABLE:
        try:
            # Build and run the CrewAI crew
            crew   = build_crew(user_input_dict)
            result = crew.kickoff()  # kickoff() starts all the tasks in sequence

            print("\n  ✅ CrewAI crew completed!")
            print("  ℹ️  Note: For full structured output (outfit cards etc.),")
            print("     the GUI also runs the LangGraph pipeline for reliable data.")

            # CrewAI returns a text summary — for the GUI we need structured data
            # so we ALSO run the LangGraph pipeline to get proper dicts and lists
            from workflow.langgraph_state import run_pipeline
            structured_result = run_pipeline(user_input_dict)

            # Add the CrewAI text summary into the result as a bonus field
            structured_result["crewai_summary"] = str(result)

            return structured_result

        except Exception as crew_error:
            # CrewAI failed (e.g. Ollama not running) — fall back gracefully
            print(f"\n  ⚠️   CrewAI error: {crew_error}")
            print("  🔄  Falling back to LangGraph pipeline...")

    else:
        print("  🔄  CrewAI not available — using LangGraph pipeline directly...")

    # ── FALLBACK: run via LangGraph pipeline ──────────────────
    from workflow.langgraph_state import run_pipeline
    return run_pipeline(user_input_dict)
