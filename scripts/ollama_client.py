"""
ollama_client.py — Ollama LLM Integration with Graceful Fallback
Wraps HTTP calls to local Ollama server for premium justification generation
and trend reasoning. Falls back to template-based responses if unavailable.
"""

from __future__ import annotations
import json
import requests
from typing import Optional


OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"  # or "deepseek-r1"


class OllamaClient:
    """
    Client for the Ollama local LLM server.
    Provides fashion-context reasoning and justification generation.
    """

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = DEFAULT_MODEL):
        self.base_url = base_url
        self.model = model
        self._available = None

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        if self._available is not None:
            return self._available
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            self._available = resp.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            self._available = False
        return self._available

    def _generate(self, prompt: str, system: str = "") -> Optional[str]:
        """Send a generation request to Ollama."""
        if not self.is_available():
            return None
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 300},
            }
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except (requests.ConnectionError, requests.Timeout, json.JSONDecodeError):
            pass
        return None

    def generate_justification(
        self,
        outfit_items: list[dict],
        occasion: str,
        style_dna: str,
        trending_colors: list[str],
        skin_tone: str = "",
    ) -> str:
        """
        Generate a premium 'The Why' justification for the curated outfit.
        Falls back to template-based response if Ollama is unavailable.
        """
        system_prompt = (
            "You are a Senior Indian Fashion Consultant at a luxury boutique. "
            "Write in a warm, expert voice — like a personal stylist speaking to a valued client. "
            "Be specific about fabrics, colors, and cultural significance. "
            "Keep your response to exactly 2-3 sentences. Do not use bullet points."
        )

        items_desc = ", ".join(
            f"{item.get('name', 'item')} ({item.get('color', '')}, {item.get('fabric', '')})"
            for item in outfit_items
        )

        prompt = (
            f"Write a 2-sentence justification for this curated outfit:\n"
            f"Items: {items_desc}\n"
            f"Occasion: {occasion}\n"
            f"Client's Style DNA: {style_dna}\n"
            f"Trending colors this season: {', '.join(trending_colors)}\n"
            f"Client's skin tone: {skin_tone}\n\n"
            f"Explain WHY these specific pieces work together and why they're perfect for this client."
        )

        llm_response = self._generate(prompt, system_prompt)
        if llm_response and len(llm_response) > 20:
            return llm_response.strip()

        # ── Fallback: Template-based justification ──
        return self._template_justification(outfit_items, occasion, style_dna, trending_colors)

    def reason_about_trends(
        self,
        raw_trend_data: dict,
        occasion: str,
        user_preferences: dict = None,
    ) -> str:
        """
        Use LLM to reason about how trends apply to a specific occasion.
        Falls back to a curated summary.
        """
        system_prompt = (
            "You are a fashion trend analyst specializing in Indian fashion. "
            "Analyze these trends and explain how they apply to the given occasion. "
            "Be specific about Indian fabrics and cultural context. "
            "Keep response to 3-4 sentences."
        )

        prompt = (
            f"Trending colors: {raw_trend_data.get('trending_colors', [])}\n"
            f"Key fabrics: {raw_trend_data.get('key_fabrics', [])}\n"
            f"Must-have silhouettes: {raw_trend_data.get('must_have_silhouette', [])}\n"
            f"Occasion: {occasion}\n"
            f"User preferences: {user_preferences or 'Not specified'}\n\n"
            f"How should these trends be adapted for this occasion in the Indian context?"
        )

        llm_response = self._generate(prompt, system_prompt)
        if llm_response and len(llm_response) > 20:
            return llm_response.strip()

        # Fallback
        colors = ", ".join(raw_trend_data.get("trending_colors", ["Cobalt Blue"])[:3])
        fabrics = ", ".join(raw_trend_data.get("key_fabrics", ["Silk"])[:2])
        return (
            f"This season's palette of {colors} pairs beautifully with {occasion} styling. "
            f"The trending fabrics — {fabrics} — offer the perfect balance of tradition "
            f"and contemporary appeal for the Indian occasion."
        )

    def _template_justification(
        self,
        outfit_items: list[dict],
        occasion: str,
        style_dna: str,
        trending_colors: list[str],
    ) -> str:
        """Fallback template-based justification when Ollama is unavailable."""
        main_piece = next((i for i in outfit_items if i.get("category") in ("Full", "Top")), {})
        accent_piece = next((i for i in outfit_items if i.get("category") in ("Accessory", "Jewelry", "Layer")), {})

        main_name = main_piece.get("name", "this ensemble")
        main_color = main_piece.get("color", "")
        main_fabric = main_piece.get("fabric", "")
        accent_name = accent_piece.get("name", "the accessories")
        accent_color = accent_piece.get("color", "")

        occasion_display = occasion.replace("_", " ").title()

        if style_dna and main_color and accent_color:
            return (
                f"We've curated this {main_name} in {main_fabric} as your foundation piece "
                f"— its {main_color} tone perfectly bridges your '{style_dna}' aesthetic with "
                f"this season's trending palette. {accent_name} in {accent_color} adds the ideal "
                f"finishing touch for your {occasion_display}, creating an elevated yet authentically you look."
            )
        elif main_name:
            return (
                f"This {main_name} embodies the {occasion_display} spirit with its "
                f"premium {main_fabric} construction. Paired with {accent_name}, "
                f"it delivers a curated look that's both on-trend and timeless."
            )
        else:
            trending = ", ".join(trending_colors[:2]) if trending_colors else "this season's palette"
            return (
                f"This curated ensemble draws from {trending} to create a harmonious "
                f"look that honors your {style_dna or 'personal'} style while embracing "
                f"the latest in Indian fashion for {occasion_display}."
            )


# Module-level instance for convenience
_client = None

def get_client(model: str = DEFAULT_MODEL) -> OllamaClient:
    """Get or create the singleton Ollama client."""
    global _client
    if _client is None or _client.model != model:
        _client = OllamaClient(model=model)
    return _client
