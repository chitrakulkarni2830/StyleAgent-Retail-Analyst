"""
gui/tkinter_app.py — Style Agent Gold Standard v2
Upgrade 4: White & Gold minimalist redesign.
Upgrade 3: Single snapping budget slider.
Upgrade 2: total_budget passed to pipeline.
Upgrade 1: shopping links displayed in outfit cards.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, colorchooser  # colorchooser is built-in — no install needed
import threading, json, csv, os, sys, webbrowser

GUI_DIR      = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(GUI_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import ollama
    OLLAMA_OK = True
except ImportError:
    OLLAMA_OK = False

# ── Colour palette ────────────────────────────────────────────
COLOURS = {
    # Main backgrounds
    "bg_primary":    "#FFFFFF",   # pure white — main window
    "bg_secondary":  "#FAFAFA",   # near-white — sidebar
    "bg_card":       "#FFFFFF",   # card background
    "bg_input":      "#F7F7F7",   # input field background
    "chat_bg":       "#F5F3EF",   # warm cream — chat window
    "darkbg_header": "#0F0F0F",   # near-black — nav bar, card headers
    # Gold scale
    "gold_primary":  "#C9A84C",   # warm gold — buttons, accents
    "gold_light":    "#F5EDD3",   # pale gold — hover backgrounds
    "gold_shimmer":  "#E8C97A",   # bright gold — shimmer effects
    "gold_dark":     "#7D5A1E",   # deep gold — headings, pressed
    # Text
    "text_primary":  "#111111",   # near-black
    "text_secondary":"#444444",   # secondary labels
    "text_muted":    "#999999",   # hints and placeholders
    # Borders
    "border_light":  "#EBEBEB",   # card outlines
    "border_mid":    "#D4D4D4",   # input borders
    "border_gold":   "#C9A84C",   # selected states
    # Status
    "success":       "#2E7D32",
    "error":         "#C62828",
    # Vibe tile accent colours
    "vibe_ethnic":   "#8B1A4A",   # deep magenta
    "vibe_modern":   "#1A3A5C",   # deep navy
    "vibe_indowest": "#6B3A2A",   # warm maroon
    "vibe_classic":  "#2A2A2A",   # near black
    "vibe_formal":   "#1B3A4B",   # dark teal
    "vibe_casual":   "#2D5A27",   # forest green
    "vibe_boho":     "#7A4F2A",   # warm brown
    "vibe_street":   "#1A1A4A",   # deep indigo
}

# ── Typography ────────────────────────────────────────────────
FONTS = {
    # Keep old keys so existing code still works
    "heading_large":  ("Georgia", 20, "bold"),
    "heading_medium": ("Georgia", 15, "bold"),
    "heading_small":  ("Georgia", 12, "bold"),
    "body":           ("Segoe UI", 10),
    "body_bold":      ("Segoe UI", 10, "bold"),
    "small":          ("Segoe UI", 9),
    "price":          ("Georgia", 13, "bold"),
    "link":           ("Segoe UI", 9, "underline"),
    "mono":           ("Courier New", 9),
    # New keys for the redesign
    "app_title":      ("Georgia", 20, "bold"),
    "section_head":   ("Georgia", 14, "bold"),
    "card_title":     ("Georgia", 13, "bold"),
    "small_bold":     ("Segoe UI", 8, "bold"),
    "btn_primary":    ("Georgia", 11, "bold"),
    "btn_secondary":  ("Segoe UI", 9, "bold"),
    "tag":            ("Segoe UI", 8),
}

# ── Budget snap steps (Upgrade 3) ─────────────────────────────
BUDGET_STEPS = [
    500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000,
    6000, 7000, 8000, 10000, 12000, 15000, 20000, 25000, 30000,
]

# ── 20-colour picker grid ─────────────────────────────────────
COLOUR_GRID = [
    ("Ivory","#FFFFF0"), ("White","#F5F5F5"), ("Black","#1C1C1C"),
    ("Navy","#000080"), ("Cobalt Blue","#0047AB"), ("Sky Blue","#87CEEB"),
    ("Emerald","#046307"), ("Sage Green","#B2AC88"), ("Olive","#556B2F"),
    ("Terracotta","#C67C5A"), ("Rust","#B7410E"), ("Burnt Orange","#CC5500"),
    ("Coral","#FF6B6B"), ("Peach","#FFCBA4"), ("Blush Pink","#FFB6C1"),
    ("Rose","#FF007F"), ("Burgundy","#800020"), ("Deep Purple","#4B0082"),
    ("Gold","#D4AF37"), ("Camel","#C19A6B"),
]

# ── 8 vibes — (emoji, display_name, colour_key) ──────────────
VIBES = [
    ("🪷", "Ethnic",       "vibe_ethnic"),
    ("🌆", "Modern",       "vibe_modern"),
    ("🌸", "Indo-Western", "vibe_indowest"),
    ("👑", "Classic",      "vibe_classic"),
    ("💼", "Formal",       "vibe_formal"),
    ("🌿", "Casual",       "vibe_casual"),
    ("🎨", "Boho",         "vibe_boho"),
    ("🛹", "Streetwear",   "vibe_street"),
]

# ── 24-swatch fashion colour grid for the favourite picker ────
FASHION_SWATCHES_24 = [
    ("#FFFFFF","White"),  ("#FFFFF0","Ivory"),   ("#F5F0E8","Cream"),
    ("#F5DEB3","Beige"),  ("#C19A6B","Camel"),   ("#1A1A1A","Black"),
    ("#8B0000","Deep Red"),("#C0392B","Red"),    ("#CC5500","Burnt Org"),
    ("#FFDB58","Mustard"),("#C67C5A","Terracotta"),("#B7410E","Rust"),
    ("#000080","Navy"),   ("#0047AB","Cobalt"),  ("#87CEEB","Sky Blue"),
    ("#046307","Emerald"),("#B2AC88","Sage"),    ("#7D3C98","Purple"),
    ("#FFB6C1","Blush"),  ("#B57EDC","Lavender"),("#98D8C8","Mint"),
    ("#FFCBA4","Peach"),  ("#D4AF37","Gold"),    ("#C0C0C0","Silver"),
]

# ── 35+ occasions ─────────────────────────────────────────────
OCCASIONS = [
    "Wedding Guest","Sangeet","Mehendi","Haldi","Pooja",
    "Diwali Party","Navratri Night","Eid Celebration","Durga Puja","Festival Mela",
    "Office / Work","Client Meeting","Job Interview","Conference","Business Lunch",
    "Networking Event","Work From Home (Video Call)",
    "Brunch with Friends","Birthday Party (Yours)","Birthday Party (Guest)",
    "Date Night","First Date","Anniversary Dinner","Girls Night Out",
    "House Party","Farewell Party",
    "Shopping Trip","College / University","Sunday Outing",
    "Movie Date","Travel / Airport","Lunch Date",
    "Black Tie Gala","Award Ceremony","Formal Dinner","Theatre / Opera",
]

HARMONIES = ["Complementary","Analogous","Triadic","Monochromatic","Surprise Me"]

# ── Occasion label → DB keyword map (fixes "wedding_guest" bug) ──
OCCASION_MAP = {
    "Wedding Guest":"wedding", "Sangeet":"sangeet", "Mehendi":"mehendi",
    "Haldi":"mehendi", "Pooja":"pooja", "Diwali Party":"diwali",
    "Navratri Night":"navratri", "Eid Celebration":"eid",
    "Durga Puja":"festival", "Festival Mela":"festival",
    "Office / Work":"office", "Client Meeting":"client_meeting",
    "Job Interview":"job_interview", "Conference":"conference",
    "Business Lunch":"business_lunch", "Networking Event":"networking_event",
    "Work From Home (Video Call)":"office",
    "Brunch with Friends":"brunch",
    "Birthday Party (Yours)":"birthday_party",
    "Birthday Party (Guest)":"birthday_party",
    "Date Night":"date_night", "First Date":"date_night",
    "Anniversary Dinner":"anniversary_dinner",
    "Girls Night Out":"girls_night_out",
    "House Party":"birthday_party", "Farewell Party":"birthday_party",
    "Shopping Trip":"shopping_trip", "College / University":"college",
    "Sunday Outing":"sunday_outing", "Movie Date":"movie_date",
    "Travel / Airport":"travel", "Lunch Date":"brunch",
    "Black Tie Gala":"black_tie", "Award Ceremony":"award_ceremony",
    "Formal Dinner":"formal_dinner", "Theatre / Opera":"theatre",
}


# =============================================================
# UPGRADE 1 — ChatGPT-style floating AI stylist dialog
# =============================================================
class StyleChatDialog:
    """
    A floating popup window styled like ChatGPT.
    Opens when the user clicks 'Ask Stylist' in the nav bar.
    Has scrolling chat history, animated typing indicator,
    and sends messages to Ollama llama3 in a background thread.
    """

    def __init__(self, parent_root):
        self.parent = parent_root          # reference to main window for centering
        self.is_typing = False             # True while AI response is loading
        self.typing_dots = 0              # animation counter (1-3)

        # Create a separate floating window on top of the main window
        self.dialog = tk.Toplevel(parent_root)
        self.dialog.title("\u2746  Your AI Stylist")
        self.dialog.configure(bg=COLOURS["bg_primary"])
        self.dialog.resizable(True, True)
        self.dialog.minsize(420, 500)
        self.dialog.transient(parent_root)   # stay on top of main window
        self.dialog.grab_set()               # block interaction with main window

        # Calculate center position on the parent window
        parent_root.update_idletasks()
        px, py = parent_root.winfo_x(), parent_root.winfo_y()
        pw, ph = parent_root.winfo_width(), parent_root.winfo_height()
        dw, dh = 520, 680
        x = px + (pw - dw) // 2    # horizontal center
        y = py + (ph - dh) // 2    # vertical center
        self.dialog.geometry(f"{dw}x{dh}+{x}+{y}")

        # Build each part of the dialog layout
        self._build_header()
        self._build_messages_area()
        self._build_typing_indicator()
        self._build_input_bar()

        # Show welcome message immediately when the dialog opens
        self._add_ai_message(
            "Hello! \U0001f44b I'm your personal AI stylist. Ask me anything about fashion!\n\n"
            "\u2022 What should I wear to a Mehendi as a guest?\n"
            "\u2022 What colours suit warm skin tones?\n"
            "\u2022 How do I style a saree for an office party?\n"
            "\u2022 What jewellery goes with a lehenga?"
        )

    def _build_header(self):
        """Dark header bar with avatar, title, online indicator, and close button."""
        hdr = tk.Frame(self.dialog, bg=COLOURS["darkbg_header"], height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)   # prevent frame shrinking to fit children

        # Gold avatar square on the left
        av = tk.Frame(hdr, bg=COLOURS["gold_primary"], width=36, height=36)
        av.pack(side="left", padx=(16, 10), pady=14)
        av.pack_propagate(False)
        tk.Label(av, text="\u2746", font=("Georgia", 14, "bold"),
                 fg=COLOURS["bg_primary"], bg=COLOURS["gold_primary"]).pack(expand=True)

        # Title and online status
        tb = tk.Frame(hdr, bg=COLOURS["darkbg_header"])
        tb.pack(side="left", expand=True, fill="x")
        tk.Label(tb, text="Style Agent", font=("Georgia", 13, "bold"),
                 fg=COLOURS["gold_primary"], bg=COLOURS["darkbg_header"]).pack(anchor="w")
        tk.Label(tb, text="\u25cf Online  \u2014  AI Fashion Stylist", font=("Segoe UI", 9),
                 fg="#4CAF50", bg=COLOURS["darkbg_header"]).pack(anchor="w")

        # Close button on the right
        tk.Button(hdr, text="\u2715", font=("Segoe UI", 11),
                  bg=COLOURS["darkbg_header"], fg=COLOURS["text_muted"],
                  relief="flat", bd=0, cursor="hand2",
                  activebackground=COLOURS["error"],
                  activeforeground=COLOURS["bg_primary"],
                  command=self.dialog.destroy).pack(side="right", padx=16, pady=20)

        # Thin gold rule under header
        tk.Frame(self.dialog, bg=COLOURS["gold_primary"], height=1).pack(fill="x")

    def _build_messages_area(self):
        """Scrollable canvas that holds all message bubbles."""
        self.msg_outer = tk.Frame(self.dialog, bg=COLOURS["chat_bg"])
        self.msg_outer.pack(fill="both", expand=True)

        # Canvas enables smooth scrolling
        self.msg_canvas = tk.Canvas(self.msg_outer, bg=COLOURS["chat_bg"],
                                    highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(self.msg_outer, orient="vertical",
                           command=self.msg_canvas.yview)
        self.msg_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.msg_canvas.pack(side="left", fill="both", expand=True)

        # Inner frame holds the actual message bubble widgets
        self.msg_frame = tk.Frame(self.msg_canvas, bg=COLOURS["chat_bg"])
        self.msg_canvas.create_window((0, 0), window=self.msg_frame,
                                      anchor="nw", width=490)

        # Update scroll region whenever new messages are added
        self.msg_frame.bind("<Configure>", lambda e: self.msg_canvas.configure(
            scrollregion=self.msg_canvas.bbox("all")))

        # Mouse wheel scrolling
        for w in [self.msg_canvas, self.msg_frame]:
            w.bind("<MouseWheel>", lambda e: self.msg_canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"))

    def _build_typing_indicator(self):
        """Animated '...' row shown while AI is generating a response."""
        self.typing_frame = tk.Frame(self.dialog, bg=COLOURS["chat_bg"], height=32)
        self.typing_frame.pack(fill="x", padx=16, pady=2)
        # Label starts hidden — shown only when AI is processing
        self.typing_label = tk.Label(self.typing_frame,
                                     text="\u2746  Style Agent is thinking...",
                                     font=("Segoe UI", 9, "italic"),
                                     fg=COLOURS["gold_primary"], bg=COLOURS["chat_bg"])

    def _show_typing(self):
        """Show the typing indicator and start animating it."""
        self.is_typing = True
        self.typing_label.pack(side="left", pady=4)
        self._animate_typing()

    def _hide_typing(self):
        """Hide the typing indicator and stop the animation."""
        self.is_typing = False
        self.typing_label.pack_forget()

    def _animate_typing(self):
        """Cycles through 1-3 dots every 400ms to show 'thinking' animation."""
        if not self.is_typing:
            return   # stop animating if hidden
        self.typing_dots = (self.typing_dots % 3) + 1
        filled = "\u25cf" * self.typing_dots + "\u25cb" * (3 - self.typing_dots)
        self.typing_label.config(text=f"\u2746  Style Agent is thinking  {filled}")
        self.dialog.after(400, self._animate_typing)   # schedule next frame

    def _build_input_bar(self):
        """Fixed input bar at the bottom with text box and send button."""
        tk.Frame(self.dialog, bg=COLOURS["border_light"], height=1).pack(fill="x")
        bar = tk.Frame(self.dialog, bg=COLOURS["bg_primary"], pady=12)
        bar.pack(fill="x", side="bottom", padx=16)

        # Bordered container for the text entry
        ctr = tk.Frame(bar, bg=COLOURS["bg_input"], highlightthickness=1,
                       highlightbackground=COLOURS["border_light"],
                       highlightcolor=COLOURS["gold_primary"])
        ctr.pack(fill="x", side="left", expand=True, padx=(0, 8))

        # Multi-line text widget (2 rows tall)
        self.input_box = tk.Text(ctr, font=("Segoe UI", 10),
                                 bg=COLOURS["bg_input"], fg=COLOURS["text_primary"],
                                 relief="flat", bd=0, height=2, wrap="word",
                                 insertbackground=COLOURS["gold_primary"],
                                 highlightthickness=0)
        self.input_box.pack(fill="x", padx=10, pady=8)

        # Placeholder text — shown when field is empty
        self.ph = "Ask your stylist anything..."
        self.input_box.insert("1.0", self.ph)
        self.input_box.config(fg=COLOURS["text_muted"])
        self.input_box.bind("<FocusIn>",  self._clear_ph)
        self.input_box.bind("<FocusOut>", self._restore_ph)
        self.input_box.bind("<Return>",       self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)  # shift+enter = newline

        # Gold send button
        tk.Button(bar, text="\u27a4", font=("Segoe UI", 14, "bold"),
                  bg=COLOURS["gold_primary"], fg=COLOURS["bg_primary"],
                  relief="flat", bd=0, width=3, height=1, cursor="hand2",
                  activebackground=COLOURS["gold_dark"],
                  command=self._send).pack(side="right", ipady=8)

    def _clear_ph(self, e):
        """Clear placeholder text when user clicks into the input field."""
        if self.input_box.get("1.0", "end").strip() == self.ph:
            self.input_box.delete("1.0", "end")
            self.input_box.config(fg=COLOURS["text_primary"])

    def _restore_ph(self, e):
        """Restore placeholder text if user leaves the field empty."""
        if not self.input_box.get("1.0", "end").strip():
            self.input_box.insert("1.0", self.ph)
            self.input_box.config(fg=COLOURS["text_muted"])

    def _on_enter(self, e):
        """Send on Enter key press (without Shift)."""
        self._send()
        return "break"   # prevent Enter from adding a newline

    def _send(self):
        """Read input, add user bubble, show typing indicator, call AI in thread."""
        text = self.input_box.get("1.0", "end").strip()
        if not text or text == self.ph:
            return
        self.input_box.delete("1.0", "end")
        self._add_user_message(text)
        self._show_typing()
        threading.Thread(target=self._get_response, args=(text,), daemon=True).start()

    def _get_response(self, user_text):
        """Call Ollama in background thread so UI stays responsive."""
        import subprocess
        sys_p = (
            "You are an expert AI fashion stylist specialising in Indian and Western fashion. "
            "You know Indian ethnic wear: sarees, lehengas, anarkalis, shararas, salwar suits. "
            "Give warm, specific, practical advice with jewellery and accessories."
        )
        try:
            r = subprocess.run(
                ["ollama", "run", "llama3"],
                input=f"{sys_p}\n\nUser: {user_text}\n\nStylist:",
                capture_output=True, text=True, timeout=60)
            resp = r.stdout.strip() or "I couldn't generate a response. Is Ollama running?"
        except subprocess.TimeoutExpired:
            resp = "Response took too long. Try a shorter question!"
        except FileNotFoundError:
            resp = "Ollama not found. Run 'ollama serve' in your terminal, then try again."
        except Exception as ex:
            resp = f"Error: {ex}"
        self.dialog.after(0, lambda: self._on_response(resp))

    def _on_response(self, text):
        """Called on main thread after AI responds — hide typing, show bubble."""
        self._hide_typing()
        self._add_ai_message(text)

    def _add_user_message(self, text):
        """Right-aligned gold bubble — user's message."""
        row = tk.Frame(self.msg_frame, bg=COLOURS["chat_bg"])
        row.pack(fill="x", padx=12, pady=4)
        tk.Frame(row, bg=COLOURS["chat_bg"]).pack(side="left", expand=True)  # left spacer
        tk.Label(row, text=text, font=("Segoe UI", 10),
                 bg=COLOURS["gold_primary"], fg=COLOURS["bg_primary"],
                 wraplength=320, justify="left", padx=14, pady=10).pack(side="right")
        self.dialog.after(50, lambda: self.msg_canvas.yview_moveto(1.0))  # scroll down

    def _add_ai_message(self, text):
        """Left-aligned white card with gold avatar — AI's message."""
        row = tk.Frame(self.msg_frame, bg=COLOURS["chat_bg"])
        row.pack(fill="x", padx=12, pady=4, anchor="w")
        # Small gold avatar
        tk.Label(row, text="\u2746", font=("Georgia", 10, "bold"),
                 bg=COLOURS["gold_primary"], fg=COLOURS["bg_primary"],
                 width=2, height=1, padx=4, pady=4).pack(side="left", anchor="n", pady=2)
        # White card with thin border
        outer = tk.Frame(row, bg=COLOURS["border_light"], padx=1, pady=1)
        outer.pack(side="left", padx=(6, 50))
        tk.Label(outer, text=text, font=("Segoe UI", 10),
                 bg=COLOURS["bg_card"], fg=COLOURS["text_primary"],
                 wraplength=340, justify="left", padx=14, pady=10).pack()
        self.dialog.after(50, lambda: self.msg_canvas.yview_moveto(1.0))  # scroll down


# =============================================================
# CLASS: StyleAgentApp
# =============================================================
class StyleAgentApp:

    def __init__(self):
        # Main window
        self.root = tk.Tk()
        self.root.title("Style Agent")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLOURS["bg_primary"])
        self.root.resizable(True, True)
        self.root.minsize(1200, 750)

        # State variables
        self.selected_vibe      = tk.StringVar(value="Ethnic")
        self.selected_occasion  = tk.StringVar(value="Wedding Guest")
        self.selected_size      = tk.StringVar(value="M")
        self.selected_undertone = tk.StringVar(value="warm")
        self.selected_body      = tk.StringVar(value="Hourglass")
        self.selected_harmony   = tk.StringVar(value="Surprise Me")
        self.selected_budget    = tk.IntVar(value=3000)   # single total budget (Upgrade 3)
        self.name_var           = tk.StringVar(value="")
        self.fav_colours        = set()
        self.avoid_colours      = set()
        self.vibe_tiles         = {}
        self.fav_tiles          = {}
        self.avoid_tiles        = {}
        self.outfit_results     = []
        self.status_var         = tk.StringVar(value="Ready — fill in your details and click Generate")

        self._setup_style()
        self._build_layout()

    # ── ttk style configuration ───────────────────────────────
    def _setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        C = COLOURS
        style.configure("TFrame",       background=C["bg_primary"])
        style.configure("TLabel",       background=C["bg_primary"], foreground=C["text_primary"])
        style.configure("TCombobox",    fieldbackground=C["bg_input"], background=C["bg_input"],
                        foreground=C["text_primary"], font=FONTS["body"])
        style.configure("TRadiobutton", background=C["bg_secondary"], foreground=C["text_primary"])
        style.configure("TScale",       background=C["bg_secondary"], troughcolor=C["border_light"])
        style.configure("Gold.TProgressbar", troughcolor=C["border_light"],
                        background=C["gold_primary"], thickness=8)
        try:
            style.layout("Horizontal.Gold.TProgressbar",
                         style.layout("Horizontal.TProgressbar"))
        except Exception:
            pass
        style.map("TCombobox",
                  selectbackground=[("readonly", C["bg_input"])],
                  selectforeground=[("readonly", C["gold_dark"])])

    # ── Master 3-column layout ────────────────────────────────
    def _build_layout(self):
        """Dark nav bar at top, then 3-column body below."""

        # ── TOP NAV BAR ─────────────────────────────────
        # Full-width dark bar with logo, tagline, and chat button
        nav = tk.Frame(self.root, bg=COLOURS["darkbg_header"], height=52)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)   # keep it exactly 52px tall

        # Logo text on the left
        tk.Label(nav, text="❆  Style Agent",
                 font=("Georgia", 16, "bold"), fg=COLOURS["gold_primary"],
                 bg=COLOURS["darkbg_header"], padx=24
                 ).pack(side="left", pady=12)

        # Tagline next to logo
        tk.Label(nav, text="Your Personal AI Fashion Stylist",
                 font=("Segoe UI", 9), fg=COLOURS["text_muted"],
                 bg=COLOURS["darkbg_header"]).pack(side="left", pady=12)

        # 'Ask Stylist' button on the right — opens the ChatGPT-style dialog
        chat_btn = tk.Button(
            nav, text="💬  Ask Stylist",
            font=FONTS["btn_secondary"],
            bg=COLOURS["gold_primary"], fg=COLOURS["darkbg_header"],
            relief="flat", bd=0, padx=16, pady=6, cursor="hand2",
            activebackground=COLOURS["gold_dark"],
            activeforeground=COLOURS["bg_primary"],
            command=lambda: StyleChatDialog(self.root)   # open floating dialog
        )
        chat_btn.pack(side="right", padx=20, pady=10)
        chat_btn.bind("<Enter>", lambda e: chat_btn.config(
            bg=COLOURS["gold_dark"], fg=COLOURS["bg_primary"]))
        chat_btn.bind("<Leave>", lambda e: chat_btn.config(
            bg=COLOURS["gold_primary"], fg=COLOURS["darkbg_header"]))

        # Gold accent line under the nav bar
        tk.Frame(self.root, bg=COLOURS["gold_primary"], height=2).pack(fill="x")

        # ── 3-COLUMN BODY ─────────────────────────────────
        top = tk.Frame(self.root, bg=COLOURS["bg_primary"])
        top.pack(fill="both", expand=True)

        # Left sidebar — 260px fixed
        self.left_col = tk.Frame(top, bg=COLOURS["bg_secondary"], width=260)
        self.left_col.pack(side="left", fill="y")
        self.left_col.pack_propagate(False)

        # Light vertical separator
        tk.Frame(top, bg=COLOURS["border_light"], width=1).pack(side="left", fill="y")

        # Centre — expands to fill remaining space
        self.centre_col = tk.Frame(top, bg=COLOURS["bg_primary"])
        self.centre_col.pack(side="left", fill="both", expand=True)

        # Light vertical separator
        tk.Frame(top, bg=COLOURS["border_light"], width=1).pack(side="left", fill="y")

        # Right results panel — 460px fixed
        self.right_col = tk.Frame(top, bg=COLOURS["bg_secondary"], width=460)
        self.right_col.pack(side="left", fill="y")
        self.right_col.pack_propagate(False)

        self._build_left_sidebar(self.left_col)
        self._build_centre_column(self.centre_col)
        self._build_right_column(self.right_col)

    # ── Small helper: gold divider line ───────────────────────
    def _divider(self, parent, colour=None, padx=16):
        tk.Frame(parent, bg=colour or COLOURS["gold_primary"], height=1).pack(
            fill="x", padx=padx, pady=4)

    # =========================================================
    # LEFT SIDEBAR — PROFILE
    # =========================================================
    def _build_left_sidebar(self, parent):
        # App logo
        tk.Label(parent, text="✦  Style Agent",
                 font=FONTS["heading_large"], fg=COLOURS["gold_dark"],
                 bg=COLOURS["bg_secondary"]).pack(pady=(18,2), padx=16)
        self._divider(parent)

        # Scrollable interior so fields don't get clipped on small screens
        canvas = tk.Canvas(parent, bg=COLOURS["bg_secondary"], highlightthickness=0)
        sb     = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=COLOURS["bg_secondary"])
        win   = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))

        # Shared entry style
        ES = dict(font=FONTS["body"], bg=COLOURS["bg_input"],
                  fg=COLOURS["text_primary"], relief="flat", bd=4,
                  highlightthickness=1, highlightbackground=COLOURS["border_light"],
                  highlightcolor=COLOURS["gold_primary"])

        def slbl(text):
            """Small section label above each input."""
            tk.Label(inner, text=text, font=FONTS["small"],
                     fg=COLOURS["text_secondary"],
                     bg=COLOURS["bg_secondary"]).pack(anchor="w", padx=16, pady=(10,2))

        # Name
        slbl("YOUR NAME")
        tk.Entry(inner, textvariable=self.name_var,
                 insertbackground=COLOURS["gold_primary"],
                 **ES).pack(fill="x", padx=16, pady=(0,4))

        # Body type
        slbl("BODY TYPE")
        ttk.Combobox(inner, textvariable=self.selected_body, state="readonly",
                     values=["Hourglass","Pear","Apple","Rectangle","Petite","Plus Size"],
                     font=FONTS["body"]).pack(fill="x", padx=16, pady=(0,4))

        # Skin undertone
        slbl("SKIN UNDERTONE")
        ut_frame = tk.Frame(inner, bg=COLOURS["bg_secondary"])
        ut_frame.pack(fill="x", padx=16, pady=(0,4))
        for lbl, val, swatch in [("Warm","warm","#D2936A"),
                                  ("Cool","cool","#B0C4DE"),
                                  ("Neutral","neutral","#C9B99A")]:
            row = tk.Frame(ut_frame, bg=COLOURS["bg_secondary"])
            row.pack(fill="x", pady=1)
            tk.Label(row, text="  ", bg=swatch, width=2).pack(side="left", padx=(0,6))
            tk.Radiobutton(row, text=lbl, variable=self.selected_undertone, value=val,
                           font=FONTS["body"], fg=COLOURS["text_primary"],
                           bg=COLOURS["bg_secondary"], selectcolor=COLOURS["gold_light"],
                           activebackground=COLOURS["bg_secondary"]).pack(side="left")

        # Size
        slbl("SIZE")
        sz_frame = tk.Frame(inner, bg=COLOURS["bg_secondary"])
        sz_frame.pack(fill="x", padx=16, pady=(0,4))
        for i, sz in enumerate(["XS","S","M","L","XL","XXL"]):
            tk.Radiobutton(sz_frame, text=sz, variable=self.selected_size, value=sz,
                           font=FONTS["small"], fg=COLOURS["text_primary"],
                           bg=COLOURS["bg_secondary"], selectcolor=COLOURS["gold_primary"],
                           activebackground=COLOURS["bg_secondary"]
                           ).grid(row=i//3, column=i%3, padx=2, pady=2, sticky="w")

        # ── Budget Slider — snaps to round steps (Upgrade 3) ──
        slbl("TOTAL OUTFIT BUDGET")
        budget_label_var = tk.StringVar(value="₹3,000")
        tk.Label(inner, textvariable=budget_label_var, font=FONTS["price"],
                 fg=COLOURS["gold_primary"],
                 bg=COLOURS["bg_secondary"]).pack(anchor="w", padx=16)

        def on_slider_move(event=None):
            # Find the nearest allowed step and snap to it
            raw     = budget_slider.get()
            nearest = min(BUDGET_STEPS, key=lambda s: abs(s - raw))
            self.selected_budget.set(nearest)
            budget_label_var.set(f"₹{nearest:,}")

        budget_slider = ttk.Scale(inner, from_=BUDGET_STEPS[0], to=BUDGET_STEPS[-1],
                                  orient="horizontal", variable=self.selected_budget,
                                  command=on_slider_move, length=180)
        budget_slider.pack(fill="x", padx=16, pady=(0,2))
        tk.Label(inner, text="Total for the complete outfit (all pieces combined)",
                 font=FONTS["small"], fg=COLOURS["text_muted"],
                 bg=COLOURS["bg_secondary"], wraplength=180,
                 justify="left").pack(padx=16, anchor="w", pady=(0,10))

    # =========================================================
    # CENTRE COLUMN — 3 stacked panels
    # =========================================================
    def _build_centre_column(self, parent):
        self._build_panel_occasion(parent)
        self._build_panel_colours(parent)
        self._build_panel_generate(parent)

    def _pframe(self, parent, pady=(6,2)):
        """Returns a white panel frame with small padding."""
        f = tk.Frame(parent, bg=COLOURS["bg_primary"])
        f.pack(fill="x", padx=8, pady=pady)
        return f

    def _panel_heading(self, parent, text):
        """Panel heading with gold underline."""
        tk.Label(parent, text=text, font=FONTS["heading_small"],
                 fg=COLOURS["gold_dark"],
                 bg=COLOURS["bg_primary"]).pack(anchor="w", padx=8, pady=(2,4))
        tk.Frame(parent, bg=COLOURS["gold_primary"], height=1).pack(
            fill="x", padx=8, pady=(0,4))

    # ── Panel: Occasion & Vibe ────────────────────────────────
    def _build_panel_occasion(self, parent):
        panel = self._pframe(parent, pady=(8,4))
        self._panel_heading(panel, "🎯  Occasion & Vibe")

        inner = tk.Frame(panel, bg=COLOURS["bg_primary"])
        inner.pack(fill="x", padx=8, pady=4)

        # Left: occasion dropdown
        occ_f = tk.Frame(inner, bg=COLOURS["bg_primary"])
        occ_f.pack(side="left", fill="x", expand=True, padx=(0,12))
        tk.Label(occ_f, text="OCCASION", font=FONTS["small"],
                 fg=COLOURS["text_secondary"],
                 bg=COLOURS["bg_primary"]).pack(anchor="w")
        ttk.Combobox(occ_f, textvariable=self.selected_occasion,
                     values=OCCASIONS, state="readonly",
                     font=FONTS["body"], width=26).pack(fill="x", pady=(2,0))

        # Right: vibe tiles grid — each tile has an emoji + name + vibe accent colour
        vibe_o = tk.Frame(inner, bg=COLOURS["bg_primary"])
        vibe_o.pack(side="left")
        tk.Label(vibe_o, text="VIBE", font=FONTS["small"],
                 fg=COLOURS["text_secondary"],
                 bg=COLOURS["bg_primary"]).pack(anchor="w")
        vibe_grid = tk.Frame(vibe_o, bg=COLOURS["bg_primary"])
        vibe_grid.pack()

        # vibe_tiles now stores (tile_frame, name_label, emoji_label, accent_colour)
        for idx, (emoji, vibe_name, colour_key) in enumerate(VIBES):
            # Outer frame acts as the tile — has a highlight border for selection
            tile = tk.Frame(vibe_grid, bg=COLOURS["bg_primary"],
                            highlightthickness=2,
                            highlightbackground=COLOURS["border_light"],
                            cursor="hand2", width=110, height=72)
            tile.grid(row=idx//4, column=idx%4, padx=3, pady=3)
            tile.pack_propagate(False)    # keep fixed size

            # Emoji label inside the tile
            el = tk.Label(tile, text=emoji, font=("Segoe UI", 18),
                          bg=COLOURS["bg_primary"], fg=COLOURS["text_secondary"])
            el.pack(pady=(8,2))

            # Vibe name label below emoji
            nl = tk.Label(tile, text=vibe_name, font=FONTS["small"],
                          bg=COLOURS["bg_primary"], fg=COLOURS["text_secondary"])
            nl.pack()

            # Store tile refs with the accent colour for this vibe
            accent = COLOURS[colour_key]
            self.vibe_tiles[vibe_name] = (tile, nl, el, accent)

            # Clicking the tile or its labels all call _select_vibe
            for w in [tile, el, nl]:
                w.bind("<Button-1>", lambda e, v=vibe_name: self._select_vibe(v))

        self._select_vibe("Ethnic")   # default selection

    def _select_vibe(self, val):
        """Highlight the selected vibe tile with its accent colour; grey out others."""
        self.selected_vibe.set(val)
        for vname, (tile, nl, el, accent) in self.vibe_tiles.items():
            if vname == val:
                # Selected: fill with vibe accent colour, white text
                tile.config(bg=accent, highlightbackground=accent)
                el.config(bg=accent, fg=COLOURS["bg_primary"])
                nl.config(bg=accent, fg=COLOURS["bg_primary"])
            else:
                # Deselected: white background, light border
                tile.config(bg=COLOURS["bg_primary"],
                            highlightbackground=COLOURS["border_light"])
                el.config(bg=COLOURS["bg_primary"], fg=COLOURS["text_secondary"])
                nl.config(bg=COLOURS["bg_primary"], fg=COLOURS["text_secondary"])

    # ── Panel: Colour Preferences ─────────────────────────────
    # ── Panel: Colour Preferences (Fix 2 — full hex picker) ─────────
    def _build_panel_colours(self, parent):
        """
        Builds the colour preferences panel with:
        Part A: 24-colour curated swatch grid (quick pick)
        Part B: 'Pick Any Colour' button — opens OS colour wheel
        Part C: Manual hex entry field + Add button
        Part D: Selected colours strip showing all chosen colours
        Part E: 'AVOID THESE' swatch grid (same swatches, separate list)
        Part F: Colour Harmony radio buttons
        """
        panel = self._pframe(parent, pady=(2,4))
        self._panel_heading(panel, "🎨  Colour Preferences")

        outer = tk.Frame(panel, bg=COLOURS["bg_primary"])
        outer.pack(fill="x", padx=8, pady=4)

        # ── LEFT: Favourite colours ─────────────────────────────
        fav_sec = tk.Frame(outer, bg=COLOURS["bg_primary"])
        fav_sec.pack(side="left", anchor="n", padx=(0,14))

        tk.Label(fav_sec, text="FAVOURITE COLOURS", font=FONTS["small"],
                 fg=COLOURS["text_secondary"],
                 bg=COLOURS["bg_primary"]).pack(anchor="w")

        # 24-colour curated fashion swatch grid (6 columns x 4 rows)
        FASHION_SWATCHES = [
            ("White",    "#FFFFFF"), ("Ivory",   "#FFFFF0"),
            ("Cream",    "#F5F0E8"), ("Beige",   "#F5DEB3"),
            ("Camel",    "#C19A6B"), ("Black",   "#1A1A1A"),
            ("Deep Red", "#8B0000"), ("Red",     "#C0392B"),
            ("Burnt Org","#CC5500"), ("Mustard", "#FFDB58"),
            ("Terracotta","#C67C5A"),("Rust",    "#B7410E"),
            ("Navy",     "#000080"), ("Cobalt",  "#0047AB"),
            ("Sky Blue", "#87CEEB"), ("Emerald", "#046307"),
            ("Sage",     "#B2AC88"), ("Purple",  "#7D3C98"),
            ("Blush",    "#FFB6C1"), ("Lavender","#B57EDC"),
            ("Mint",     "#98D8C8"), ("Peach",   "#FFCBA4"),
            ("Gold",     "#D4AF37"), ("Silver",  "#C0C0C0"),
        ]   # 24 swatches covering all major Indian fashion colour families

        swatch_grid = tk.Frame(fav_sec, bg=COLOURS["bg_primary"])
        swatch_grid.pack(pady=(2,4))

        # Store outer-frame refs so we can update borders on select/deselect
        fav_swatch_outers = {}   # hex_code → outer border frame

        def on_fav_swatch(hx, outer_frame):
            """Toggle a curated swatch on/off for favourite colours."""
            if hx in self.fav_colours:
                self.fav_colours.discard(hx)              # deselect
                outer_frame.config(bg=COLOURS["border_light"])  # reset border
            else:
                self.fav_colours.add(hx)                  # select
                outer_frame.config(bg=COLOURS["gold_primary"])  # gold border
            _update_selected_strip()                       # refresh strip below

        for idx, (name, hx) in enumerate(FASHION_SWATCHES):
            # Each swatch is a coloured label inside a thin outer frame (acts as border)
            outer_f = tk.Frame(swatch_grid, bg=COLOURS["border_light"], padx=1, pady=1)
            outer_f.grid(row=idx//6, column=idx%6, padx=2, pady=2)
            swatch = tk.Label(outer_f, bg=hx, width=3, height=1, cursor="hand2")
            swatch.pack()
            swatch.bind("<Enter>", lambda e, n=name: self.status_var.set(f"Colour: {n}"))
            swatch.bind("<Leave>", lambda e: self.status_var.set(""))
            swatch.bind("<Button-1>", lambda e, h=hx, o=outer_f: on_fav_swatch(h, o))
            fav_swatch_outers[hx] = outer_f

        # ── Hex colour picker row ─────────────────────────────
        tk.Frame(fav_sec, bg=COLOURS["border_light"], height=1).pack(fill="x", pady=4)
        picker_row = tk.Frame(fav_sec, bg=COLOURS["bg_primary"])
        picker_row.pack(anchor="w", pady=2)

        # Colour preview square (shows last custom colour)
        custom_preview = tk.Label(picker_row, bg=COLOURS["bg_input"],
                                  width=2, height=1, relief="flat",
                                  highlightthickness=1,
                                  highlightbackground=COLOURS["border_light"])
        custom_preview.pack(side="left", padx=(0,4))

        hex_var = tk.StringVar(value="#C9A84C")  # default to gold
        hex_entry = tk.Entry(picker_row, textvariable=hex_var, font=FONTS["mono"],
                             width=9, bg=COLOURS["bg_input"], fg=COLOURS["text_primary"],
                             relief="flat", bd=0, highlightthickness=1,
                             highlightbackground=COLOURS["border_light"],
                             highlightcolor=COLOURS["gold_primary"],
                             insertbackground=COLOURS["gold_primary"])
        hex_entry.pack(side="left", padx=(0,4))

        def add_custom_hex(event=None):
            """Validates and adds the hex code currently in the entry field."""
            raw = hex_var.get().strip()
            if not raw.startswith("#"):
                raw = "#" + raw           # add # if user forgot it
            valid = set("0123456789abcdefABCDEF")
            if len(raw) == 7 and all(c in valid for c in raw[1:]):
                hx = raw.upper()          # normalise to uppercase
                self.fav_colours.add(hx) # add to favourites
                custom_preview.config(bg=raw)     # update preview swatch
                _update_selected_strip()           # refresh strip
            else:
                # Flash red border to signal bad input
                hex_entry.config(highlightbackground=COLOURS["error"])
                hex_entry.after(1500, lambda:
                    hex_entry.config(highlightbackground=COLOURS["border_light"]))

        hex_entry.bind("<Return>", add_custom_hex)  # Enter key adds the hex

        add_btn = tk.Button(picker_row, text="Add", font=FONTS["small"],
                            bg=COLOURS["gold_primary"], fg=COLOURS["bg_primary"],
                            relief="flat", padx=6, pady=3, cursor="hand2",
                            command=add_custom_hex)
        add_btn.pack(side="left", padx=(0,4))

        def open_colour_picker():
            """
            Opens the operating system colour picker dialog (built into tkinter).
            Returns (#rrggbb, (r,g,b)) or (None, None) if user cancels.
            """
            start = self.fav_colours and list(self.fav_colours)[-1] or COLOURS["gold_primary"]
            result = colorchooser.askcolor(title="Pick Your Colour", color=start)
            if result[1] is not None:          # user picked a colour and did not cancel
                chosen_hex = result[1].upper() # e.g. "#FF6B35"
                hex_var.set(chosen_hex)        # update entry field
                custom_preview.config(bg=result[1])  # update preview square
                self.fav_colours.add(chosen_hex)     # add to favourites
                _update_selected_strip()              # refresh strip

        pick_btn = tk.Button(picker_row, text="🎨 Pick", font=FONTS["small"],
                             bg=COLOURS["bg_input"], fg=COLOURS["text_primary"],
                             relief="flat", padx=8, pady=3, cursor="hand2",
                             highlightthickness=1,
                             highlightbackground=COLOURS["border_light"],
                             command=open_colour_picker)
        pick_btn.pack(side="left")
        pick_btn.bind("<Enter>", lambda e: pick_btn.config(
            bg=COLOURS["gold_light"], highlightbackground=COLOURS["gold_primary"]))
        pick_btn.bind("<Leave>", lambda e: pick_btn.config(
            bg=COLOURS["bg_input"], highlightbackground=COLOURS["border_light"]))

        # ── Selected colours strip ──────────────────────────────
        # Shows all selected colours as a horizontal row of small squares
        strip_frame = tk.Frame(fav_sec, bg=COLOURS["bg_primary"])
        strip_frame.pack(anchor="w", pady=(4,0))

        def _update_selected_strip():
            """Redraws the selected colours strip whenever a colour is added or removed."""
            for w in strip_frame.winfo_children():
                w.destroy()   # clear old content
            if not self.fav_colours:
                tk.Label(strip_frame, text="No colours selected",
                         font=FONTS["small"], fg=COLOURS["text_muted"],
                         bg=COLOURS["bg_primary"]).pack(side="left")
                return
            for hx in sorted(self.fav_colours):
                cell = tk.Frame(strip_frame, bg=COLOURS["bg_primary"])
                cell.pack(side="left", padx=2)
                # Small colour square
                tk.Label(cell, bg=hx, width=2, height=1,
                         highlightthickness=2,
                         highlightbackground=COLOURS["gold_primary"]).pack()
                # Hex code below in tiny monospace
                tk.Label(cell, text=hx, font=("Courier New",7),
                         fg=COLOURS["text_muted"],
                         bg=COLOURS["bg_primary"]).pack()

        _update_selected_strip()   # initial draw (empty state)

        def clear_all():
            """Clears all selected favourite colours and resets all swatch borders."""
            self.fav_colours.clear()
            for o in fav_swatch_outers.values():
                o.config(bg=COLOURS["border_light"])  # reset all borders to grey
            _update_selected_strip()                   # redraw strip with empty state

        tk.Button(fav_sec, text="✕ Clear All", font=FONTS["small"],
                  bg=COLOURS["bg_primary"], fg=COLOURS["text_muted"],
                  relief="flat", bd=0, cursor="hand2",
                  command=clear_all).pack(anchor="w", pady=(2,4))

        # ── MIDDLE: Avoid these colours ────────────────────────
        avoid_sec = tk.Frame(outer, bg=COLOURS["bg_primary"])
        avoid_sec.pack(side="left", anchor="n", padx=(0,14))

        tk.Label(avoid_sec, text="AVOID THESE", font=FONTS["small"],
                 fg=COLOURS["text_secondary"],
                 bg=COLOURS["bg_primary"]).pack(anchor="w")
        avoid_grid = tk.Frame(avoid_sec, bg=COLOURS["bg_primary"])
        avoid_grid.pack(pady=(2,0))

        for idx, (name, hx) in enumerate(COLOUR_GRID):
            # Reuse the existing COLOUR_GRID constant (20 colours) for the avoid section
            tile = tk.Label(avoid_grid, bg=hx, width=3, height=1, relief="flat",
                            cursor="hand2", highlightthickness=1,
                            highlightbackground=COLOURS["border_light"])
            tile.grid(row=idx//4, column=idx%4, padx=2, pady=2)
            tile.bind("<Enter>", lambda e, n=name: self.status_var.set(f"Avoid: {n}"))
            tile.bind("<Leave>", lambda e: self.status_var.set(""))
            tile.bind("<Button-1>", lambda e, h=hx, t=tile: self._toggle_avoid(h, t))
            self.avoid_tiles[hx] = tile

        # ── RIGHT: Colour Harmony radio buttons ────────────────
        harm = tk.Frame(outer, bg=COLOURS["bg_primary"])
        harm.pack(side="left", anchor="n")
        tk.Label(harm, text="COLOUR HARMONY", font=FONTS["small"],
                 fg=COLOURS["text_secondary"],
                 bg=COLOURS["bg_primary"]).pack(anchor="w")
        for h in HARMONIES:
            tk.Radiobutton(harm, text=h, variable=self.selected_harmony, value=h,
                           font=FONTS["small"], fg=COLOURS["text_primary"],
                           bg=COLOURS["bg_primary"], selectcolor=COLOURS["gold_primary"],
                           activebackground=COLOURS["bg_primary"]).pack(anchor="w", pady=1)

    def _toggle_fav(self, hx, tile):
        """Kept for backward compat — curated swatch toggle is now inline in _build_panel_colours."""
        if hx in self.fav_colours:
            self.fav_colours.discard(hx)
            tile.config(highlightthickness=1, highlightbackground=COLOURS["border_light"])
        else:
            self.fav_colours.add(hx)
            tile.config(highlightthickness=3, highlightbackground=COLOURS["gold_primary"])

    def _toggle_avoid(self, hx, tile):
        """Toggles a colour in the avoid list. Called by the avoid swatch grid."""
        if hx in self.avoid_colours:
            self.avoid_colours.discard(hx)
            tile.config(highlightthickness=1, highlightbackground=COLOURS["border_light"])
        else:
            self.avoid_colours.add(hx)
            tile.config(highlightthickness=3, highlightbackground=COLOURS["error"])

    # ── Panel: Generate Button ────────────────────────────────
    def _build_panel_generate(self, parent):
        panel = self._pframe(parent, pady=(4,8))
        inner = tk.Frame(panel, bg=COLOURS["bg_primary"])
        inner.pack(fill="x", padx=8, pady=8)

        self.gen_btn = tk.Button(inner, text="✦  Generate My Outfits",
                                 font=("Georgia", 13, "bold"),
                                 bg=COLOURS["darkbg_header"],   # near-black — matches nav bar
                                 fg=COLOURS["gold_primary"],    # gold text
                                 activebackground=COLOURS["gold_primary"],   # gold on press
                                 activeforeground=COLOURS["darkbg_header"],  # dark text on press
                                 relief="flat", padx=28, pady=12,
                                 cursor="hand2", command=self._on_generate)
        self.gen_btn.pack(pady=(0,8))
        # Hover: flip to gold background + dark text
        self.gen_btn.bind("<Enter>", lambda e: self.gen_btn.config(
            bg=COLOURS["gold_primary"], fg=COLOURS["darkbg_header"]))
        self.gen_btn.bind("<Leave>", lambda e: self.gen_btn.config(
            bg=COLOURS["darkbg_header"], fg=COLOURS["gold_primary"]))

        self.progress = ttk.Progressbar(inner, orient="horizontal",
                                        mode="indeterminate",
                                        style="Gold.TProgressbar", length=400)
        self.progress.pack(fill="x", pady=(0,4))

        tk.Label(inner, textvariable=self.status_var, font=FONTS["small"],
                 fg=COLOURS["text_secondary"],
                 bg=COLOURS["bg_primary"], wraplength=400).pack()

    # =========================================================
    # RIGHT COLUMN — Results (top) + Chat (bottom)
    # =========================================================
    def _build_right_column(self, parent):
        """Dark header bar at top, then scrollable outfit results below."""
        # Dark header bar — matches nav bar style
        hdr = tk.Frame(parent, bg=COLOURS["darkbg_header"], height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  👗  Your Curated Looks",
                 font=("Georgia", 12, "bold"), fg=COLOURS["gold_primary"],
                 bg=COLOURS["darkbg_header"], pady=10).pack(side="left")
        tk.Frame(parent, bg=COLOURS["gold_primary"], height=2).pack(fill="x")
        self._build_results_area(parent)

    # ── Results: scrollable outfit cards ─────────────────────
    def _build_results_area(self, parent):
        tk.Label(parent, text="👗  Your Looks", font=FONTS["heading_small"],
                 fg=COLOURS["gold_dark"],
                 bg=COLOURS["bg_primary"]).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(parent, bg=COLOURS["gold_primary"], height=1).pack(fill="x", padx=12)

        self.results_canvas = tk.Canvas(parent, bg=COLOURS["bg_primary"],
                                        highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=self.results_canvas.yview)
        self.results_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.results_canvas.pack(side="left", fill="both", expand=True)

        self.results_inner = tk.Frame(self.results_canvas, bg=COLOURS["bg_primary"])
        self.results_win   = self.results_canvas.create_window(
            (0, 0), window=self.results_inner, anchor="nw")
        self.results_inner.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(
                scrollregion=self.results_canvas.bbox("all")))
        self.results_canvas.bind(
            "<Configure>",
            lambda e: self.results_canvas.itemconfig(self.results_win, width=e.width))
        self.results_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.results_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        tk.Label(self.results_inner,
                 text="Your outfit recommendations\nwill appear here.",
                 font=FONTS["body"], fg=COLOURS["text_muted"],
                 bg=COLOURS["bg_primary"], justify="center").pack(pady=30)

    # ── Chat: AI stylist at bottom of right column ────────────
    def _build_chat_area(self, parent):
        chat_outer = tk.Frame(parent, bg=COLOURS["bg_primary"])
        chat_outer.pack(fill="x", side="bottom")

        tk.Label(chat_outer, text="💬  AI Stylist Chat",
                 font=FONTS["heading_small"], fg=COLOURS["gold_dark"],
                 bg=COLOURS["bg_primary"]).pack(anchor="w", padx=12, pady=(8,2))

        self.chat_display = scrolledtext.ScrolledText(
            chat_outer, height=6, font=FONTS["body"],
            bg=COLOURS["bg_primary"], fg=COLOURS["text_primary"],
            relief="flat", state="disabled", wrap="word", highlightthickness=0)
        self.chat_display.pack(fill="x", padx=8, pady=(0,4))
        self.chat_display.tag_configure("user_msg",
                                        foreground=COLOURS["gold_dark"], font=FONTS["body_bold"])
        self.chat_display.tag_configure("ai_msg",
                                        foreground=COLOURS["text_primary"], font=FONTS["body"])
        self.chat_display.tag_configure("ai_label",
                                        foreground=COLOURS["gold_primary"], font=FONTS["small"])

        input_row = tk.Frame(chat_outer, bg=COLOURS["bg_primary"])
        input_row.pack(fill="x", padx=8, pady=(0,8))

        self.chat_input = tk.Entry(input_row, font=FONTS["body"],
                                   bg=COLOURS["bg_input"], fg=COLOURS["text_primary"],
                                   relief="flat", bd=4, highlightthickness=1,
                                   highlightbackground=COLOURS["border_light"],
                                   highlightcolor=COLOURS["gold_primary"],
                                   insertbackground=COLOURS["gold_primary"])
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.chat_input.bind("<Return>", lambda e: self._send_chat())

        send_btn = tk.Button(input_row, text="Send ➤", font=FONTS["body_bold"],
                             bg=COLOURS["gold_primary"], fg=COLOURS["bg_primary"],
                             relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
                             command=self._send_chat)
        send_btn.pack(side="left")
        send_btn.bind("<Enter>", lambda e: send_btn.config(bg=COLOURS["gold_dark"]))
        send_btn.bind("<Leave>", lambda e: send_btn.config(bg=COLOURS["gold_primary"]))

    # =========================================================
    # GENERATION — on click, thread, done
    # =========================================================
    def _on_generate(self):
        self.gen_btn.config(state="disabled", text="⏳  Generating...")
        self.progress.start(12)
        self.status_var.set("🌐  Scouting 2026 trends...")

        # Map GUI label → DB keyword (fixes the occasion mismatch bug)
        raw_occ    = self.selected_occasion.get()
        mapped_occ = OCCASION_MAP.get(
            raw_occ, raw_occ.lower().replace(" / ", " ").replace(" ", "_"))

        user_input = {
            "name":              self.name_var.get() or "Valued Customer",
            "body_type":         self.selected_body.get(),
            "skin_undertone":    self.selected_undertone.get(),
            "total_budget":      self.selected_budget.get(),   # Upgrade 2: single budget
            "size":              self.selected_size.get(),
            "occasion":          mapped_occ,
            "vibe":              self.selected_vibe.get(),
            "favourite_colours": list(self.fav_colours) or ["#C67C5A"],
            "avoid_colours":     list(self.avoid_colours),
            "colour_harmony":    self.selected_harmony.get(),
            "user_id":           1,
        }
        threading.Thread(target=self._run_pipeline_thread,
                         args=(user_input,), daemon=True).start()

    def _run_pipeline_thread(self, user_input):
        def set_status(msg):
            self.root.after(0, lambda: self.status_var.set(msg))
        try:
            set_status("🤖  Running Style Agent pipeline...")
            from workflow.langgraph_state import run_pipeline
            result          = run_pipeline(user_input)
            self.outfit_results = result.get("final_recommendations", [])
            self.root.after(0, lambda: self._display_results(result))
        except Exception as err:
            self.root.after(0, lambda: self.status_var.set(f"⚠️  Error: {err}"))
        finally:
            self.root.after(0, self._generation_done)

    def _generation_done(self):
        self.progress.stop()
        self.gen_btn.config(state="normal", text="✦  Generate My Outfits")
        self.status_var.set("✅  Your looks are ready!")

    # =========================================================
    # RESULTS — draw outfit cards
    # =========================================================
    def _display_results(self, state_dict):
        for w in self.results_inner.winfo_children():
            w.destroy()
        recs = state_dict.get("final_recommendations", [])
        if not recs:
            tk.Label(self.results_inner,
                     text="No outfits found.\nRun setup_database.py then try again.",
                     font=FONTS["body"], fg=COLOURS["text_muted"],
                     bg=COLOURS["bg_primary"], justify="center").pack(pady=30)
            return
        for i, rec in enumerate(recs):
            self._build_outfit_card(self.results_inner, rec, i + 1)
        self.status_var.set(f"✅  {len(recs)} looks generated!")

    # ── Helper: clickable shopping link label (Upgrade 1) ─────
    def _add_shopping_link(self, parent, url, source):
        lbl = tk.Label(parent, text=f"🛍  Buy on {source}",
                       font=FONTS["link"], fg=COLOURS["gold_primary"],
                       bg=COLOURS["bg_card"], cursor="hand2")
        lbl.pack(anchor="w", padx=32, pady=1)
        lbl.bind("<Enter>", lambda e: lbl.config(fg=COLOURS["gold_dark"]))
        lbl.bind("<Leave>", lambda e: lbl.config(fg=COLOURS["gold_primary"]))
        if url:
            lbl.bind("<Button-1>", lambda e: webbrowser.open(url))

    # ── Helper: thin budget bar inside card (Upgrade 2) ───────
    def _draw_budget_bar(self, parent, total_cost, total_budget):
        if total_budget <= 0:
            return
        fraction = min(total_cost / total_budget, 1.0)
        bar = tk.Canvas(parent, height=6, bg=COLOURS["bg_card"], highlightthickness=0)
        bar.pack(fill="x", padx=16, pady=(2,4))
        bar.update_idletasks()
        width = bar.winfo_width() or 300
        bar.create_rectangle(0, 0, width, 6, fill=COLOURS["border_light"], outline="")
        bar.create_rectangle(0, 0, int(width * fraction), 6,
                             fill=COLOURS["gold_primary"], outline="")

    # ── Main outfit card widget ───────────────────────────────
    def _build_outfit_card(self, parent, rec, outfit_num):
        outfit       = rec.get("outfit", {})
        kit          = rec.get("jewellery_kit", {})
        total_cost   = outfit.get("total_cost", 0)
        total_budget = outfit.get("budget_given", 0)

        # Card outer frame — cream background, light border
        card = tk.Frame(parent, bg=COLOURS["bg_card"],
                        highlightthickness=1,
                        highlightbackground=COLOURS["border_light"])
        card.pack(fill="x", padx=8, pady=6)

        # Palette name heading
        tk.Label(card, text=f"  {outfit.get('palette_name', f'Look {outfit_num}')}",
                 font=FONTS["heading_small"], fg=COLOURS["gold_dark"],
                 bg=COLOURS["bg_card"]).pack(anchor="w", padx=12, pady=(10,2))

        # Colour swatches row
        sw = tk.Frame(card, bg=COLOURS["bg_card"])
        sw.pack(anchor="w", padx=12, pady=(0,6))
        for s in outfit.get("colour_swatches", []):
            tk.Label(sw, bg=s.get("hex","#888"), width=3, height=1,
                     relief="raised").pack(side="left", padx=2)
            tk.Label(sw, text=s.get("name",""), font=FONTS["small"],
                     fg=COLOURS["text_secondary"],
                     bg=COLOURS["bg_card"]).pack(side="left", padx=(0,8))

        tk.Frame(card, bg=COLOURS["border_light"], height=1).pack(fill="x", padx=12, pady=2)

        # CLOTHING section
        tk.Label(card, text="CLOTHING", font=FONTS["small"],
                 fg=COLOURS["gold_dark"], bg=COLOURS["bg_card"]).pack(
            anchor="w", padx=12, pady=(6,2))

        item_labels = [("dress","👗 DRESS"),("top","👚 TOP"),("bottom","👖 BOTTOM"),
                       ("outerwear","🧥 LAYER"),("footwear","👠 FOOTWEAR"),("bag","👜 BAG")]
        for key, label in item_labels:
            item = outfit.get("items", {}).get(key)
            if not item or not isinstance(item, dict):
                continue
            name  = item.get("name","")
            price = item.get("price","")
            if not name:
                continue
            row = tk.Frame(card, bg=COLOURS["bg_card"])
            row.pack(fill="x", padx=12, pady=1)
            tk.Label(row, text=f"↳ {label}:", font=FONTS["small"],
                     fg=COLOURS["gold_primary"], bg=COLOURS["bg_card"],
                     width=13, anchor="w").pack(side="left")
            tk.Label(row, text=f"{name}  {price}", font=FONTS["small"],
                     fg=COLOURS["text_primary"], bg=COLOURS["bg_card"],
                     wraplength=240, justify="left", anchor="w").pack(side="left", fill="x")
            # Shopping link (Upgrade 1)
            link_url = item.get("shopping_link","")
            source   = item.get("link_source","Google Shopping")
            if link_url:
                self._add_shopping_link(card, link_url, source)

        tk.Frame(card, bg=COLOURS["border_light"], height=1).pack(fill="x", padx=12, pady=2)

        # JEWELLERY section
        if kit:
            tk.Label(card, text="JEWELLERY", font=FONTS["small"],
                     fg=COLOURS["gold_dark"], bg=COLOURS["bg_card"]).pack(
                anchor="w", padx=12, pady=(4,2))
            for jk in ["earrings","necklace","bangles","rings","maang_tikka","optional_extras"]:
                val = kit.get(jk,"")
                if val and "Skip" not in str(val):
                    jr = tk.Frame(card, bg=COLOURS["bg_card"])
                    jr.pack(fill="x", padx=12, pady=1)
                    tk.Label(jr, text=f"↳ {jk.replace('_',' ').title()}:",
                             font=FONTS["small"], fg=COLOURS["text_secondary"],
                             bg=COLOURS["bg_card"], width=16, anchor="w").pack(side="left")
                    tk.Label(jr, text=val, font=FONTS["small"],
                             fg=COLOURS["text_primary"], bg=COLOURS["bg_card"],
                             wraplength=220, justify="left", anchor="w").pack(side="left")
            frag = kit.get("fragrance_note","")
            if frag:
                tk.Label(card, text=f"🌸 {frag}", font=FONTS["small"],
                         fg=COLOURS["text_secondary"], bg=COLOURS["bg_card"],
                         wraplength=330, justify="left").pack(anchor="w", padx=12, pady=2)

        tk.Frame(card, bg=COLOURS["border_light"], height=1).pack(fill="x", padx=12, pady=2)

        # BUDGET BAR (Upgrade 2)
        if total_budget > 0:
            br = tk.Frame(card, bg=COLOURS["bg_card"])
            br.pack(fill="x", padx=12, pady=2)
            remaining  = total_budget - total_cost
            rem_text   = f"  ₹{remaining:,.0f} remaining" if remaining >= 0 else f"  ₹{-remaining:,.0f} over budget"
            rem_colour = COLOURS["success"] if remaining >= 0 else COLOURS["error"]
            tk.Label(br, text="TOTAL:", font=FONTS["small"],
                     fg=COLOURS["gold_dark"], bg=COLOURS["bg_card"]).pack(side="left")
            tk.Label(br, text=f"  ₹{total_cost:,.0f}  of  ₹{total_budget:,}",
                     font=FONTS["body_bold"], fg=COLOURS["text_primary"],
                     bg=COLOURS["bg_card"]).pack(side="left")
            tk.Label(br, text=rem_text, font=FONTS["small"],
                     fg=rem_colour, bg=COLOURS["bg_card"]).pack(side="left")
            self._draw_budget_bar(card, total_cost, total_budget)

        tk.Frame(card, bg=COLOURS["border_light"], height=1).pack(fill="x", padx=12, pady=2)

        # WHY THIS WORKS
        why = outfit.get("why_this_works","")
        if why:
            tk.Label(card, text="WHY THIS WORKS", font=FONTS["small"],
                     fg=COLOURS["gold_dark"], bg=COLOURS["bg_card"]).pack(anchor="w", padx=12)
            tk.Label(card, text=why, font=("Segoe UI", 9, "italic"),
                     fg=COLOURS["text_secondary"], bg=COLOURS["bg_card"],
                     wraplength=330, justify="left").pack(anchor="w", padx=16, pady=(2,4))

        # STYLIST TIPS
        notes = outfit.get("occasion_notes", [])
        if notes:
            tk.Label(card, text="STYLIST TIPS", font=FONTS["small"],
                     fg=COLOURS["gold_dark"], bg=COLOURS["bg_card"]).pack(anchor="w", padx=12)
            for note in notes:
                tk.Label(card, text=f"  • {note}", font=FONTS["small"],
                         fg=COLOURS["text_primary"], bg=COLOURS["bg_card"],
                         wraplength=330, justify="left").pack(anchor="w", padx=16, pady=1)

        # Action buttons
        bf = tk.Frame(card, bg=COLOURS["bg_card"])
        bf.pack(fill="x", padx=12, pady=(6,10))

        sb_btn = tk.Button(bf, text="💾 Save This Look", font=FONTS["small"],
                           bg=COLOURS["gold_primary"], fg=COLOURS["bg_primary"],
                           relief="flat", padx=10, pady=5, cursor="hand2",
                           command=lambda r=rec, n=outfit_num: self._save_look(r, n))
        sb_btn.pack(side="left", padx=(0,6))
        sb_btn.bind("<Enter>", lambda e: sb_btn.config(bg=COLOURS["gold_dark"]))
        sb_btn.bind("<Leave>", lambda e: sb_btn.config(bg=COLOURS["gold_primary"]))

        ex_btn = tk.Button(bf, text="📊 Export CSV", font=FONTS["small"],
                           bg=COLOURS["bg_input"], fg=COLOURS["text_primary"],
                           relief="flat", padx=10, pady=5, cursor="hand2",
                           command=self._export_tableau)
        ex_btn.pack(side="left")

    # =========================================================
    # SAVE / EXPORT
    # =========================================================
    def _save_look(self, rec, num):
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
        out_dir  = os.path.join(PROJECT_ROOT, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "tableau_export.csv")
        try:
            rows = []
            for rec in self.outfit_results:
                outfit = rec.get("outfit", {})
                kit    = rec.get("jewellery_kit", {})
                items  = outfit.get("items", {})
                rows.append({
                    "outfit_number": outfit.get("outfit_number",""),
                    "palette_name":  outfit.get("palette_name",""),
                    "total_cost":    outfit.get("total_cost",""),
                    "budget_given":  outfit.get("budget_given",""),
                    "top":     (items.get("top") or {}).get("name","") or
                               (items.get("dress") or {}).get("name",""),
                    "bottom":      (items.get("bottom") or {}).get("name",""),
                    "outerwear":   (items.get("outerwear") or {}).get("name",""),
                    "footwear":    (items.get("footwear") or {}).get("name",""),
                    "bag":         (items.get("bag") or {}).get("name",""),
                    "earrings":    kit.get("earrings",""),
                    "necklace":    kit.get("necklace",""),
                    "fragrance":   kit.get("fragrance_note",""),
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
    # AI STYLIST CHAT
    # =========================================================
    def _send_chat(self):
        msg = self.chat_input.get().strip()
        if not msg:
            return
        self.chat_input.delete(0, "end")
        self._chat_append(f"You: {msg}\n", "user_msg")
        threading.Thread(target=self._ollama_thread, args=(msg,), daemon=True).start()

    def _ollama_thread(self, msg):
        def ap(text, tag="ai_msg"):
            self.root.after(0, lambda: self._chat_append(text, tag))
        if not OLLAMA_OK:
            ap("Style Agent: Install Ollama and run 'ollama pull llama3' to activate AI chat.\n")
            return
        try:
            import ollama
            ap("Style Agent: ", "ai_label")
            resp = ollama.chat(
                model="llama3",
                messages=[
                    {"role": "system",
                     "content": "You are Style Agent, a luxury fashion stylist specialising "
                                "in Indian fashion. Give concise, expert styling advice."},
                    {"role": "user", "content": msg},
                ])
            ap(resp["message"]["content"] + "\n\n")
        except Exception as e:
            ap(f"Chat error: {e}\n")

    def _chat_append(self, text, tag="ai_msg"):
        self.chat_display.config(state="normal")
        self.chat_display.insert("end", text, tag)
        self.chat_display.config(state="disabled")
        self.chat_display.see("end")

    # ── Entry point ───────────────────────────────────────────
    def run(self):
        self.root.mainloop()

