#!/usr/bin/env python3
"""
AI-powered astrological interpretation module.
Integrates LLM capabilities for intelligent chart analysis and insights.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

@dataclass
class InterpretationCache:
    """Cache for storing interpretations."""
    cache: Dict[str, str] = None
    
    def __post_init__(self):
        if self.cache is None:
            self.cache = {}
    
    def get_hash(self, key: str) -> str:
        """Generate hash key for caching."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def set(self, key: str, value: str) -> None:
        """Store interpretation in cache."""
        hash_key = self.get_hash(key)
        self.cache[hash_key] = value
    
    def get(self, key: str) -> Optional[str]:
        """Retrieve interpretation from cache."""
        hash_key = self.get_hash(key)
        return self.cache.get(hash_key)


class AstrologicalInterpreter:
    """AI-powered interpreter for astrological data."""
    
    def __init__(self, api_provider: str = "openai", api_key: Optional[str] = None):
        """
        Initialize the interpreter.
        
        Args:
            api_provider: 'openai' or 'anthropic'
            api_key: API key (if None, reads from environment)
        """
        self.api_provider = api_provider
        self.cache = InterpretationCache()
        
        # Try to load API key from environment
        if api_key is None:
            if api_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif api_provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
        
        self.api_key = api_key
        self.client = None
        
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the API client."""
        try:
            if self.api_provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            elif self.api_provider == "anthropic":
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
        except ImportError as e:
            logger.warning(f"Could not import {self.api_provider} client: {type(e).__name__}")
            self.client = None
    
    def interpret_aspects(self, aspects: List[Dict]) -> str:
        """
        Generate AI interpretation of planetary aspects.
        
        Args:
            aspects: List of aspect dictionaries
            
        Returns:
            Human-readable interpretation
        """
        if not aspects:
            return "No major aspects found in this chart."
        
        # Create cache key
        cache_key = json.dumps(aspects, sort_keys=True)
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Format aspects for AI
        aspect_text = self._format_aspects(aspects)
        
        # If no API available, return template interpretation
        if not self.client:
            return self._template_interpretation(aspects)
        
        prompt = f"""Analyze these astrological aspects and provide a meaningful interpretation:

{aspect_text}

Provide insights on:
1. Personal challenges and growth opportunities
2. Relationship dynamics
3. Creative and professional potential
4. Spiritual development
5. Timing for action

Keep the interpretation balanced, thoughtful, and constructive."""
        
        try:
            interpretation = self._query_ai(prompt)
            self.cache.set(cache_key, interpretation)
            return interpretation
        except Exception as e:
            logger.warning(f"AI interpretation failed: {type(e).__name__}")
            return self._template_interpretation(aspects)
    
    def interpret_moon_phase(self, phase: float) -> str:
        """
        Interpret the moon phase.
        
        Args:
            phase: Moon phase 0-1 (0=new, 0.5=full)
            
        Returns:
            Interpretation text
        """
        cache_key = f"moon_phase_{phase:.2f}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        phase_name = self._get_moon_phase_name(phase)
        
        if not self.client:
            return self._template_moon_interpretation(phase_name)
        
        prompt = f"""The moon is in the {phase_name} phase (phase value: {phase:.2f}).
        
Provide a brief interpretation of what this moon phase means for:
1. Emotional cycles
2. Manifestation energy
3. Recommended activities
4. Introspection opportunities

Keep it concise and practical."""
        
        try:
            interpretation = self._query_ai(prompt)
            self.cache.set(cache_key, interpretation)
            return interpretation
        except Exception as e:
            logger.warning(f"AI moon interpretation failed: {type(e).__name__}")
            return self._template_moon_interpretation(phase_name)
    
    def generate_chart_summary(self, chart_data: Dict) -> str:
        """
        Generate comprehensive AI summary of astrological chart.
        
        Args:
            chart_data: Complete chart dictionary
            
        Returns:
            Chart summary
        """
        if not self.client:
            return self._template_chart_summary(chart_data)
        
        planets_text = self._format_planets(chart_data.get('planets', {}))
        aspects_text = self._format_aspects(chart_data.get('aspects', []))
        
        prompt = f"""Create a comprehensive astrological chart reading based on:

PLANETS AND SIGNS:
{planets_text}

ASPECTS:
{aspects_text}

Moon Phase: {chart_data.get('moon_phase', 0):.2f}

Provide a holistic reading covering:
1. Core personality traits
2. Life purpose and direction
3. Relationship patterns
4. Career and creativity
5. Spiritual journey
6. Current life season and opportunities
7. Recommendations for alignment

Format as a readable, flowing narrative."""
        
        try:
            summary = self._query_ai(prompt)
            return summary
        except Exception as e:
            logger.warning(f"AI chart summary failed: {type(e).__name__}")
            return self._template_chart_summary(chart_data)
    
    def analyze_compatibility(self, chart1: Dict, chart2: Dict) -> str:
        """
        Analyze astrological compatibility between two charts.
        
        Args:
            chart1: First chart dictionary
            chart2: Second chart dictionary
            
        Returns:
            Compatibility analysis
        """
        if not self.client:
            return "AI compatibility analysis requires API connection."
        
        planets1 = self._format_planets(chart1.get('planets', {}))
        planets2 = self._format_planets(chart2.get('planets', {}))
        
        prompt = f"""Analyze the astrological compatibility between two people:

PERSON 1 PLANETS:
{planets1}

PERSON 2 PLANETS:
{planets2}

Evaluate:
1. Emotional compatibility (Moon compatibility)
2. Communication style (Mercury compatibility)
3. Love and passion (Venus/Mars compatibility)
4. Shared values and growth (Jupiter/Saturn compatibility)
5. Overall relationship potential
6. Challenges to work through
7. Strengths of the partnership

Provide a balanced, constructive analysis."""
        
        try:
            analysis = self._query_ai(prompt)
            return analysis
        except Exception as e:
            logger.warning(f"AI compatibility analysis failed: {type(e).__name__}")
            return "Compatibility analysis unavailable."
    
    def answer_question(self, question: str, chart_data: Optional[Dict] = None) -> str:
        """
        Answer an astrological question using AI and optional chart context.
        
        Args:
            question: User question about astrology or chart
            chart_data: Optional chart data for context
            
        Returns:
            Answer
        """
        if not self.client:
            return "AI Q&A requires API connection."
        
        context = ""
        if chart_data:
            planets_text = self._format_planets(chart_data.get('planets', {}))
            context = f"\nChart Context:\n{planets_text}"
        
        prompt = f"""Answer this astrological question thoughtfully and accurately:{context}

Question: {question}

Provide a clear, helpful response grounded in astrological knowledge."""
        
        try:
            answer = self._query_ai(prompt)
            return answer
        except Exception as e:
            logger.warning(f"AI question answering failed: {type(e).__name__}")
            return "Unable to process question."
    
    def _query_ai(self, prompt: str) -> str:
        """Query the AI service."""
        if not self.client:
            raise RuntimeError("AI client not initialized")
        
        if self.api_provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert astrologer with deep knowledge of natal charts, aspects, and astrological interpretation. Provide insightful, balanced, and constructive guidance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content.strip()
        
        elif self.api_provider == "anthropic":
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                system="You are an expert astrologer with deep knowledge of natal charts, aspects, and astrological interpretation. Provide insightful, balanced, and constructive guidance.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
        
        else:
            raise ValueError(f"Unknown API provider: {self.api_provider}")
    
    @staticmethod
    def _format_aspects(aspects: List[Dict]) -> str:
        """Format aspects for AI processing."""
        if not aspects:
            return "No major aspects."
        
        lines = []
        for aspect in aspects:
            line = f"- {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (orb: {aspect['orb']}°)"
            lines.append(line)
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_planets(planets: Dict) -> str:
        """Format planets data for AI processing."""
        lines = []
        for name, pos in planets.items():
            if isinstance(pos, dict):
                lon = pos.get('longitude', 0)
                sign = AstrologicalInterpreter._get_zodiac_sign(lon)
                line = f"- {name}: {lon:.2f}° ({sign})"
            lines.append(line)
        
        return "\n".join(lines) if lines else "No planetary data."
    
    @staticmethod
    def _get_zodiac_sign(longitude: float) -> str:
        """Get zodiac sign from longitude."""
        signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        sign_index = int(longitude / 30) % 12
        return signs[sign_index]
    
    @staticmethod
    def _get_moon_phase_name(phase: float) -> str:
        """Get moon phase name."""
        if phase < 0.125:
            return "New Moon"
        elif phase < 0.25:
            return "Waxing Crescent"
        elif phase < 0.375:
            return "First Quarter"
        elif phase < 0.5:
            return "Waxing Gibbous"
        elif phase < 0.625:
            return "Full Moon"
        elif phase < 0.75:
            return "Waning Gibbous"
        elif phase < 0.875:
            return "Last Quarter"
        else:
            return "Waning Crescent"
    
    @staticmethod
    def _template_interpretation(aspects: List[Dict]) -> str:
        """Template interpretation when AI is unavailable."""
        if not aspects:
            return "No major aspects found in this chart."
        
        lines = ["Aspect Interpretation (Template Mode):\n"]
        
        for aspect in aspects:
            p1 = aspect['planet1']
            p2 = aspect['planet2']
            a = aspect['aspect']
            
            if a == "Conjunction":
                interpretation = f"{p1} and {p2} unite their energies, creating intensity and focus."
            elif a == "Sextile":
                interpretation = f"{p1} and {p2} support each other harmoniously."
            elif a == "Square":
                interpretation = f"{p1} and {p2} create tension that drives growth."
            elif a == "Trine":
                interpretation = f"{p1} and {p2} flow together naturally and effortlessly."
            elif a == "Opposition":
                interpretation = f"{p1} and {p2} challenge each other, seeking balance."
            else:
                interpretation = f"{p1} and {p2} interact in complex ways."
            
            lines.append(f"• {interpretation}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _template_moon_interpretation(phase_name: str) -> str:
        """Template moon interpretation when AI is unavailable."""
        interpretations = {
            "New Moon": "A time for new beginnings, setting intentions, and inner reflection.",
            "Waxing Crescent": "Building momentum toward your goals; plant seeds and nurture projects.",
            "First Quarter": "Challenges arise to test your commitment; push through obstacles.",
            "Waxing Gibbous": "Refine your efforts; the finish line approaches.",
            "Full Moon": "Peak energy and illumination; culmination and revelations.",
            "Waning Gibbous": "Share your gifts; gratitude and release what no longer serves.",
            "Last Quarter": "Take time for reflection and prepare for the new cycle.",
            "Waning Crescent": "Rest and renew; trust the darkness before rebirth."
        }
        return interpretations.get(phase_name, "Moon phase energy present.")
    
    @staticmethod
    def _template_chart_summary(chart_data: Dict) -> str:
        """Template chart summary when AI is unavailable."""
        return """
Astrological Chart Summary (Template Mode):

This chart reveals the complex interplay of cosmic energies at work in your life.
The positions of planets in signs, houses, and their relationships (aspects) 
create a unique blueprint of your personality, potential, and life path.

Key Themes:
- Understand your core drives and motivations
- Recognize your strengths and growth opportunities
- Align with your natural rhythms and cycles
- Navigate challenges with clarity and wisdom
- Express your unique gifts in the world

For deeper insights, enable AI interpretation with an API key.
"""
