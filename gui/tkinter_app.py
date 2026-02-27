"""
=============================================================
gui/tkinter_app.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  The complete Tkinter GUI application. Dark theme (#1A1A2E),
  gold accents (#C9A84C), Georgia headings, Segoe UI body text.

  6 PANELS:
    1. LEFT SIDEBAR   — user profile (name, body, undertone, budget, size)
    2. CENTRE TOP     — occasion dropdown + 8 vibe tiles
    3. CENTRE MIDDLE  — colour preference grids + harmony radio
    4. CENTRE BOTTOM  — generate button + progress bar + status
    5. RIGHT PANEL    — scrollable outfit results (3 cards)
    6. BOTTOM STRIP   — AI stylist chat (Ollama llama3)

  Generation runs in a background thread so the GUI never freezes.
=============================================================
"""

import tkinter as tk                     # built-in GUI framework
from tkinter import ttk, scrolledtext   # themed widgets + scrollable text
import threading                         # for running agents in background
import json                              # for saving JSON output
import csv                               # for exporting Tableau CSV
import os                                # for file paths
import sys                               # for module path

# ── Add project root to sys.path so we can import our modules ─
GUI_DIR      = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(GUI_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Try to import Ollama for the AI chat panel ────────────────
try:
    import ollama        # pip install ollama
    OLLAMA_OK = True
except ImportError:
    OLLAMA_OK = False    # chat will show a friendly "not installed" message

# =============================================================
# COLOUR PALETTE & FONTS — the entire app uses these constants
# =============================================================
BG_DARK      = "#1A1A2E"   # main window background — deep navy
BG_PANEL     = "#16213E"   # panel backgrounds — slightly lighter navy
BG_CARD      = "#0F3460"   # card backgrounds — deep indigo
GOLD         = "#C9A84C"   # accent gold — for headings, selected items
GOLD_DARK    = "#A07830"   # darker gold — for button hover
WHITE        = "#FFFFFF"   # primary text
GREY         = "#A0A0B0"   # secondary text / labels
GREEN        = "#4CAF50"   # success messages

FONT_HEADING = ("Georgia", 13, "bold")         # panel headings
FONT_SUBHEAD = ("Georgia", 11, "bold")         # card headings
FONT_BODY    = ("Segoe UI", 10)                # regular text
FONT_SMALL   = ("Segoe UI", 9)                 # secondary labels
FONT_BTN     = ("Segoe UI", 11, "bold")        # buttons

# 20 colours for the colour-picker grids (name → HEX)
COLOUR_GRID = [
    ("Ivory",       "#FFFFF0"), ("White",       "#F5F5F5"),
    ("Black",       "#1C1C1C"), ("Navy",         "#000080"),
    ("Cobalt Blue", "#0047AB"), ("Sky Blue",     "#87CEEB"),
    ("Emerald",     "#046307"), ("Sage Green",   "#B2AC88"),
    ("Olive",       "#556B2F"), ("Terracotta",   "#C67C5A"),
    ("Rust",        "#B7410E"), ("Burnt Orange", "#CC5500"),
    ("Coral",       "#FF6B6B"), ("Peach",        "#FFCBA4"),
    ("Blush Pink",  "#FFB6C1"), ("Rose",         "#FF007F"),
    ("Burgundy",    "#800020"), ("Deep Purple",  "#4B0082"),
    ("Gold",        "#D4AF37"), ("Camel",        "#C19A6B"),
]

# 8 vibes with emoji labels
VIBES = [
    ("🪷 Ethnic",       "Ethnic"),
    ("🌆 Modern",       "Modern"),
    ("🌸 Indo-Western", "Indo-Western"),
    ("👑 Classic",      "Classic"),
    ("💼 Formal",       "Formal"),
    ("🌿 Casual",       "Casual"),
    ("🎨 Boho",         "Boho"),
    ("🛹 Streetwear",   "Streetwear"),
]

# 30+ occasions in groups
OCCASIONS = [
    # Indian
    "Wedding Guest", "Sangeet", "Mehendi", "Haldi", "Pooja",
    "Diwali Party", "Navratri Night", "Eid Celebration", "Durga Puja", "Festival Mela",
    # Professional
    "Office / Work", "Client Meeting", "Job Interview", "Conference", "Business Lunch",
    "Networking Event", "Work From Home (Video Call)",
    # Social
    "Brunch with Friends", "Birthday Party (Yours)", "Birthday Party (Guest)",
    "Date Night", "First Date", "Anniversary Dinner", "Girls Night Out",
    "House Party", "Farewell Party",
    # Casual
    "Shopping Trip", "College / University", "Sunday Outing",
    "Movie Date", "Travel / Airport", "Lunch Date",
    # Formal
    "Black Tie Gala", "Award Ceremony", "Formal Dinner", "Theatre / Opera",
]

# Harmony options
HARMONIES = ["Complementary", "Analogous", "Triadic", "Monochromatic", "Surprise Me"]

# =============================================================
# CLASS: StyleAgentApp — the main application window
# =============================================================
class StyleAgentApp:
    """
    The main Tkinter application. Call StyleAgentApp().run() to launch.
    All widgets are built in the __init__ method and helper methods.
    """

    def __init__(self):
        """Create the main window, set theme, and build all 6 panels."""

        # ── Create the root window ────────────────────────────
        self.root = tk.Tk()
        self.root.title("✨ Style Agent — Hyper-Personalised AI Fashion Stylist")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1400x900")   # 1400 wide × 900 tall
        self.root.minsize(1100, 700)     # minimum usable size

        # ── State variables ───────────────────────────────────
        self.selected_vibe         = tk.StringVar(value="Ethnic")   # chosen vibe
        self.selected_occasion     = tk.StringVar(value="Wedding Guest")
        self.selected_size         = tk.StringVar(value="M")
        self.selected_undertone    = tk.StringVar(value="warm")
        self.selected_body         = tk.StringVar(value="Hourglass")
        self.selected_harmony      = tk.StringVar(value="Surprise Me")
        self.budget_min_var        = tk.DoubleVar(value=3000)
        self.budget_max_var        = tk.DoubleVar(value=20000)
        self.name_var              = tk.StringVar(value="")

        # Colour selections — sets of HEX codes
        self.fav_colours   = set()   # user's favourite colours
        self.avoid_colours = set()   # colours to avoid

        # Tile widget references (so we can highlight selected ones)
        self.vibe_tiles       = {}       # label → (display, value)
        self.fav_tiles        = {}       # hex → Label widget
        self.avoid_tiles      = {}       # hex → Label widget
        self.outfit_results   = []       # list of result dicts from agent pipeline
        self.status_var       = tk.StringVar(value="Ready — fill in your details and click Generate")

        # ── Configure ttk style for dark theme ────────────────
        self._setup_style()

        # ── Build the overall layout ──────────────────────────
        self._build_layout()

    # ─────────────────────────────────────────────────────────
    # _setup_style: configure ttk widgets for dark theme
    # ─────────────────────────────────────────────────────────
    def _setup_style(self):
        """Applies the dark gold theme to all ttk widgets."""
        style = ttk.Style(self.root)
        style.theme_use("clam")   # 'clam' is most customisable

        # Dark backgrounds for all ttk widgets
        style.configure("TFrame",       background=BG_DARK)
        style.configure("TLabel",       background=BG_DARK, foreground=WHITE, font=FONT_BODY)
        style.configure("TCombobox",    fieldbackground=BG_PANEL, background=BG_PANEL,
                        foreground=WHITE, font=FONT_BODY)
        style.configure("TRadiobutton", background=BG_DARK, foreground=WHITE, font=FONT_BODY,
                        indicatoron=True)
        style.configure("TScale",       background=BG_DARK, troughcolor=BG_PANEL)
        style.configure("Gold.TProgressbar", troughcolor=BG_PANEL,
                        background=GOLD, thickness=12)

        # Map combobox selection highlight to gold
        style.map("TCombobox",
                  selectbackground=[("readonly", BG_PANEL)],
                  selectforeground=[("readonly", GOLD)])

    # ─────────────────────────────────────────────────────────
    # _lbl: helper to make a gold heading label
    # ─────────────────────────────────────────────────────────
    def _lbl(self, parent, text, font=FONT_HEADING, fg=GOLD, **kwargs):
        """Returns a configured Label widget — shortcuts repeated styling."""
        return tk.Label(parent, text=text, font=font, fg=fg, bg=BG_DARK, **kwargs)

    # ─────────────────────────────────────────────────────────
    # _panel: helper to make a styled panel Frame
    # ─────────────────────────────────────────────────────────
    def _panel(self, parent, **kwargs):
        """Returns a dark-theme Frame for use as a panel."""
        return tk.Frame(parent, bg=BG_PANEL, relief="flat", bd=0, **kwargs)

    # ─────────────────────────────────────────────────────────
    # _build_layout: create the 3-column overall layout
    # ─────────────────────────────────────────────────────────
    def _build_layout(self):
        """
        Builds the master layout:
          LEFT COLUMN (250px)   — Panel 1: User Profile Sidebar
          CENTRE COLUMN (flex)  — Panels 2, 3, 4: Occasion + Colours + Generate
          RIGHT COLUMN (400px)  — Panel 5: Outfit Results
          BOTTOM STRIP (full)   — Panel 6: AI Chat
        """
        # ── Top portion: 3 columns side by side ────────────────
        self.top_frame = tk.Frame(self.root, bg=BG_DARK)
        self.top_frame.pack(fill="both", expand=True, padx=6, pady=6)

        # Left column — fixed width 240px
        self.left_col = tk.Frame(self.top_frame, bg=BG_DARK, width=240)
        self.left_col.pack(side="left", fill="y", padx=(0, 4))
        self.left_col.pack_propagate(False)   # prevent shrinking

        # Centre column — expands to fill space
        self.centre_col = tk.Frame(self.top_frame, bg=BG_DARK)
        self.centre_col.pack(side="left", fill="both", expand=True, padx=(0, 4))

        # Right column — fixed 420px
        self.right_col = tk.Frame(self.top_frame, bg=BG_DARK, width=420)
        self.right_col.pack(side="left", fill="y")
        self.right_col.pack_propagate(False)

        # ── Bottom: AI Chat strip (full width) ─────────────────
        self.bottom_frame = tk.Frame(self.root, bg=BG_DARK)
        self.bottom_frame.pack(fill="x", padx=6, pady=(0, 6))

        # ── Build each panel ───────────────────────────────────
        self._build_panel1_profile(self.left_col)
        self._build_panel2_occasion(self.centre_col)
        self._build_panel3_colours(self.centre_col)
        self._build_panel4_generate(self.centre_col)
        self._build_panel5_results(self.right_col)
        self._build_panel6_chat(self.bottom_frame)

    # =========================================================
    # PANEL 1 — USER PROFILE SIDEBAR
    # =========================================================
    def _build_panel1_profile(self, parent):
        """Left panel: name, body type, skin undertone, budget, size."""
        panel = self._panel(parent)
        panel.pack(fill="both", expand=True, padx=4, pady=4)

        # ── Heading ───────────────────────────────────────────
        self._lbl(panel, "👤  My Profile", bg=BG_PANEL).pack(pady=(10, 6))
        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=10, pady=4)

        inner = tk.Frame(panel, bg=BG_PANEL)
        inner.pack(fill="both", expand=True, padx=10)

        # Name field
        tk.Label(inner, text="Your Name", font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w", pady=(6,2))
        name_entry = tk.Entry(inner, textvariable=self.name_var, font=FONT_BODY,
                              bg=BG_CARD, fg=WHITE, insertbackground=WHITE,
                              relief="flat", bd=4)
        name_entry.pack(fill="x", pady=(0, 8))

        # Body type
        tk.Label(inner, text="Body Type", font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w", pady=(0,2))
        body_combo = ttk.Combobox(inner, textvariable=self.selected_body, state="readonly",
                                  values=["Hourglass","Pear","Apple","Rectangle","Petite","Plus Size"],
                                  font=FONT_BODY)
        body_combo.pack(fill="x", pady=(0, 8))

        # Skin undertone with coloured swatches
        tk.Label(inner, text="Skin Undertone", font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w", pady=(0,2))
        undertone_frame = tk.Frame(inner, bg=BG_PANEL)
        undertone_frame.pack(fill="x", pady=(0, 8))

        undertone_defs = [
            ("Warm",    "warm",    "#D2936A"),   # warm peachy swatch
            ("Cool",    "cool",    "#B0C4DE"),   # cool blue swatch
            ("Neutral", "neutral", "#C9B99A"),   # neutral beige swatch
        ]
        for label_text, value, swatch_hex in undertone_defs:
            row = tk.Frame(undertone_frame, bg=BG_PANEL)
            row.pack(fill="x", pady=1)
            # Coloured swatch square
            tk.Label(row, text="  ", bg=swatch_hex, width=2).pack(side="left", padx=(0,4))
            tk.Radiobutton(row, text=label_text, variable=self.selected_undertone,
                           value=value, font=FONT_BODY, fg=WHITE, bg=BG_PANEL,
                           selectcolor=BG_DARK, activebackground=BG_PANEL,
                           activeforeground=GOLD).pack(side="left")

        # Budget sliders
        tk.Label(inner, text="Budget Range (₹)", font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w", pady=(0,2))

        # Min budget slider
        min_row = tk.Frame(inner, bg=BG_PANEL)
        min_row.pack(fill="x")
        tk.Label(min_row, text="Min:", font=FONT_SMALL, fg=GREY, bg=BG_PANEL, width=4).pack(side="left")
        self.min_lbl = tk.Label(min_row, text="₹3,000", font=FONT_SMALL, fg=GOLD, bg=BG_PANEL, width=8)
        self.min_lbl.pack(side="right")

        min_scale = ttk.Scale(inner, from_=500, to=50000, variable=self.budget_min_var,
                              orient="horizontal",
                              command=lambda v: self.min_lbl.config(text=f"₹{int(float(v)):,}"))
        min_scale.pack(fill="x", pady=(0, 4))

        # Max budget slider
        max_row = tk.Frame(inner, bg=BG_PANEL)
        max_row.pack(fill="x")
        tk.Label(max_row, text="Max:", font=FONT_SMALL, fg=GREY, bg=BG_PANEL, width=4).pack(side="left")
        self.max_lbl = tk.Label(max_row, text="₹20,000", font=FONT_SMALL, fg=GOLD, bg=BG_PANEL, width=8)
        self.max_lbl.pack(side="right")

        max_scale = ttk.Scale(inner, from_=500, to=100000, variable=self.budget_max_var,
                              orient="horizontal",
                              command=lambda v: self.max_lbl.config(text=f"₹{int(float(v)):,}"))
        max_scale.pack(fill="x", pady=(0, 8))

        # Size selector (radio buttons)
        tk.Label(inner, text="Size", font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w", pady=(0,2))
        size_frame = tk.Frame(inner, bg=BG_PANEL)
        size_frame.pack(fill="x", pady=(0, 8))

        for i, sz in enumerate(["XS","S","M","L","XL","XXL"]):
            tk.Radiobutton(size_frame, text=sz, variable=self.selected_size, value=sz,
                           font=FONT_SMALL, fg=WHITE, bg=BG_PANEL,
                           selectcolor=GOLD, activebackground=BG_PANEL,
                           activeforeground=GOLD).grid(row=i//3, column=i%3, padx=2, pady=1, sticky="w")

    # =========================================================
    # PANEL 2 — OCCASION & VIBE
    # =========================================================
    def _build_panel2_occasion(self, parent):
        """Centre-top: occasion dropdown + 8 vibe tiles in 4x2 grid."""
        panel = self._panel(parent)
        panel.pack(fill="x", padx=4, pady=(4, 2))

        self._lbl(panel, "🎯  Occasion & Vibe", bg=BG_PANEL).pack(pady=(8, 4))
        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=10, pady=2)

        inner = tk.Frame(panel, bg=BG_PANEL)
        inner.pack(fill="x", padx=10, pady=6)

        # Occasion dropdown (left side)
        occ_frame = tk.Frame(inner, bg=BG_PANEL)
        occ_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(occ_frame, text="Occasion", font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w")
        occ_box = ttk.Combobox(occ_frame, textvariable=self.selected_occasion,
                               values=OCCASIONS, state="readonly", font=FONT_BODY, width=28)
        occ_box.pack(fill="x", pady=(2, 0))

        # Vibe tiles (right side) — 4x2 grid of clickable Labels
        vibe_frame = tk.Frame(inner, bg=BG_PANEL)
        vibe_frame.pack(side="left")
        tk.Label(inner, text="Vibe", font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(side="top", anchor="w")

        for idx, (emoji_label, vibe_val) in enumerate(VIBES):
            tile = tk.Label(vibe_frame, text=emoji_label, font=FONT_SMALL,
                            fg=WHITE, bg=BG_CARD, relief="flat",
                            padx=8, pady=4, cursor="hand2", width=14)
            tile.grid(row=idx//4, column=idx%4, padx=2, pady=2)
            # Store reference and bind click
            self.vibe_tiles[vibe_val] = tile
            tile.bind("<Button-1>", lambda e, v=vibe_val: self._select_vibe(v))

        # Highlight the default vibe
        self._select_vibe("Ethnic")

    def _select_vibe(self, vibe_value):
        """Highlights the selected vibe tile in gold, resets others."""
        self.selected_vibe.set(vibe_value)
        for val, tile in self.vibe_tiles.items():
            if val == vibe_value:
                tile.config(bg=GOLD, fg=BG_DARK, relief="solid")   # selected = gold
            else:
                tile.config(bg=BG_CARD, fg=WHITE, relief="flat")    # unselected = dark

    # =========================================================
    # PANEL 3 — COLOUR PREFERENCES
    # =========================================================
    def _build_panel3_colours(self, parent):
        """Centre-middle: two 5x4 colour grids + harmony radio buttons."""
        panel = self._panel(parent)
        panel.pack(fill="x", padx=4, pady=2)

        self._lbl(panel, "🎨  Colour Preferences", bg=BG_PANEL).pack(pady=(8, 4))
        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=10, pady=2)

        inner = tk.Frame(panel, bg=BG_PANEL)
        inner.pack(fill="x", padx=10, pady=6)

        # ── Favourite Colours grid ────────────────────────────
        fav_section = tk.Frame(inner, bg=BG_PANEL)
        fav_section.pack(side="left", padx=(0, 16))
        tk.Label(fav_section, text="Favourite Colours (click to select)",
                 font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w")
        fav_grid = tk.Frame(fav_section, bg=BG_PANEL)
        fav_grid.pack()

        for idx, (name, hex_code) in enumerate(COLOUR_GRID):
            tile = tk.Label(fav_grid, bg=hex_code, width=3, height=1,
                            relief="flat", cursor="hand2")
            tile.grid(row=idx//5, column=idx%5, padx=2, pady=2)
            # Show colour name as tooltip on hover
            tile.bind("<Enter>", lambda e, n=name: self.status_var.set(f"Colour: {n}"))
            tile.bind("<Leave>", lambda e: self.status_var.set(""))
            tile.bind("<Button-1>", lambda e, h=hex_code, t=tile: self._toggle_fav(h, t))
            self.fav_tiles[hex_code] = tile

        # ── Avoid Colours grid ────────────────────────────────
        avoid_section = tk.Frame(inner, bg=BG_PANEL)
        avoid_section.pack(side="left", padx=(0, 16))
        tk.Label(avoid_section, text="Avoid These Colours",
                 font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w")
        avoid_grid = tk.Frame(avoid_section, bg=BG_PANEL)
        avoid_grid.pack()

        for idx, (name, hex_code) in enumerate(COLOUR_GRID):
            tile = tk.Label(avoid_grid, bg=hex_code, width=3, height=1,
                            relief="flat", cursor="hand2")
            tile.grid(row=idx//5, column=idx%5, padx=2, pady=2)
            tile.bind("<Button-1>", lambda e, h=hex_code, t=tile: self._toggle_avoid(h, t))
            self.avoid_tiles[hex_code] = tile

        # ── Colour Harmony radio buttons ──────────────────────
        harm_section = tk.Frame(inner, bg=BG_PANEL)
        harm_section.pack(side="left")
        tk.Label(harm_section, text="Colour Harmony",
                 font=FONT_SMALL, fg=GREY, bg=BG_PANEL).pack(anchor="w")
        for h in HARMONIES:
            tk.Radiobutton(harm_section, text=h, variable=self.selected_harmony,
                           value=h, font=FONT_SMALL, fg=WHITE, bg=BG_PANEL,
                           selectcolor=GOLD, activebackground=BG_PANEL).pack(anchor="w", pady=1)

    def _toggle_fav(self, hex_code, tile):
        """Toggle a colour in/out of the favourites selection."""
        if hex_code in self.fav_colours:
            self.fav_colours.discard(hex_code)
            tile.config(highlightthickness=0, relief="flat")      # deselect
        else:
            self.fav_colours.add(hex_code)
            tile.config(highlightthickness=2, highlightbackground=GOLD, relief="solid")  # select

    def _toggle_avoid(self, hex_code, tile):
        """Toggle a colour in/out of the avoid selection."""
        if hex_code in self.avoid_colours:
            self.avoid_colours.discard(hex_code)
            tile.config(highlightthickness=0, relief="flat")
        else:
            self.avoid_colours.add(hex_code)
            tile.config(highlightthickness=2, highlightbackground="#FF4444", relief="solid")

    # =========================================================
    # PANEL 4 — GENERATE BUTTON
    # =========================================================
    def _build_panel4_generate(self, parent):
        """Centre-bottom: large gold Generate button + progress bar + status."""
        panel = self._panel(parent)
        panel.pack(fill="x", padx=4, pady=2)

        inner = tk.Frame(panel, bg=BG_PANEL)
        inner.pack(fill="x", padx=15, pady=10)

        # The big generate button
        self.gen_btn = tk.Button(
            inner,
            text="✨  Generate My Outfits",
            font=("Segoe UI", 14, "bold"),
            bg=GOLD, fg=BG_DARK,
            relief="flat", padx=20, pady=10,
            cursor="hand2",
            command=self._on_generate,
            activebackground=GOLD_DARK,
            activeforeground=BG_DARK,
        )
        self.gen_btn.pack(pady=(0, 8))

        # Progress bar (animated during generation)
        self.progress = ttk.Progressbar(
            inner, orient="horizontal", mode="indeterminate",
            style="Gold.TProgressbar", length=400
        )
        self.progress.pack(fill="x", pady=(0, 4))

        # Status label — updates live as each agent runs
        status_lbl = tk.Label(inner, textvariable=self.status_var,
                              font=FONT_SMALL, fg=GREY, bg=BG_PANEL, wraplength=400)
        status_lbl.pack()

    def _on_generate(self):
        """Called when the user clicks Generate. Starts background thread."""
        # Disable button while running so user doesn't click twice
        self.gen_btn.config(state="disabled", text="⏳  Generating...")
        self.progress.start(12)   # start spinning at 12ms intervals
        self.status_var.set("🌐  Scouting 2026 trends...")

        # Build user_input_dict from GUI selections
        user_input = {
            "name":             self.name_var.get() or "Valued Customer",
            "body_type":        self.selected_body.get(),
            "skin_undertone":   self.selected_undertone.get(),
            "budget_min":       int(self.budget_min_var.get()),
            "budget_max":       int(self.budget_max_var.get()),
            "size":             self.selected_size.get(),
            "occasion":         self.selected_occasion.get().lower().replace(" / "," ").replace(" ","_"),
            "vibe":             self.selected_vibe.get(),
            "favourite_colours": list(self.fav_colours) or ["#C67C5A"],
            "avoid_colours":    list(self.avoid_colours),
            "colour_harmony":   self.selected_harmony.get(),
            "user_id":          1,
        }

        # Run the agent pipeline in a background thread
        thread = threading.Thread(
            target=self._run_pipeline_thread,
            args=(user_input,),
            daemon=True    # daemon = stop thread when main window closes
        )
        thread.start()

    def _run_pipeline_thread(self, user_input):
        """
        Background thread function — runs all 5 agents.
        Updates status labels via root.after() (thread-safe Tk calls).
        """
        def set_status(msg):
            """Thread-safe status update."""
            self.root.after(0, lambda: self.status_var.set(msg))

        try:
            set_status("🌐  Scouting 2026 trends...")
            from workflow.langgraph_state import run_pipeline
            result = run_pipeline(user_input)   # runs all 5 agents, returns state dict

            # Store results and update UI on the main thread
            self.outfit_results = result.get("final_recommendations", [])
            self.root.after(0, lambda: self._display_results(result))

        except Exception as error:
            self.root.after(0, lambda: self.status_var.set(f"⚠️  Error: {error}"))

        finally:
            # Re-enable button and stop progress bar (always runs)
            self.root.after(0, self._generation_done)

    def _generation_done(self):
        """Called on the main thread after generation completes."""
        self.progress.stop()
        self.gen_btn.config(state="normal", text="✨  Generate My Outfits")
        self.status_var.set("✅  Your looks are ready!")

    # =========================================================
    # PANEL 5 — RESULTS DISPLAY
    # =========================================================
    def _build_panel5_results(self, parent):
        """Right panel: scrollable Canvas with 3 outfit cards."""
        panel = tk.Frame(parent, bg=BG_PANEL, relief="flat")
        panel.pack(fill="both", expand=True, padx=4, pady=4)

        self._lbl(panel, "👗  Your Looks", bg=BG_PANEL).pack(pady=(8, 4))
        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=8, pady=2)

        # Scrollable canvas
        self.results_canvas = tk.Canvas(panel, bg=BG_PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.results_canvas.yview)
        self.results_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.results_canvas.pack(side="left", fill="both", expand=True)

        # This inner frame is what we actually pack things into
        self.results_inner = tk.Frame(self.results_canvas, bg=BG_PANEL)
        self.results_canvas_win = self.results_canvas.create_window(
            (0, 0), window=self.results_inner, anchor="nw"
        )

        # Bind resize to keep canvas scrollregion updated
        self.results_inner.bind("<Configure>", self._on_results_resize)
        self.results_canvas.bind("<Configure>", self._on_canvas_resize)

        # Mouse wheel scrolling
        self.results_canvas.bind_all("<MouseWheel>",
            lambda e: self.results_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Placeholder text
        tk.Label(self.results_inner, text="Your outfit recommendations\nwill appear here.",
                 font=FONT_BODY, fg=GREY, bg=BG_PANEL, justify="center").pack(pady=40)

    def _on_results_resize(self, event):
        """Updates scroll region when items are added to the results panel."""
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        """Keeps the inner frame the same width as the canvas."""
        self.results_canvas.itemconfig(self.results_canvas_win, width=event.width)

    def _display_results(self, state_dict):
        """Clears old results and draws 3 fresh outfit cards."""
        # Clear all existing widgets in the inner frame
        for widget in self.results_inner.winfo_children():
            widget.destroy()

        recommendations = state_dict.get("final_recommendations", [])
        errors          = state_dict.get("error_log", [])

        if errors:
            tk.Label(self.results_inner, text=f"⚠️ {len(errors)} agent(s) used fallback data.",
                     font=FONT_SMALL, fg="#FFAA00", bg=BG_PANEL).pack(pady=4)

        if not recommendations:
            tk.Label(self.results_inner,
                     text="No outfits found.\nPlease run: python database/setup_database.py\nthen try again.",
                     font=FONT_BODY, fg=GREY, bg=BG_PANEL, justify="center").pack(pady=30)
            return

        for i, rec in enumerate(recommendations):
            self._build_outfit_card(self.results_inner, rec, i + 1)

        # Update status
        self.status_var.set(f"✅  {len(recommendations)} looks generated!")

    def _build_outfit_card(self, parent, rec, outfit_num):
        """Draws one outfit card widget with all details."""
        outfit  = rec.get("outfit", {})
        kit     = rec.get("jewellery_kit", {})

        # Card frame
        card = tk.Frame(parent, bg=BG_CARD, relief="ridge", bd=1)
        card.pack(fill="x", padx=6, pady=6)

        # ── Card heading + palette name ───────────────────────
        palette_name = outfit.get("palette_name", f"Look {outfit_num}")
        tk.Label(card, text=f"  ✦  {palette_name}",
                 font=FONT_SUBHEAD, fg=GOLD, bg=BG_CARD).pack(anchor="w", padx=10, pady=(8,2))

        # ── Colour swatches ───────────────────────────────────
        swatch_frame = tk.Frame(card, bg=BG_CARD)
        swatch_frame.pack(anchor="w", padx=10, pady=(0, 6))

        for swatch in outfit.get("colour_swatches", []):
            colour_hex  = swatch.get("hex", "#888")
            colour_name = swatch.get("name", "")
            dot = tk.Label(swatch_frame, bg=colour_hex, width=3, height=1, relief="raised")
            dot.pack(side="left", padx=2)
            tk.Label(swatch_frame, text=colour_name, font=FONT_SMALL, fg=GREY, bg=BG_CARD).pack(side="left", padx=(0,8))

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=10, pady=2)

        # ── Clothing items ────────────────────────────────────
        items = outfit.get("items", {})
        item_labels = {
            "dress":    "👗 DRESS",
            "top":      "👚 TOP",
            "bottom":   "👖 BOTTOM",
            "outerwear":"🧥 OUTERWEAR",
            "footwear": "👠 FOOTWEAR",
            "bag":      "👜 BAG",
        }
        for key, label in item_labels.items():
            item = items.get(key)
            if item and isinstance(item, dict):
                name  = item.get("name", "")
                price = item.get("price", "")
                if name:
                    row = tk.Frame(card, bg=BG_CARD)
                    row.pack(fill="x", padx=10, pady=1)
                    tk.Label(row, text=f"{label}:", font=FONT_SMALL, fg=GOLD,
                             bg=BG_CARD, width=12, anchor="w").pack(side="left")
                    tk.Label(row, text=f"{name}  {price}", font=FONT_SMALL, fg=WHITE,
                             bg=BG_CARD, wraplength=300, justify="left", anchor="w").pack(side="left", fill="x")

        # Total cost
        total = outfit.get("total_estimated_cost", "")
        if total:
            tk.Label(card, text=f"  💰 Total: {total}", font=FONT_SMALL, fg=GREEN,
                     bg=BG_CARD).pack(anchor="w", padx=10, pady=2)

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=10, pady=2)

        # ── Jewellery Kit ─────────────────────────────────────
        if kit:
            tk.Label(card, text="  💎 JEWELLERY KIT", font=FONT_SMALL, fg=GOLD,
                     bg=BG_CARD).pack(anchor="w", padx=10, pady=(4,2))
            for j_key in ["earrings","necklace","bangles","rings","maang_tikka","optional_extras"]:
                val = kit.get(j_key, "")
                if val and val != "Skip — not applicable for this vibe/occasion combination":
                    j_label = j_key.replace("_"," ").title()
                    row = tk.Frame(card, bg=BG_CARD)
                    row.pack(fill="x", padx=10, pady=1)
                    tk.Label(row, text=f"{j_label}:", font=FONT_SMALL, fg=GREY,
                             bg=BG_CARD, width=14, anchor="w").pack(side="left")
                    tk.Label(row, text=val, font=FONT_SMALL, fg=WHITE, bg=BG_CARD,
                             wraplength=260, justify="left", anchor="w").pack(side="left", fill="x")

            # Fragrance note
            fragrance = kit.get("fragrance_note", "")
            if fragrance:
                tk.Label(card, text=f"  🌸 Fragrance: {fragrance}", font=FONT_SMALL,
                         fg=GREY, bg=BG_CARD, wraplength=360, justify="left").pack(
                    anchor="w", padx=10, pady=2)

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=10, pady=2)

        # ── Why This Works ────────────────────────────────────
        why = outfit.get("why_this_works", "")
        if why:
            tk.Label(card, text="  ✨ Why This Works", font=FONT_SMALL, fg=GOLD, bg=BG_CARD).pack(anchor="w", padx=10)
            tk.Label(card, text=why, font=("Segoe UI", 9, "italic"), fg=GREY, bg=BG_CARD,
                     wraplength=370, justify="left").pack(anchor="w", padx=14, pady=(2, 4))

        # ── Occasion Notes ────────────────────────────────────
        notes = outfit.get("occasion_notes", [])
        if notes:
            tk.Label(card, text="  📌 Stylist Tips", font=FONT_SMALL, fg=GOLD, bg=BG_CARD).pack(anchor="w", padx=10)
            for note in notes:
                tk.Label(card, text=f"    • {note}", font=FONT_SMALL, fg=WHITE, bg=BG_CARD,
                         wraplength=370, justify="left").pack(anchor="w", padx=14, pady=1)

        # ── Action buttons ────────────────────────────────────
        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(fill="x", padx=10, pady=(6, 10))

        tk.Button(btn_frame, text="💾 Save This Look", font=FONT_SMALL,
                  bg=GOLD, fg=BG_DARK, relief="flat", padx=8, pady=4, cursor="hand2",
                  command=lambda r=rec, n=outfit_num: self._save_look(r, n)
                  ).pack(side="left", padx=(0, 6))

        tk.Button(btn_frame, text="📊 Export to Tableau", font=FONT_SMALL,
                  bg=BG_PANEL, fg=WHITE, relief="flat", padx=8, pady=4, cursor="hand2",
                  command=lambda: self._export_tableau()
                  ).pack(side="left")

    def _save_look(self, rec, num):
        """Saves a single outfit recommendation to outputs/outfit_recommendation.json."""
        out_dir  = os.path.join(PROJECT_ROOT, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "outfit_recommendation.json")
        try:
            existing = []
            if os.path.exists(out_path):
                with open(out_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            existing.append(rec)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            self.status_var.set(f"✅  Look {num} saved to outputs/outfit_recommendation.json")
        except Exception as e:
            self.status_var.set(f"⚠️  Save failed: {e}")

    def _export_tableau(self):
        """Exports all current outfit results to outputs/tableau_export.csv."""
        out_dir  = os.path.join(PROJECT_ROOT, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "tableau_export.csv")
        try:
            rows = []
            for rec in self.outfit_results:
                outfit  = rec.get("outfit", {})
                kit     = rec.get("jewellery_kit", {})
                palette = outfit.get("palette_name", "")
                items   = outfit.get("items", {})
                rows.append({
                    "outfit_number":    outfit.get("outfit_number", ""),
                    "palette_name":     palette,
                    "primary_colour":   outfit.get("colour_swatches", [{}])[0].get("name",""),
                    "secondary_colour": outfit.get("colour_swatches", [{}]*2)[1].get("name","") if len(outfit.get("colour_swatches",[])) > 1 else "",
                    "top":              items.get("top", {}).get("name","") or items.get("dress",{}).get("name",""),
                    "bottom":           items.get("bottom", {}).get("name",""),
                    "outerwear":        items.get("outerwear",{}).get("name",""),
                    "footwear":         items.get("footwear",{}).get("name",""),
                    "bag":              items.get("bag",{}).get("name",""),
                    "total_cost":       outfit.get("total_estimated_cost",""),
                    "earrings":         kit.get("earrings",""),
                    "necklace":         kit.get("necklace",""),
                    "occasion":         "",
                    "vibe":             "",
                    "fragrance":        kit.get("fragrance_note",""),
                })

            if rows:
                with open(out_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                self.status_var.set(f"✅  Exported {len(rows)} looks to outputs/tableau_export.csv")
            else:
                self.status_var.set("⚠️  Generate outfits first before exporting.")
        except Exception as e:
            self.status_var.set(f"⚠️  Export failed: {e}")

    # =========================================================
    # PANEL 6 — AI STYLIST CHAT
    # =========================================================
    def _build_panel6_chat(self, parent):
        """Bottom strip: scrollable chat + input field + Send button."""
        panel = tk.Frame(parent, bg=BG_PANEL, relief="flat", bd=0)
        panel.pack(fill="x", padx=4, pady=(2, 0))

        tk.Label(panel, text="💬  AI Stylist Chat", font=FONT_SUBHEAD, fg=GOLD,
                 bg=BG_PANEL).pack(anchor="w", padx=10, pady=(6, 2))

        # Scrollable chat history display
        self.chat_display = scrolledtext.ScrolledText(
            panel, height=5, font=FONT_SMALL,
            bg=BG_CARD, fg=WHITE, insertbackground=WHITE,
            relief="flat", state="disabled", wrap="word"
        )
        self.chat_display.pack(fill="x", padx=8, pady=(0, 4))

        # Add a welcome message
        self._chat_append("AI Stylist", "Hello! Ask me anything about fashion, colours, or your outfit. Try: 'What jewellery works with a V-neck blouse?'")

        # Input row: Entry + Send button side by side
        input_row = tk.Frame(panel, bg=BG_PANEL)
        input_row.pack(fill="x", padx=8, pady=(0, 8))

        self.chat_entry = tk.Entry(input_row, font=FONT_BODY, bg=BG_CARD, fg=WHITE,
                                   insertbackground=WHITE, relief="flat", bd=4)
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.chat_entry.insert(0, "Ask your AI stylist anything...")
        self.chat_entry.bind("<FocusIn>",  lambda e: self._clear_placeholder())
        self.chat_entry.bind("<FocusOut>", lambda e: self._restore_placeholder())
        self.chat_entry.bind("<Return>",   lambda e: self._send_chat())

        tk.Button(input_row, text="Send ▶", font=FONT_BTN, bg=GOLD, fg=BG_DARK,
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=self._send_chat).pack(side="left")

    def _clear_placeholder(self):
        """Remove placeholder text when user clicks the chat entry."""
        if self.chat_entry.get() == "Ask your AI stylist anything...":
            self.chat_entry.delete(0, "end")
            self.chat_entry.config(fg=WHITE)

    def _restore_placeholder(self):
        """Restore placeholder text if the entry is empty."""
        if not self.chat_entry.get().strip():
            self.chat_entry.insert(0, "Ask your AI stylist anything...")
            self.chat_entry.config(fg=GREY)

    def _chat_append(self, speaker, message):
        """Appends a message to the chat display widget."""
        self.chat_display.config(state="normal")    # enable editing temporarily
        self.chat_display.insert("end", f"\n{speaker}: {message}\n")
        self.chat_display.see("end")                # scroll to bottom
        self.chat_display.config(state="disabled")  # lock back to read-only

    def _send_chat(self):
        """Sends the chat message to Ollama llama3 and displays the response."""
        user_msg = self.chat_entry.get().strip()
        if not user_msg or user_msg == "Ask your AI stylist anything...":
            return

        self.chat_entry.delete(0, "end")
        self._chat_append("You", user_msg)

        # Build system context with current outfit data
        context_summary = ""
        if self.outfit_results:
            context_summary = f"The user has generated outfit recommendations for: {self.outfit_results[0].get('outfit', {}).get('palette_name', '')}. "

        system_prompt = (
            "You are a world-class Indian fashion stylist specialising in Indian women's fashion. "
            "You have encyclopaedic knowledge of Indian occasions, fabrics, jewellery, and colour theory. "
            "Give warm, specific, actionable advice — never vague. "
            "Always mention specific fabrics, colour names, and jewellery types. "
            + context_summary
        )

        # Run Ollama in a background thread so the GUI stays responsive
        threading.Thread(
            target=self._chat_thread,
            args=(user_msg, system_prompt),
            daemon=True
        ).start()

    def _chat_thread(self, user_msg, system_prompt):
        """Background thread: calls Ollama and posts the reply to the chat."""
        if not OLLAMA_OK:
            reply = ("Ollama is not installed. Run: pip install ollama\n"
                     "Then install llama3: ollama pull llama3\n"
                     "Once done, restart this app and the AI chat will work!")
        else:
            try:
                response = ollama.chat(
                    model="llama3",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_msg},
                    ]
                )
                reply = response["message"]["content"]
            except Exception as e:
                reply = (f"Cannot reach Ollama: {e}\n"
                         f"Make sure Ollama is running: open a terminal and type 'ollama serve'")

        # Post the reply to the GUI on the main thread
        self.root.after(0, lambda: self._chat_append("AI Stylist", reply))

    # =========================================================
    # RUN
    # =========================================================
    def run(self):
        """Starts the Tkinter main event loop — keeps the window open."""
        self.root.mainloop()


# =============================================================
# MAIN — launch the app when this file is run directly
# =============================================================
if __name__ == "__main__":
    app = StyleAgentApp()
    app.run()
