"""
=============================================================
workflow/langgraph_state.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This file is the BRAIN CONNECTOR of the entire project.
  It does two things:

  1. Defines StyleAgentState — a shared "notepad" (TypedDict)
     that all 5 agents read from and write to as they work.

  2. Builds a LangGraph StateGraph — think of it as a flowchart
     that sends data from one agent to the next, in order:
       Scout → Persona → Colour → Wardrobe → Jewellery

  LangGraph is a framework for building multi-step AI pipelines
  where each step can read what the previous steps wrote.

HOW TO USE:
  from workflow.langgraph_state import run_pipeline
  result = run_pipeline(user_input_dict)
=============================================================
"""

import sys          # built-in: used to modify the module search path
import os           # built-in: used for file path building
from typing import TypedDict, List  # built-in: for type hints

# ── Add the project root to sys.path so Python can find our agents
# This makes "from agents.trend_scout_agent import ..." work correctly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)  # insert at position 0 = highest priority

# ── Try to import LangGraph — if not installed, we use a simple fallback
try:
    from langgraph.graph import StateGraph, END  # the pipeline framework
    LANGGRAPH_AVAILABLE = True  # flag so we know if LangGraph is ready
    print("  ✅ LangGraph imported successfully")
except ImportError:
    # LangGraph not installed — we will use a plain Python fallback instead
    LANGGRAPH_AVAILABLE = False
    print("  ⚠️  LangGraph not found — using direct pipeline fallback")

# ── Import all 5 agent classes from their files
from agents.trend_scout_agent        import TrendScoutAgent          # Agent 1
from agents.persona_agent            import PersonaAgent             # Agent 2
from agents.colour_engine_agent      import ColourEngineAgent        # Agent 3
from agents.wardrobe_architect_agent import WardrobeArchitectAgent   # Agent 4
from agents.jewellery_agent          import JewelleryAgent           # Agent 5


# =============================================================
# StyleAgentState — the shared notepad passed between all agents
# =============================================================
class StyleAgentState(TypedDict):
    """
    A TypedDict is like a dictionary with labelled slots.
    Each agent reads inputs from this dict and writes outputs back.

    Think of it as a baton in a relay race — each runner (agent)
    picks it up, adds their contribution, and passes it forward.
    """
    user_input:           dict   # raw selections from the GUI (occasion, vibe, budget etc.)
    trend_brief:          dict   # output from Agent 1 — the trend report
    user_persona:         dict   # output from Agent 2 — the style persona profile
    colour_palettes:      list   # output from Agent 3 — 3 palette options
    outfit_options:       list   # output from Agent 4 — 3 complete outfit dicts
    jewellery_kits:       list   # output from Agent 5 — 3 jewellery kit dicts
    final_recommendations: list  # combined final output list (outfits + jewellery merged)
    error_log:            list   # any errors caught during execution (so app keeps running)
    total_budget:         int    # Upgrade 2: single total outfit budget from the GUI


# =============================================================
# NODE FUNCTIONS — one function per agent, one function per node
# Each node function:
#   - receives the current state dict
#   - runs its agent
#   - writes results back into the state
#   - returns the updated state
# =============================================================

def node_trend_scout(state: StyleAgentState) -> StyleAgentState:
    """
    Node 1: Runs the Trend Scout Agent.
    Scrapes live fashion trends (or uses fallback data).
    """
    print("\n  [1/5] 🌐  Trend Scout — Scouting 2026 trends...")
    try:
        # Create an instance of the agent and run it
        agent       = TrendScoutAgent()
        trend_data  = agent.run()  # returns a dict of trend info

        # Write the result into the shared state
        state["trend_brief"] = trend_data
        print("  [1/5] ✅  Trend Scout complete")

    except Exception as error:
        # Something went wrong — log the error and use an empty dict so the pipeline continues
        error_message = f"TrendScout failed: {str(error)}"
        state["error_log"].append(error_message)
        state["trend_brief"] = {}  # empty dict — other agents can handle missing data
        print(f"  [1/5] ⚠️   Trend Scout error: {error}")

    return state  # pass the updated state to the next node


def node_persona(state: StyleAgentState) -> StyleAgentState:
    """
    Node 2: Runs the Persona Agent.
    Reads purchase + browsing history and assigns a Style Persona.
    """
    print("\n  [2/5] 👤  Persona Agent — Building your style profile...")
    try:
        # Get the user_id from user_input, default to 1 if not provided
        user_id = state["user_input"].get("user_id", 1)

        agent        = PersonaAgent()
        persona_data = agent.run(user_id=user_id)  # returns profile dict

        # Override persona data with any GUI-provided values
        # (e.g. the user can set their own body type and budget in the GUI)
        gui_input     = state["user_input"]
        if gui_input.get("body_type"):
            persona_data["body_type"]     = gui_input["body_type"]
        if gui_input.get("skin_undertone"):
            persona_data["skin_undertone"] = gui_input["skin_undertone"]
        if gui_input.get("budget_min"):
            persona_data["budget_min"]    = gui_input["budget_min"]
        if gui_input.get("budget_max"):
            persona_data["budget_max"]    = gui_input["budget_max"]
        if gui_input.get("size"):
            persona_data["size"]          = gui_input["size"]

        state["user_persona"] = persona_data
        print("  [2/5] ✅  Persona Agent complete")

    except Exception as error:
        error_message = f"PersonaAgent failed: {str(error)}"
        state["error_log"].append(error_message)
        # Use safe defaults so the pipeline can still produce outfit suggestions
        # Upgrade 2: no longer using budget_min/budget_max — just total_budget
        state["user_persona"] = {
            "skin_undertone":    state["user_input"].get("skin_undertone", "warm"),
            "body_type":         state["user_input"].get("body_type", "Hourglass"),
            "size":              state["user_input"].get("size", "M"),
            "preferred_fabrics": ["Cotton", "Silk", "Georgette"],
            "persona_name":      "Ethnic Royale",
        }
        print(f"  [2/5] ⚠️   Persona Agent error: {error}")

    return state


def node_colour(state: StyleAgentState) -> StyleAgentState:
    """
    Node 3: Runs the Colour Engine Agent.
    Generates 3 colour palettes based on base colour + skin undertone.
    """
    print("\n  [3/5] 🎨  Colour Engine — Generating your palettes...")
    try:
        # Get the base colour from user selections in the GUI
        user_input      = state["user_input"]
        favourite_colours = user_input.get("favourite_colours", [])

        # Use the first selected colour as the base, default to terracotta
        base_hex = favourite_colours[0] if favourite_colours else "#C67C5A"

        # Get skin undertone from the persona profile
        skin_undertone = state["user_persona"].get("skin_undertone", "warm")

        # Get the user's harmony preference from the GUI
        harmony_pref = user_input.get("colour_harmony", "Surprise Me")

        agent    = ColourEngineAgent()
        palettes = agent.run(
            base_hex           = base_hex,
            skin_undertone     = skin_undertone,
            harmony_preference = harmony_pref
        )  # returns a list of 3 palette dicts

        state["colour_palettes"] = palettes
        print("  [3/5] ✅  Colour Engine complete")

    except Exception as error:
        error_message = f"ColourEngine failed: {str(error)}"
        state["error_log"].append(error_message)
        # Fallback: a hardcoded set of palettes so the app keeps running
        state["colour_palettes"] = [
            {
                "harmony_type": "Analogous", "primary_colour": "Terracotta",
                "primary_hex": "#C67C5A", "secondary_colour": "Rust",
                "secondary_hex": "#B7410E", "accent_colour": "Peach",
                "accent_hex": "#FFCBA4",
                "colour_rationale": "Earthy terracotta tones that flatter warm undertones beautifully."
            },
            {
                "harmony_type": "Triadic", "primary_colour": "Terracotta",
                "primary_hex": "#C67C5A", "secondary_colour": "Cobalt Blue",
                "secondary_hex": "#0047AB", "accent_colour": "Sage Green",
                "accent_hex": "#B2AC88",
                "colour_rationale": "Bold triadic combination — terracotta anchors cobalt and sage perfectly."
            },
            {
                "harmony_type": "Split Complementary", "primary_colour": "Terracotta",
                "primary_hex": "#C67C5A", "secondary_colour": "Teal",
                "secondary_hex": "#008080", "accent_colour": "Ivory",
                "accent_hex": "#FFFFF0",
                "colour_rationale": "Sophisticated pairing with natural warmth and cool depth."
            }
        ]
        print(f"  [3/5] ⚠️   Colour Engine error: {error}")

    return state


def node_wardrobe(state: StyleAgentState) -> StyleAgentState:
    """
    Node 4: Runs the Wardrobe Architect Agent.
    Queries the inventory database and builds 3 complete outfits.
    Upgrade 2: now passes total_budget so the agent can distribute
    spending across pieces rather than applying one flat budget.
    """
    print("\n  [4/5] 👗  Wardrobe Architect — Building your outfits...")
    try:
        user_input   = state["user_input"]
        occasion     = user_input.get("occasion", "festival")
        vibe         = user_input.get("vibe", "Ethnic")

        # Upgrade 2: read total_budget from state (set by the GUI via _on_generate)
        # Fall back to 15000 if not set, so the app never crashes
        total_budget = state.get("total_budget",
                       user_input.get("total_budget", 15000))

        agent   = WardrobeArchitectAgent()
        outfits = agent.run(
            palettes     = state["colour_palettes"],
            persona      = state["user_persona"],
            occasion     = occasion,
            vibe         = vibe,
            total_budget = total_budget,   # Upgrade 2: pass the full outfit budget
        )  # returns list of 3 outfit dicts

        state["outfit_options"] = outfits
        print("  [4/5] ✅  Wardrobe Architect complete")

    except Exception as error:
        error_message = f"WardrobeArchitect failed: {str(error)}"
        state["error_log"].append(error_message)
        state["outfit_options"] = []  # empty — GUI will show a "no results" message
        print(f"  [4/5] ⚠️   Wardrobe Architect error: {error}")

    return state


def node_jewellery(state: StyleAgentState) -> StyleAgentState:
    """
    Node 5: Runs the Jewellery Agent.
    Matches a complete jewellery kit to each of the 3 outfits.
    """
    print("\n  [5/5] 💎  Jewellery Agent — Matching your jewellery...")
    try:
        user_input     = state["user_input"]
        skin_undertone = state["user_persona"].get("skin_undertone", "warm")
        occasion       = user_input.get("occasion", "festival")
        vibe           = user_input.get("vibe", "Ethnic")

        agent          = JewelleryAgent()
        jewellery_kits = agent.run(
            outfits        = state["outfit_options"],
            skin_undertone = skin_undertone,
            occasion       = occasion,
            vibe           = vibe
        )  # returns list of 3 jewellery kit dicts

        state["jewellery_kits"] = jewellery_kits
        print("  [5/5] ✅  Jewellery Agent complete")

    except Exception as error:
        error_message = f"JewelleryAgent failed: {str(error)}"
        state["error_log"].append(error_message)
        state["jewellery_kits"] = []
        print(f"  [5/5] ⚠️   Jewellery Agent error: {error}")

    return state


def node_merge_results(state: StyleAgentState) -> StyleAgentState:
    """
    Final node: Merges outfits and jewellery kits into one clean list.
    This is what the GUI displays in the results panel.
    """
    print("\n  [✨] Merging final recommendations...")

    merged = []  # list to hold the combined outfit + jewellery dicts

    outfits   = state.get("outfit_options", [])
    kits      = state.get("jewellery_kits", [])

    # Zip together — pair outfit 1 with kit 1, outfit 2 with kit 2, etc.
    for outfit, kit in zip(outfits, kits):
        combined = {
            "outfit":          outfit,   # full outfit with clothing items
            "jewellery_kit":   kit,      # matching jewellery kit
        }
        merged.append(combined)

    # If jewellery is missing (agent failed), still show outfits alone
    if not kits and outfits:
        for outfit in outfits:
            merged.append({"outfit": outfit, "jewellery_kit": {}})

    state["final_recommendations"] = merged
    print(f"  [✨] ✅  {len(merged)} complete looks ready!")
    return state


# =============================================================
# build_graph — creates and compiles the LangGraph StateGraph
# =============================================================
def _build_langgraph():
    """
    If LangGraph is available, constructs the StateGraph and compiles it.
    Returns the compiled graph object, or None if LangGraph is not available.
    """
    if not LANGGRAPH_AVAILABLE:
        return None  # skip — we will use the direct fallback below

    try:
        # Create a new StateGraph, telling it what shape the state dictionary has
        graph = StateGraph(StyleAgentState)

        # Add each agent as a node (a "step") in the graph
        # The string labels ("scout", "persona" etc.) are just names for the steps
        graph.add_node("scout",    node_trend_scout)   # step 1
        graph.add_node("persona",  node_persona)       # step 2
        graph.add_node("colour",   node_colour)        # step 3
        graph.add_node("wardrobe", node_wardrobe)      # step 4
        graph.add_node("jewellery",node_jewellery)     # step 5
        graph.add_node("merge",    node_merge_results) # final step

        # Define the flow: scout → persona → colour → wardrobe → jewellery → merge → END
        graph.set_entry_point("scout")         # where does execution start?
        graph.add_edge("scout",     "persona") # scout's output flows into persona
        graph.add_edge("persona",   "colour")
        graph.add_edge("colour",    "wardrobe")
        graph.add_edge("wardrobe",  "jewellery")
        graph.add_edge("jewellery", "merge")
        graph.add_edge("merge",     END)       # END signals the graph is complete

        compiled = graph.compile()  # compile = lock in the connections
        print("  ✅ LangGraph StateGraph compiled successfully")
        return compiled

    except Exception as graph_error:
        print(f"  ⚠️  LangGraph graph build failed: {graph_error}")
        return None  # fall back to direct pipeline


# Build the graph once when this module is imported
_compiled_graph = _build_langgraph()


# =============================================================
# run_pipeline — THE MAIN ENTRY POINT called by the GUI
# =============================================================
def run_pipeline(user_input_dict: dict) -> dict:
    """
    Runs all 5 agents in sequence and returns the final result dict.

    user_input_dict should contain:
        occasion:         e.g. "wedding"
        vibe:             e.g. "Ethnic"
        skin_undertone:   "warm" / "cool" / "neutral"
        body_type:        e.g. "Hourglass"
        size:             "M"
        budget_min:       2000
        budget_max:       20000
        favourite_colours: list of HEX strings (e.g. ["#C67C5A", "#800020"])
        colour_harmony:   "Analogous" / "Triadic" / "Surprise Me" etc.
        user_id:          1 (default test user)

    Returns: the fully populated StyleAgentState dict
    """
    print("\n" + "=" * 55)
    print("  🚀 Style Agent Pipeline Starting...")
    print("=" * 55)

    # Step 1: Create the initial state with empty slots for each agent to fill
    # Upgrade 2: extract total_budget from user_input and store at top level of state
    # This allows node_wardrobe to read it directly without digging into user_input
    total_budget = user_input_dict.get("total_budget", 15000)   # default ₹15,000

    initial_state: StyleAgentState = {
        "user_input":            user_input_dict,   # user's selections from GUI
        "trend_brief":           {},                # will be filled by Agent 1
        "user_persona":          {},                # will be filled by Agent 2
        "colour_palettes":       [],                # will be filled by Agent 3
        "outfit_options":        [],                # will be filled by Agent 4
        "jewellery_kits":        [],                # will be filled by Agent 5
        "final_recommendations": [],                # will be filled by merge node
        "error_log":             [],                # starts empty, errors added here
        "total_budget":          total_budget,      # Upgrade 2: single budget value
    }

    # Step 2: Run through the graph (or fallback if LangGraph is not available)
    if _compiled_graph is not None:
        # Use LangGraph — it handles the flow automatically
        print("  🔗 Running via LangGraph StateGraph...")
        final_state = _compiled_graph.invoke(initial_state)

    else:
        # Fallback: run each node function directly in sequence
        print("  🔗 Running via direct pipeline (LangGraph not available)...")
        state = initial_state
        state = node_trend_scout(state)   # Agent 1
        state = node_persona(state)       # Agent 2
        state = node_colour(state)        # Agent 3
        state = node_wardrobe(state)      # Agent 4
        state = node_jewellery(state)     # Agent 5
        state = node_merge_results(state) # Merge step
        final_state = state

    # Step 3: Print a summary
    print("\n" + "=" * 55)
    num_looks = len(final_state.get("final_recommendations", []))
    num_errors = len(final_state.get("error_log", []))
    print(f"  ✅ Pipeline complete! {num_looks} looks generated.")
    if num_errors > 0:
        print(f"  ⚠️   {num_errors} non-critical errors logged.")
    print("=" * 55 + "\n")

    return final_state  # return the complete state dict to the GUI
