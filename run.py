"""
=============================================================
run.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This is the single entry point for the entire application.
  Run this file to start everything:
    python run.py

  It does 4 things before launching the GUI:
    1. Checks if the database exists — if not, creates it automatically
    2. Prints a welcome banner
    3. Checks if Ollama is reachable (for the AI chat feature)
    4. Launches gui/tkinter_app.py
=============================================================
"""

import os            # built-in: for file path checking
import sys           # built-in: for modifying Python module path

# ── Add the project root to sys.path so ALL imports work ──────
# This file sits at the project root, so its own folder IS the root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Paths we need to check ────────────────────────────────────
DB_PATH      = os.path.join(PROJECT_ROOT, "database", "inventory.db")
DB_SETUP_PY  = os.path.join(PROJECT_ROOT, "database", "setup_database.py")
OUTPUTS_DIR  = os.path.join(PROJECT_ROOT, "outputs")


# =============================================================
# STEP 1: Print Welcome Banner
# =============================================================
def print_banner():
    """Prints a styled welcome banner to the terminal."""
    print("\n" + "=" * 60)
    print("        ✨  STYLE AGENT — Gold Standard Edition")
    print("        Hyper-Personalised AI Fashion Stylist")
    print("=" * 60)
    print("  Built with: Python · Tkinter · SQLite · Ollama llama3")
    print("              LangGraph · CrewAI · BeautifulSoup4")
    print("─" * 60)


# =============================================================
# STEP 2: Ensure database exists — auto-create if missing
# =============================================================
def ensure_database():
    """
    Checks if inventory.db exists. If not, runs setup_database.py
    automatically so the user doesn't have to remember to do it.
    """
    if os.path.exists(DB_PATH):
        # Database already exists — get file size as a sanity check
        size_kb = os.path.getsize(DB_PATH) / 1024
        print(f"  ✅ Database found: database/inventory.db ({size_kb:.1f} KB)")
        return True

    # Database missing — create it now
    print("  ⚠️  database/inventory.db not found.")
    print("  🔧 Running setup_database.py to create it now...")
    print("─" * 60)

    try:
        # Import and run the setup function directly (no subprocess needed)
        import importlib.util
        spec   = importlib.util.spec_from_file_location("setup_database", DB_SETUP_PY)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # this runs setup_database.py

        if os.path.exists(DB_PATH):
            print("\n  ✅ Database created successfully!")
            return True
        else:
            print("\n  ❌ Database creation failed. Please run manually:")
            print("     python database/setup_database.py")
            return False

    except Exception as setup_error:
        print(f"\n  ❌ Database setup error: {setup_error}")
        print("  Please run manually: python database/setup_database.py")
        return False


# =============================================================
# STEP 3: Ensure outputs/ folder exists
# =============================================================
def ensure_outputs_folder():
    """Creates the outputs/ directory if it doesn't exist."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)   # exist_ok=True = no error if already exists
    print(f"  ✅ Outputs folder ready: outputs/")


# =============================================================
# STEP 4: Check Ollama availability (for AI chat panel)
# =============================================================
def check_ollama():
    """
    Tries to ping the Ollama service.
    Prints a helpful message either way — the app works without it.
    """
    try:
        import ollama   # pip install ollama
        # Try to list available models — this only works if Ollama is running
        models = ollama.list()
        model_names = [m.get("name", "") for m in models.get("models", [])]
        if "llama3" in str(model_names) or any("llama3" in m for m in model_names):
            print("  ✅ Ollama llama3 is ready — AI chat panel will be fully active")
        else:
            print("  ⚠️  Ollama is running but llama3 is not pulled.")
            print("      Run: ollama pull llama3")
            print("      The AI chat panel will show instructions until you do this.")
    except ImportError:
        print("  ⚠️  Ollama Python library not installed.")
        print("      Run: pip install ollama")
        print("      The AI chat panel will still work after installation.")
    except Exception:
        print("  ⚠️  Ollama is not running. Start it with: ollama serve")
        print("      The rest of the app works perfectly without it.")


# =============================================================
# STEP 5: Check for required libraries
# =============================================================
def check_libraries():
    """Checks if key libraries are installed. Prints status for each."""
    print("\n  Library check:")

    libraries = {
        "requests":       "Web scraping (Trend Scout)",
        "bs4":            "HTML parsing (Trend Scout)",
        "langgraph":      "Agent pipeline (LangGraph)",
        "crewai":         "Agent orchestration (CrewAI)",
        "PIL":            "Image colour extraction (Pillow)",
        "ollama":         "Local LLM (AI chat panel)",
    }

    for lib, description in libraries.items():
        try:
            __import__(lib)
            print(f"    ✅ {lib:15s} — {description}")
        except ImportError:
            print(f"    ⚠️  {lib:15s} — {description} (run: pip install {lib})")

    print()


# =============================================================
# STEP 6: Launch the GUI
# =============================================================
def launch_gui():
    """Imports and launches the Tkinter GUI application."""
    print("─" * 60)
    print("  🚀 Launching Style Agent GUI...")
    print("  (Close the window to exit the application)")
    print("─" * 60 + "\n")

    try:
        from gui.tkinter_app import StyleAgentApp   # import the GUI class
        app = StyleAgentApp()                       # create the window
        app.run()                                   # start the event loop

    except ImportError as import_error:
        print(f"\n  ❌ GUI import failed: {import_error}")
        print("  Make sure you are running this from the project root folder:")
        print(f"    cd \"{PROJECT_ROOT}\"")
        print("    python run.py")
        sys.exit(1)

    except tk_error := Exception() if False else None:
        pass  # just a placeholder; real errors caught below

    except Exception as gui_error:
        print(f"\n  ❌ GUI error: {gui_error}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# =============================================================
# MAIN — runs when you type: python run.py
# =============================================================
if __name__ == "__main__":
    print_banner()                  # Step 1 — welcome banner

    db_ok = ensure_database()       # Step 2 — create database if needed
    ensure_outputs_folder()         # Step 3 — create outputs/ if needed
    check_ollama()                  # Step 4 — check Ollama status
    check_libraries()               # Step 5 — check all libraries

    if not db_ok:
        print("\n  ❌ Cannot start without the database. Please fix the error above first.")
        sys.exit(1)

    launch_gui()                    # Step 6 — open the Tkinter window
