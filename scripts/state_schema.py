"""
StyleState — Global State Schema for the Multi-Agent Style Orchestrator.
Persists throughout the entire workflow and is handed off between agents.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TrendBrief(BaseModel):
    """Output from the Trend Scout Agent."""
    trending_colors: list[str] = Field(default_factory=list, description="e.g. ['Cobalt Blue', 'Peach Fuzz', 'Emerald Green']")
    key_fabrics: list[str] = Field(default_factory=list, description="e.g. ['Silk', 'Chanderi', 'Organza']")
    must_have_silhouette: list[str] = Field(default_factory=list, description="e.g. ['A-Line', 'Straight Cut', 'Draped']")
    season: str = ""
    year: int = 2026
    source_summary: str = ""


class UserStyleProfile(BaseModel):
    """Output from the Customer Persona Agent."""
    user_id: int = 0
    dominant_colors: list[str] = Field(default_factory=list)
    dominant_colors_pct: dict[str, float] = Field(default_factory=dict)
    preferred_silhouettes: list[str] = Field(default_factory=list)
    preferred_fabrics: list[str] = Field(default_factory=list)
    style_dna: str = ""  # e.g. "Minimalist Professional", "Bold Traditionalist"
    size: str = ""
    skin_tone: str = ""  # warm / cool / neutral
    primary_colors: list[str] = Field(default_factory=list)
    budget_range: tuple[float, float] = (0, 50000)


class OutfitItem(BaseModel):
    """A single item in the curated outfit."""
    sku: str = ""
    name: str = ""
    category: str = ""  # Top / Bottom / Accessory / Footwear / Jewelry / Layer
    brand: str = ""
    price: float = 0.0
    color: str = ""
    color_hex: str = ""
    fabric: str = ""
    image_url: str = ""
    product_url: str = ""  # Live clickable link to the product page
    style_match_pct: float = 0.0
    role: str = ""  # "Main Piece" / "Accent Piece" / "Foundation" / etc.
    cut: str = ""
    fit: str = ""
    silhouette: str = ""
    vibe: str = ""


class FinalRecommendation(BaseModel):
    """The curated outfit + justification from the Wardrobe Architect."""
    outfit_items: list[OutfitItem] = Field(default_factory=list)
    the_why: str = ""  # 2-sentence justification
    trend_alignment_score: float = 0.0  # 1-10
    confidence_score: float = 0.0  # 0-100 indicating match to specified vibe
    inventory_availability_status: str = "available"  # available / limited / out_of_stock
    palette_strategy: str = ""  # complementary / analogous / monochromatic
    color_palette: list[str] = Field(default_factory=list)  # hex codes
    accessory_suite: dict[str, str] = Field(default_factory=dict)
    occasion: str = ""
    sub_occasion: str = ""


class StyleState(BaseModel):
    """
    Global state that persists throughout the multi-agent workflow.
    Handed off between Trend Scout → Customer Persona → Wardrobe Architect.
    """
    # --- Core pipeline data ---
    trend_brief: Optional[TrendBrief] = None
    user_style_profile: Optional[UserStyleProfile] = None
    inventory_match: list[dict] = Field(default_factory=list)
    final_recommendation: Optional[FinalRecommendation] = None

    # --- User input context ---
    occasion: str = ""
    sub_occasion: str = ""  # e.g. "Day Phera" vs "Evening Reception"
    budget: float = 15000.0
    gender: str = ""  # male / female / unisex
    region: str = ""  # e.g. "Pune", "Delhi", "Chennai"
    user_query: str = ""  # raw user input

    # --- Pipeline metadata ---
    preferred_clothing_type: str = "Any"
    preferred_accessory_type: str = "Any"
    preferred_jewelry_type: str = "Any"
    color_mood: str = "Neutral"  # Vibrant / Pastel / Earthy / Neutral
    preferred_vibe: str = "Any"
    current_step: str = "idle"  # idle / trend_scout / customer_persona / wardrobe_architect / complete
    feedback_history: list[str] = Field(default_factory=list)
    rejected_skus: list[str] = Field(default_factory=list)
    iteration: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    def reset_for_refinement(self):
        """Reset state for a feedback-driven re-curation, keeping user profile and trends."""
        self.inventory_match = []
        self.final_recommendation = None
        self.current_step = "wardrobe_architect"
        self.iteration += 1

    def full_reset(self):
        """Full state reset for a brand-new query."""
        self.trend_brief = None
        self.user_style_profile = None
        self.inventory_match = []
        self.final_recommendation = None
        self.current_step = "idle"
        self.feedback_history = []
        self.rejected_skus = []
        self.iteration = 0
        self.timestamp = datetime.now().isoformat()

    def to_dashboard_format(self) -> dict:
        """Export state for Tableau-style dashboard display."""
        rec = self.final_recommendation
        return {
            "occasion": self.occasion,
            "sub_occasion": self.sub_occasion,
            "budget": self.budget,
            "gender": self.gender,
            "region": self.region,
            "style_dna": self.user_style_profile.style_dna if self.user_style_profile else "",
            "trend_alignment_score": rec.trend_alignment_score if rec else 0,
            "availability": rec.inventory_availability_status if rec else "",
            "palette": rec.palette_strategy if rec else "",
            "outfit_count": len(rec.outfit_items) if rec else 0,
            "iteration": self.iteration,
            "the_why": rec.the_why if rec else "",
        }
