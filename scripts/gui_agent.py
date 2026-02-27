"""
gui_agent.py — Premium CustomTkinter GUI
Gold/Deep Blue luxury theme with chat interface, Lookbook grid,
Color Palette Visualizer, and Feedback panel.
"""

from __future__ import annotations
import sys
import os
import threading
import math
import webbrowser
import urllib.request
import io
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

from state_schema import StyleState
from setup_db import initialize_database, DB_PATH, get_all_users, create_user
from trend_scout_agent import TrendScoutAgent
from customer_persona_agent import CustomerPersonaAgent
from wardrobe_architect_agent import WardrobeArchitectAgent
from feedback_loop import FeedbackHandler
from indian_fashion_kb import get_clarifying_questions, OCCASION_RULES
from color_engine import get_color_hex, COLOR_DB


# ═══════════════════════════════════════════════════════════════
#  THEME CONSTANTS — Gold / Deep Blue Luxury
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "bg_dark":          "#0B1529",      # Deep navy background
    "bg_card":          "#111D35",      # Card background
    "bg_input":         "#162240",      # Input field background
    "bg_chat_user":     "#1B3A6B",      # User message bubble
    "bg_chat_ai":       "#0F2847",      # AI message bubble
    "accent_gold":      "#D4AF37",      # Primary gold accent
    "accent_gold_dim":  "#A08520",      # Dimmed gold
    "accent_blue":      "#2B6CB0",      # Secondary blue accent
    "text_primary":     "#F0E6D3",      # Warm white text
    "text_secondary":   "#8899AA",      # Muted text
    "text_gold":        "#D4AF37",      # Gold text
    "border":           "#1E3050",      # Subtle border
    "success":          "#48BB78",      # Green for available
    "warning":          "#ECC94B",      # Yellow for limited
    "error":            "#FC8181",      # Red for out of stock
    "scrollbar":        "#2D4A7A",      # Scrollbar color
}

FONTS = {
    "heading":      ("Helvetica Neue", 22, "bold"),
    "subheading":   ("Helvetica Neue", 16, "bold"),
    "body":         ("Helvetica Neue", 13),
    "body_bold":    ("Helvetica Neue", 13, "bold"),
    "small":        ("Helvetica Neue", 11),
    "tiny":         ("Helvetica Neue", 10),
    "mono":         ("SF Mono", 12),
    "chat":         ("Helvetica Neue", 13),
    "chat_bold":    ("Helvetica Neue", 13, "bold"),
    "price":        ("Helvetica Neue", 15, "bold"),
    "emoji":        ("Apple Color Emoji", 14),
}

OCCASIONS = list(OCCASION_RULES.keys())
GENDERS = ["female", "male"]


class StyleApp(ctk.CTk):
    """Premium Personal Shopping Assistant — CustomTkinter GUI"""

    def __init__(self):
        super().__init__()

        # ── Window Setup ──
        self.title("✨ StyleDNA — Your Personal Indian Style Architect")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLORS["bg_dark"])

        # ── Backend ──
        self.app_state = StyleState()
        self.trend_scout = TrendScoutAgent()
        self.customer_persona = CustomerPersonaAgent()
        self.wardrobe_architect = WardrobeArchitectAgent()
        self.feedback_handler = FeedbackHandler()

        # Initialize DB and fetch users
        if not os.path.exists(DB_PATH):
            initialize_database()
        
        self.users = get_all_users()

        # ── Build UI ──
        self._build_layout()
        self._add_welcome_message()

    # ═══════════════════════════════════════════════════════════
    #  LAYOUT
    # ═══════════════════════════════════════════════════════════

    def _build_layout(self):
        """Build the 2-column layout: Chat + Lookbook."""
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content

        # ── HEADER BAR ──
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="✨ StyleDNA", font=FONTS["heading"],
            text_color=COLORS["accent_gold"]
        ).grid(row=0, column=0, padx=20, pady=15)

        ctk.CTkLabel(
            header, text="Your Personal Indian Style Architect",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).grid(row=0, column=1, padx=10, pady=15, sticky="w")

        # Dark/Light mode toggle
        self.mode_var = ctk.StringVar(value="dark")
        mode_switch = ctk.CTkSwitch(
            header, text="Light", variable=self.mode_var,
            onvalue="light", offvalue="dark",
            command=self._toggle_mode,
            fg_color=COLORS["accent_gold_dim"],
            progress_color=COLORS["accent_gold"],
            text_color=COLORS["text_secondary"],
        )
        mode_switch.grid(row=0, column=2, padx=20, pady=15)

        # ── LEFT PANEL: Chat Interface ──
        left_panel = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Controls bar
        self._build_controls(left_panel)

        # Chat area
        self.chat_frame = ctk.CTkScrollableFrame(
            left_panel, fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["scrollbar"],
            corner_radius=8,
        )
        self.chat_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 5))
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_msg_count = 0

        # Input area
        input_frame = ctk.CTkFrame(left_panel, fg_color=COLORS["bg_card"], corner_radius=12)
        input_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        input_frame.grid_columnconfigure(0, weight=1)

        self.user_input = ctk.CTkEntry(
            input_frame, placeholder_text="Tell me about the occasion, your style, or give feedback...",
            font=FONTS["chat"], fg_color=COLORS["bg_input"],
            border_color=COLORS["border"], text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_secondary"],
            height=45, corner_radius=10,
        )
        self.user_input.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.user_input.bind("<Return>", lambda e: self._on_send())

        send_btn = ctk.CTkButton(
            input_frame, text="Send", font=FONTS["body_bold"],
            fg_color=COLORS["accent_gold"], hover_color=COLORS["accent_gold_dim"],
            text_color=COLORS["bg_dark"], width=80, height=40, corner_radius=10,
            command=self._on_send,
        )
        send_btn.grid(row=0, column=1, padx=(0, 10), pady=10)

        # ── RIGHT PANEL: Lookbook / Results ──
        self.right_panel = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        # Lookbook scrollable area
        self.lookbook_frame = ctk.CTkScrollableFrame(
            self.right_panel, fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["scrollbar"],
            corner_radius=8,
        )
        self.lookbook_frame.grid(row=0, column=0, sticky="nsew")
        self.lookbook_frame.grid_columnconfigure(0, weight=1)

        self._show_lookbook_placeholder()

    def _build_controls(self, parent):
        """Build the controls bar with occasion, gender, budget, user selectors."""
        controls = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Row 1: Occasion + Gender
        row1 = ctk.CTkFrame(controls, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(row1, text="Occasion", font=FONTS["tiny"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self.occasion_var = ctk.StringVar(value="wedding")
        self.occasion_menu = ctk.CTkOptionMenu(
            row1, variable=self.occasion_var,
            values=[o.replace("_", " ").title() for o in OCCASIONS],
            font=FONTS["small"], fg_color=COLORS["bg_input"],
            button_color=COLORS["accent_gold_dim"],
            button_hover_color=COLORS["accent_gold"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            width=150, height=32,
        )
        self.occasion_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row1, text="Gender", font=FONTS["tiny"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self.gender_var = ctk.StringVar(value="female")
        ctk.CTkSegmentedButton(
            row1, values=["Female", "Male"],
            variable=self.gender_var,
            font=FONTS["small"],
            fg_color=COLORS["bg_input"],
            selected_color=COLORS["accent_gold"],
            selected_hover_color=COLORS["accent_gold_dim"],
            unselected_color=COLORS["bg_input"],
            unselected_hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            text_color_disabled=COLORS["text_secondary"],
            height=32,
            command=lambda v: self.gender_var.set(v.lower()),
        ).pack(side="left", padx=(0, 15))

        # Row 2: Budget + User + Run
        row2 = ctk.CTkFrame(controls, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(row2, text="Budget ₹", font=FONTS["tiny"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self.budget_var = ctk.StringVar(value="15000")
        budget_entry = ctk.CTkEntry(
            row2, textvariable=self.budget_var, width=90, height=32,
            font=FONTS["small"], fg_color=COLORS["bg_input"],
            border_color=COLORS["border"], text_color=COLORS["text_primary"],
        )
        budget_entry.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row2, text="User", font=FONTS["tiny"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        
        self.user_menu_values = [f"{u['user_id']} — {u['name']}" for u in self.users] if self.users else ["No Users"]
        self.user_var = ctk.StringVar(value=self.user_menu_values[0])
        
        self.user_menu = ctk.CTkOptionMenu(
            row2, variable=self.user_var,
            values=self.user_menu_values,
            font=FONTS["small"], fg_color=COLORS["bg_input"],
            button_color=COLORS["accent_gold_dim"],
            button_hover_color=COLORS["accent_gold"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            width=180, height=32,
        )
        self.user_menu.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            row2, text="+ New User", font=FONTS["tiny"],
            fg_color="transparent", hover_color=COLORS["bg_input"],
            text_color=COLORS["accent_gold"], border_width=1, border_color=COLORS["accent_gold"],
            width=70, height=32, corner_radius=6,
            command=self._open_user_creation,
        ).pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row2, text="Region", font=FONTS["tiny"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self.region_var = ctk.StringVar(value="")
        ctk.CTkEntry(
            row2, textvariable=self.region_var, width=90, height=32,
            font=FONTS["small"], fg_color=COLORS["bg_input"],
            border_color=COLORS["border"], text_color=COLORS["text_primary"],
            placeholder_text="e.g. Pune",
            placeholder_text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 15))

        # Row 3: Filters (Clothing, Accessory, Jewelry) + Run
        row3 = ctk.CTkFrame(controls, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(row3, text="Clothing", font=FONTS["tiny"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self.clothing_type_var = ctk.StringVar(value="Any")
        self.clothing_menu = ctk.CTkOptionMenu(
            row3, variable=self.clothing_type_var,
            values=["Any", "Lehenga", "Saree", "Kurta", "Anarkali", "Sherwani", "Dress", "Blazer", "Sharara", "Dhoti", "Suit"],
            font=FONTS["small"], fg_color=COLORS["bg_input"], button_color=COLORS["accent_gold_dim"], button_hover_color=COLORS["accent_gold"], width=110, height=32,
        )
        self.clothing_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row3, text="Accessory", font=FONTS["tiny"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self.accessory_type_var = ctk.StringVar(value="Any")
        self.accessory_menu = ctk.CTkOptionMenu(
            row3, variable=self.accessory_type_var,
            values=["Any", "Potli", "Clutch", "Dupatta", "Stole", "Brooch", "Tie", "Bag"],
            font=FONTS["small"], fg_color=COLORS["bg_input"], button_color=COLORS["accent_gold_dim"], button_hover_color=COLORS["accent_gold"], width=110, height=32,
        )
        self.accessory_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row3, text="Jewelry", font=FONTS["tiny"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self.jewelry_type_var = ctk.StringVar(value="Any")
        self.jewelry_menu = ctk.CTkOptionMenu(
            row3, variable=self.jewelry_type_var,
            values=["Any", "Necklace", "Earrings", "Bracelet", "Ring", "Watch", "Tikka", "Jhumka", "Choker"],
            font=FONTS["small"], fg_color=COLORS["bg_input"], button_color=COLORS["accent_gold_dim"], button_hover_color=COLORS["accent_gold"], width=110, height=32,
        )
        self.jewelry_menu.pack(side="left", padx=(0, 15))

        # Run button
        self.run_btn = ctk.CTkButton(
            row3, text="✨ Curate Look", font=FONTS["body_bold"],
            fg_color=COLORS["accent_gold"], hover_color=COLORS["accent_gold_dim"],
            text_color=COLORS["bg_dark"], width=130, height=32, corner_radius=8,
            command=self._on_curate,
        )
        self.run_btn.pack(side="right")

    def _open_user_creation(self):
        """Open a popup window to create a new user profile."""
        popup = ctk.CTkToplevel(self)
        popup.title("Create Style Profile")
        popup.geometry("450x550")
        popup.configure(fg_color=COLORS["bg_dark"])
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(
            popup, text="Create Style Profile", font=FONTS["subheading"], text_color=COLORS["accent_gold"]
        ).pack(pady=(20, 15))

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(fill="x", padx=30)

        # Name
        ctk.CTkLabel(form, text="Name", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        name_var = ctk.StringVar()
        ctk.CTkEntry(form, textvariable=name_var, height=35, fg_color=COLORS["bg_input"]).pack(fill="x", pady=(0, 10))

        # Skin Tone
        ctk.CTkLabel(form, text="Skin Tone", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        skin_var = ctk.StringVar(value="neutral")
        ctk.CTkSegmentedButton(
            form, values=["warm", "neutral", "cool"], variable=skin_var,
            selected_color=COLORS["accent_gold"], selected_hover_color=COLORS["accent_gold_dim"]
        ).pack(fill="x", pady=(0, 10))

        # Size
        ctk.CTkLabel(form, text="Size", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        size_var = ctk.StringVar(value="M")
        ctk.CTkOptionMenu(
            form, values=["XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"], variable=size_var,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent_gold"], button_hover_color=COLORS["accent_gold_dim"]
        ).pack(fill="x", pady=(0, 10))

        # Colors
        ctk.CTkLabel(form, text="Preferred Colors (comma separated)", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        colors_var = ctk.StringVar(value="Black, Navy Blue, Maroon")
        ctk.CTkEntry(form, textvariable=colors_var, height=35, fg_color=COLORS["bg_input"]).pack(fill="x", pady=(0, 10))

        # Fabrics
        ctk.CTkLabel(form, text="Preferred Fabrics (comma separated)", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        fabrics_var = ctk.StringVar(value="Cotton, Linen, Silk")
        ctk.CTkEntry(form, textvariable=fabrics_var, height=35, fg_color=COLORS["bg_input"]).pack(fill="x", pady=(0, 10))

        # DNA
        ctk.CTkLabel(form, text="Style DNA (e.g. Minimalist Professional)", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        dna_var = ctk.StringVar(value="Minimalist Professional")
        ctk.CTkEntry(form, textvariable=dna_var, height=35, fg_color=COLORS["bg_input"]).pack(fill="x", pady=(0, 20))

        def save_user():
            name = name_var.get().strip() or "Guest User"
            colors = [c.strip() for c in colors_var.get().split(",")]
            fabrics = [f.strip() for f in fabrics_var.get().split(",")]
            
            new_id = create_user(
                name=name,
                preferred_colors=colors,
                preferred_fabrics=fabrics,
                size=size_var.get(),
                skin_tone=skin_var.get(),
                budget_range="5000-25000",
                style_dna=dna_var.get(),
            )
            
            # Refresh user list
            self.users = get_all_users()
            self.user_menu_values = [f"{u['user_id']} — {u['name']}" for u in self.users]
            self.user_menu.configure(values=self.user_menu_values)
            self.user_var.set(f"{new_id} — {name}")
            
            self._add_chat_message(f"Profile created for {name}! ✨", sender="ai")
            popup.destroy()

        ctk.CTkButton(
            popup, text="Create Profile", font=FONTS["body_bold"],
            fg_color=COLORS["accent_gold"], hover_color=COLORS["accent_gold_dim"],
            text_color=COLORS["bg_dark"], height=40, command=save_user
        ).pack(fill="x", padx=30)


    # ═══════════════════════════════════════════════════════════
    #  CHAT INTERFACE
    # ═══════════════════════════════════════════════════════════

    def _add_chat_message(self, text: str, sender: str = "ai", tag: str = ""):
        """Add a message to the chat window."""
        is_user = sender == "user"
        bubble_color = COLORS["bg_chat_user"] if is_user else COLORS["bg_chat_ai"]
        text_color = COLORS["text_primary"]
        anchor = "e" if is_user else "w"
        padx_left = (80, 10) if is_user else (10, 80)
        icon = "👤" if is_user else "✨"

        msg_frame = ctk.CTkFrame(
            self.chat_frame, fg_color=bubble_color, corner_radius=14,
        )
        msg_frame.grid(
            row=self.chat_msg_count, column=0, sticky="ew",
            padx=padx_left, pady=4,
        )
        msg_frame.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(msg_frame, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(8, 0))

        sender_label = "You" if is_user else "StyleDNA"
        ctk.CTkLabel(
            header, text=f"{icon} {sender_label}",
            font=FONTS["chat_bold"],
            text_color=COLORS["accent_gold"] if not is_user else COLORS["text_primary"],
        ).pack(side="left")

        if tag:
            ctk.CTkLabel(
                header, text=tag, font=FONTS["tiny"],
                text_color=COLORS["text_secondary"],
            ).pack(side="right")

        # Message body
        msg_label = ctk.CTkLabel(
            msg_frame, text=text, font=FONTS["chat"],
            text_color=text_color, wraplength=450,
            justify="left", anchor="w",
        )
        msg_label.pack(fill="x", padx=12, pady=(4, 10))

        self.chat_msg_count += 1
        self.chat_frame.after(100, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))

    def _add_welcome_message(self):
        """Show welcome message."""
        self._add_chat_message(
            "Welcome to StyleDNA! 🎉\n\n"
            "I'm your personal Indian Style Architect. "
            "Tell me about the occasion — a Sangeet in Pune, Diwali dinner, "
            "or a corporate lunch — and I'll curate a premium look just for you.\n\n"
            "Select your occasion, gender, and budget above, then click "
            "'✨ Curate Look' to begin. Or type your request below!",
            sender="ai", tag="Welcome"
        )

    # ═══════════════════════════════════════════════════════════
    #  LOOKBOOK DISPLAY
    # ═══════════════════════════════════════════════════════════

    def _show_lookbook_placeholder(self):
        """Show placeholder in the lookbook area."""
        for widget in self.lookbook_frame.winfo_children():
            widget.destroy()

        placeholder = ctk.CTkFrame(self.lookbook_frame, fg_color=COLORS["bg_card"], corner_radius=16)
        placeholder.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(
            placeholder, text="👗", font=("Apple Color Emoji", 50),
        ).pack(pady=(30, 10))
        ctk.CTkLabel(
            placeholder, text="Your Curated Lookbook",
            font=FONTS["heading"], text_color=COLORS["accent_gold"],
        ).pack(pady=(0, 5))
        ctk.CTkLabel(
            placeholder, text="Curate a look to see your personalized outfit here",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(pady=(0, 30))

    def _display_lookbook(self, state: StyleState):
        """Display the curated outfit in the lookbook panel."""
        for widget in self.lookbook_frame.winfo_children():
            widget.destroy()

        rec = state.final_recommendation
        if not rec or not rec.outfit_items:
            self._show_lookbook_placeholder()
            return

        row_idx = 0

        # ── Header Card ──
        header_card = ctk.CTkFrame(self.lookbook_frame, fg_color=COLORS["bg_card"], corner_radius=16)
        header_card.grid(row=row_idx, column=0, sticky="ew", padx=10, pady=(10, 5))
        row_idx += 1

        ctk.CTkLabel(
            header_card, text="✨ YOUR CURATED LOOK",
            font=FONTS["heading"], text_color=COLORS["accent_gold"],
        ).pack(pady=(15, 5))

        occasion_text = rec.occasion.replace("_", " ").title()
        if rec.sub_occasion:
            occasion_text += f" — {rec.sub_occasion.replace('_', ' ').title()}"
        ctk.CTkLabel(
            header_card, text=occasion_text,
            font=FONTS["subheading"], text_color=COLORS["text_primary"],
        ).pack(pady=(0, 3))

        # Style DNA & Palette
        meta_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        meta_frame.pack(fill="x", padx=15, pady=(5, 15))

        if state.user_style_profile:
            ctk.CTkLabel(
                meta_frame, text=f"🧬 {state.user_style_profile.style_dna}",
                font=FONTS["body"], text_color=COLORS["text_secondary"],
            ).pack(side="left", padx=(0, 15))

        ctk.CTkLabel(
            meta_frame, text=f"🎨 {rec.palette_strategy.upper()}",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 15))

        score_color = COLORS["success"] if rec.trend_alignment_score >= 7 else COLORS["warning"]
        ctk.CTkLabel(
            meta_frame, text=f"📊 Trend: {rec.trend_alignment_score}/10",
            font=FONTS["body_bold"], text_color=score_color,
        ).pack(side="left")

        # ── Color Palette Visualizer ──
        if rec.color_palette:
            palette_card = ctk.CTkFrame(self.lookbook_frame, fg_color=COLORS["bg_card"], corner_radius=12)
            palette_card.grid(row=row_idx, column=0, sticky="ew", padx=10, pady=5)
            row_idx += 1

            ctk.CTkLabel(
                palette_card, text="COLOR PALETTE",
                font=FONTS["tiny"], text_color=COLORS["text_secondary"],
            ).pack(pady=(10, 5))

            palette_row = ctk.CTkFrame(palette_card, fg_color="transparent")
            palette_row.pack(pady=(0, 10))

            for hex_color in rec.color_palette[:5]:
                # Create color swatch
                swatch = ctk.CTkFrame(
                    palette_row, fg_color=hex_color, width=50, height=50,
                    corner_radius=8, border_width=2, border_color=COLORS["border"],
                )
                swatch.pack(side="left", padx=5)
                swatch.pack_propagate(False)

                # Find color name
                name = hex_color
                for cname, cinfo in COLOR_DB.items():
                    if cinfo["hex"].lower() == hex_color.lower():
                        name = cname
                        break
                ctk.CTkLabel(
                    palette_row, text=name, font=FONTS["tiny"],
                    text_color=COLORS["text_secondary"],
                ).pack(side="left", padx=(0, 10))

        # ── Outfit Items ──
        sections = {
            "🧥 THE FOUNDATION": [],
            "✨ THE ACCENTS": [],
            "👠 THE FINISHING TOUCHES": [],
        }

        for item in rec.outfit_items:
            if "Foundation" in item.role:
                sections["🧥 THE FOUNDATION"].append(item)
            elif "Accent" in item.role or "Jewelry" in item.role:
                sections["✨ THE ACCENTS"].append(item)
            else:
                sections["👠 THE FINISHING TOUCHES"].append(item)

        total_cost = 0

        for section_name, items in sections.items():
            if not items:
                continue

            section_card = ctk.CTkFrame(self.lookbook_frame, fg_color=COLORS["bg_card"], corner_radius=12)
            section_card.grid(row=row_idx, column=0, sticky="ew", padx=10, pady=5)
            row_idx += 1

            ctk.CTkLabel(
                section_card, text=section_name,
                font=FONTS["subheading"], text_color=COLORS["accent_gold"],
            ).pack(anchor="w", padx=15, pady=(12, 5))

            for item in items:
                total_cost += item.price
                item_frame = ctk.CTkFrame(section_card, fg_color=COLORS["bg_input"], corner_radius=10)
                item_frame.pack(fill="x", padx=12, pady=4)

                # Color swatch + info
                content = ctk.CTkFrame(item_frame, fg_color="transparent")
                content.pack(fill="x", padx=10, pady=8)

                # Product Image or Color swatch fallback
                image_loaded = False
                if item.image_url:
                    try:
                        req = urllib.request.Request(item.image_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=3) as response:
                            img_data = response.read()
                        pil_img = Image.open(io.BytesIO(img_data))
                        
                        # Calculate aspect ratio to fit within 60x80 while maintaining proportions
                        width, height = pil_img.size
                        ratio = min(60/width, 80/height)
                        new_size = (int(width*ratio), int(height*ratio))
                        
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=new_size)
                        img_label = ctk.CTkLabel(content, image=ctk_img, text="")
                        img_label.pack(side="left", padx=(0, 12))
                        image_loaded = True
                    except Exception as e:
                        print(f"Error loading image {item.image_url}: {e}")
                
                if not image_loaded:
                    swatch = ctk.CTkFrame(
                        content, fg_color=item.color_hex or "#808080",
                        width=50, height=50, corner_radius=6,
                    )
                    swatch.pack(side="left", padx=(0, 12))
                    swatch.pack_propagate(False)

                # Text info
                info = ctk.CTkFrame(content, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)

                ctk.CTkLabel(
                    info, text=item.name, font=FONTS["body_bold"],
                    text_color=COLORS["text_primary"], anchor="w",
                ).pack(anchor="w")

                detail_text = f"{item.brand}  •  {item.color}  •  {item.fabric}"
                ctk.CTkLabel(
                    info, text=detail_text, font=FONTS["small"],
                    text_color=COLORS["text_secondary"], anchor="w",
                ).pack(anchor="w")

                if "Accent Piece (Trending)" in item.role:
                    ctk.CTkLabel(
                        info, text="⭐ Trending Accent", font=FONTS["tiny"],
                        text_color=COLORS["accent_gold"], anchor="w",
                    ).pack(anchor="w")

                # Price + Shop link column
                right_col = ctk.CTkFrame(content, fg_color="transparent")
                right_col.pack(side="right", padx=(10, 0))

                ctk.CTkLabel(
                    right_col, text=f"₹{item.price:,.0f}", font=FONTS["price"],
                    text_color=COLORS["accent_gold"],
                ).pack(anchor="e")

                if item.product_url:
                    shop_btn = ctk.CTkButton(
                        right_col, text="Shop →", font=FONTS["tiny"],
                        fg_color=COLORS["accent_blue"], hover_color=COLORS["accent_gold"],
                        text_color="#FFFFFF",
                        width=65, height=22, corner_radius=6,
                        command=lambda url=item.product_url: webbrowser.open(url),
                    )
                    shop_btn.pack(anchor="e", pady=(4, 0))

            # Section padding
            ctk.CTkFrame(section_card, fg_color="transparent", height=5).pack()

        # ── Total ──
        total_card = ctk.CTkFrame(self.lookbook_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        total_card.grid(row=row_idx, column=0, sticky="ew", padx=10, pady=5)
        row_idx += 1

        total_row = ctk.CTkFrame(total_card, fg_color="transparent")
        total_row.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(
            total_row, text="TOTAL", font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        budget_ok = total_cost <= state.budget
        ctk.CTkLabel(
            total_row, text=f"₹{total_cost:,.0f}",
            font=("Helvetica Neue", 20, "bold"),
            text_color=COLORS["success"] if budget_ok else COLORS["error"],
        ).pack(side="right")

        # ── The Why ──
        why_card = ctk.CTkFrame(self.lookbook_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        why_card.grid(row=row_idx, column=0, sticky="ew", padx=10, pady=5)
        row_idx += 1

        ctk.CTkLabel(
            why_card, text="📝 THE STYLIST'S WHY",
            font=FONTS["subheading"], text_color=COLORS["accent_gold"],
        ).pack(anchor="w", padx=15, pady=(12, 5))

        ctk.CTkLabel(
            why_card, text=f"\"{rec.the_why}\"",
            font=FONTS["body"], text_color=COLORS["text_primary"],
            wraplength=500, justify="left", anchor="w",
        ).pack(fill="x", padx=15, pady=(0, 5))

        if rec.accessory_suite.get("stylist_tip"):
            ctk.CTkLabel(
                why_card, text=rec.accessory_suite["stylist_tip"],
                font=FONTS["small"], text_color=COLORS["text_secondary"],
                wraplength=500, justify="left", anchor="w",
            ).pack(fill="x", padx=15, pady=(5, 12))

        # ── Feedback Buttons ──
        feedback_card = ctk.CTkFrame(self.lookbook_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        feedback_card.grid(row=row_idx, column=0, sticky="ew", padx=10, pady=(5, 15))
        row_idx += 1

        ctk.CTkLabel(
            feedback_card, text="REFINE YOUR LOOK",
            font=FONTS["tiny"], text_color=COLORS["text_secondary"],
        ).pack(pady=(10, 5))

        btn_row = ctk.CTkFrame(feedback_card, fg_color="transparent")
        btn_row.pack(pady=(0, 12))

        feedback_options = [
            ("💚 Love it!", None),
            ("🪶 Lighter", "Too heavy, I want something lighter"),
            ("🎨 Bolder", "Make it bolder and more vibrant"),
            ("💰 Cheaper", "I need something more affordable"),
            ("🔄 Different", "Try something else entirely"),
        ]

        for label, feedback_text in feedback_options:
            btn = ctk.CTkButton(
                btn_row, text=label, font=FONTS["small"],
                fg_color=COLORS["bg_input"], hover_color=COLORS["accent_blue"],
                text_color=COLORS["text_primary"],
                width=95, height=32, corner_radius=8,
                command=lambda ft=feedback_text: self._on_feedback(ft) if ft else None,
            )
            btn.pack(side="left", padx=3)

    # ═══════════════════════════════════════════════════════════
    #  EVENT HANDLERS
    # ═══════════════════════════════════════════════════════════

    def _on_send(self):
        """Handle user text input."""
        text = self.user_input.get().strip()
        if not text:
            return

        self.user_input.delete(0, "end")
        self._add_chat_message(text, sender="user")

        # Check if this is feedback on existing outfit
        if self.app_state.final_recommendation:
            self._on_feedback(text)
        else:
            # Parse and curate
            self._add_chat_message(
                "Let me understand your request and curate the perfect look for you...",
                sender="ai", tag="Processing"
            )
            self._on_curate()

    def _on_curate(self):
        """Run the full pipeline in a background thread."""
        self._add_chat_message(
            "🔍 Researching trends...\n"
            "👤 Analyzing your style profile...\n"
            "👗 Curating your perfect look...\n\n"
            "This will take just a moment! ✨",
            sender="ai", tag="Curating"
        )

        self.run_btn.configure(state="disabled", text="Curating...")

        # Run pipeline in background thread
        thread = threading.Thread(target=self._run_pipeline_thread, daemon=True)
        thread.start()

    def _run_pipeline_thread(self):
        """Execute the pipeline in a background thread."""
        try:
            occasion_raw = self.occasion_var.get().lower().replace(" ", "_")
            gender = self.gender_var.get().lower()
            budget = float(self.budget_var.get() or 15000)
            user_id = int(self.user_var.get().split(" — ")[0])
            region = self.region_var.get().strip()

            # Initialize state
            self.app_state = StyleState(
                occasion=occasion_raw,
                gender=gender,
                budget=budget,
                region=region,
                preferred_clothing_type=self.clothing_type_var.get(),
                preferred_accessory_type=self.accessory_type_var.get(),
                preferred_jewelry_type=self.jewelry_type_var.get(),
            )

            # Run the three-agent pipeline
            self.app_state = self.trend_scout.run(self.app_state)
            self.app_state = self.customer_persona.run(self.app_state, user_id=user_id)
            self.app_state = self.wardrobe_architect.curate(self.app_state)

            # Update UI on main thread
            self.after(0, self._on_pipeline_complete)

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self._on_pipeline_error(err_msg))

    def _on_pipeline_complete(self):
        """Update UI after pipeline completes."""
        self.run_btn.configure(state="normal", text="✨ Curate Look")

        rec = self.app_state.final_recommendation
        if rec and rec.outfit_items:
            # Chat message with summary
            items_summary = "\n".join(
                f"  • {item.name} — ₹{item.price:,.0f}" for item in rec.outfit_items
            )
            total = sum(item.price for item in rec.outfit_items)

            self._add_chat_message(
                f"Here's your curated look! 🎉\n\n{items_summary}\n\n"
                f"💰 Total: ₹{total:,.0f}\n"
                f"📊 Trend Score: {rec.trend_alignment_score}/10\n\n"
                f"\"{rec.the_why}\"\n\n"
                f"Check the Lookbook panel for full details →\n"
                f"Use the buttons below to refine!",
                sender="ai", tag="Curated ✨"
            )

            # Display lookbook
            self._display_lookbook(self.app_state)

            # Ask clarifying questions if needed
            questions = get_clarifying_questions(
                self.app_state.occasion, self.app_state.gender
            )
            if questions and self.app_state.iteration == 0:
                q_text = "To refine further, you can also tell me:\n" + "\n".join(
                    f"  {i+1}. {q}" for i, q in enumerate(questions[:2])
                )
                self._add_chat_message(q_text, sender="ai", tag="Fine-tune")
        else:
            self._add_chat_message(
                "I couldn't find matching items for your criteria. "
                "Try adjusting the budget or occasion!",
                sender="ai", tag="No matches"
            )

    def _on_pipeline_error(self, error: str):
        """Handle pipeline errors."""
        self.run_btn.configure(state="normal", text="✨ Curate Look")
        self._add_chat_message(
            f"Something went wrong: {error}\nPlease try again.",
            sender="ai", tag="Error"
        )

    def _on_feedback(self, feedback_text: str):
        """Handle feedback and re-curate."""
        if not feedback_text:
            return

        self._add_chat_message(feedback_text, sender="user")
        self._add_chat_message(
            "Got it! Let me adjust the look based on your feedback... 🔄",
            sender="ai", tag="Refining"
        )

        self.run_btn.configure(state="disabled", text="Refining...")
        thread = threading.Thread(
            target=self._run_feedback_thread,
            args=(feedback_text,), daemon=True,
        )
        thread.start()

    def _run_feedback_thread(self, feedback_text: str):
        """Run feedback loop in background thread."""
        try:
            self.app_state, action = self.feedback_handler.process(feedback_text, self.app_state)
            self.app_state = self.wardrobe_architect.curate(self.app_state)
            self.after(0, self._on_pipeline_complete)
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self._on_pipeline_error(err_msg))

    def _toggle_mode(self):
        """Toggle dark/light mode."""
        mode = self.mode_var.get()
        ctk.set_appearance_mode(mode)

    # ═══════════════════════════════════════════════════════════
    #  DASHBOARD DATA (for Tableau Export)
    # ═══════════════════════════════════════════════════════════

    def get_dashboard_data(self) -> dict:
        """Export current state in dashboard format."""
        return self.app_state.to_dashboard_format()


def launch_gui():
    """Entry point for the GUI."""
    app = StyleApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
