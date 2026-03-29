#!/usr/bin/env python3
"""
Advanced AI-powered astrological analysis module.
Includes pattern recognition, predictions, and personalized recommendations.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from ai_interpreter import AstrologicalInterpreter


class PatternAnalyzer:
    """Analyzes patterns in astrological data using AI."""
    
    def __init__(self, interpreter: AstrologicalInterpreter):
        """Initialize pattern analyzer with interpreter."""
        self.interpreter = interpreter
        self.chart_history: List[Dict] = []
    
    def add_chart(self, chart_data: Dict, date_context: Optional[str] = None) -> None:
        """
        Add a chart to the history for pattern analysis.
        
        Args:
            chart_data: Chart dictionary
            date_context: Optional context (event, milestone, etc.)
        """
        entry = {
            'chart': chart_data,
            'date': chart_data.get('datetime_utc'),
            'context': date_context,
            'analyzed_at': datetime.utcnow().isoformat()
        }
        self.chart_history.append(entry)
    
    def analyze_life_patterns(self) -> str:
        """
        Analyze patterns across multiple charts in history.
        
        Returns:
            AI-generated analysis of life patterns
        """
        if not self.interpreter.client:
            return "Pattern analysis requires AI API connection."
        
        if len(self.chart_history) < 2:
            return "Need at least 2 charts to analyze patterns."
        
        # Extract key data
        planets_evolution = self._extract_planet_evolution()
        aspect_patterns = self._extract_aspect_patterns()
        moon_phases = self._extract_moon_phases()
        
        prompt = f"""Analyze these astrological patterns across time:

PLANETARY EVOLUTION:
{planets_evolution}

ASPECT PATTERNS:
{aspect_patterns}

MOON PHASE SEQUENCE:
{moon_phases}

Identify:
1. Recurring themes and cycles
2. Personal growth patterns
3. Challenge periods and their outcomes
4. Alignment opportunities
5. Spiritual development arc

Provide insights on what these patterns reveal about life direction."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Pattern analysis error: {e}"
    
    def predict_future_themes(self, days_ahead: int = 90) -> str:
        """
        Use AI to predict themes for the coming period.
        
        Args:
            days_ahead: Number of days to predict ahead
            
        Returns:
            Predictive insights
        """
        if not self.interpreter.client:
            return "Predictions require AI API connection."
        
        if not self.chart_history:
            return "Need natal chart data for predictions."
        
        natal_chart = self.chart_history[0]['chart']
        
        prompt = f"""Based on this natal chart, predict the themes for the next {days_ahead} days:

NATAL PLANETS:
{self.interpreter._format_planets(natal_chart.get('planets', {}))}

NATAL ASPECTS:
{self.interpreter._format_aspects(natal_chart.get('aspects', []))}

Forecast:
1. Primary energy and focus
2. Opportunities to embrace
3. Challenges to navigate
4. Timing for important actions
5. Recommended practices and practices
6. Life areas most affected
7. Spiritual lessons emerging

Keep response practical and forward-looking."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Prediction error: {e}"
    
    def get_personalized_recommendations(self, life_context: Optional[str] = None) -> str:
        """
        Generate AI personalized recommendations based on natal chart.
        
        Args:
            life_context: Optional context about current life situation
            
        Returns:
            Personalized recommendations
        """
        if not self.interpreter.client:
            return "Recommendations require AI API connection."
        
        if not self.chart_history:
            return "Need natal chart data for recommendations."
        
        natal_chart = self.chart_history[0]['chart']
        
        context_text = f"Current life situation: {life_context}" if life_context else ""
        
        prompt = f"""Provide personalized recommendations based on this natal chart:

NATAL DATA:
{self.interpreter._format_planets(natal_chart.get('planets', {}))}

ASPECTS:
{self.interpreter._format_aspects(natal_chart.get('aspects', []))}

{context_text}

Recommend:
1. Career and professional path
2. Relationship dynamics to cultivate
3. Creative expression outlets
4. Spiritual practices suited to this chart
5. Physical activities and health approaches
6. Financial stewardship strategies
7. Personal development priorities
8. Life balance recommendations

Base all suggestions on natal chart signatures."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Recommendation error: {e}"
    
    def analyze_synchronicity(self, events: List[Dict], include_interpretations: bool = True) -> str:
        """
        Analyze synchronistic connections between events and astrological data.
        
        Args:
            events: List of events with dates and descriptions
            include_interpretations: Whether to include AI interpretations
            
        Returns:
            Synchronicity analysis
        """
        if not self.interpreter.client:
            return "Synchronicity analysis requires AI API connection."
        
        if not self.chart_history:
            return "Need natal chart data for synchronicity analysis."
        
        natal_chart = self.chart_history[0]['chart']
        events_text = self._format_events(events)
        
        prompt = f"""Analyze the synchronistic connections between these life events and astrological patterns:

NATAL CHART:
{self.interpreter._format_planets(natal_chart.get('planets', {}))}

LIFE EVENTS:
{events_text}

Examine:
1. Planetary transits during key events
2. Astrological timing patterns
3. Synchronistic meanings
4. Life lessons revealed by timing
5. Deeper purpose connections
6. Cycles and recurrence patterns

Provide insights on how astrology and life events align."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Synchronicity analysis error: {e}"
    
    def generate_yearly_forecast(self, year: int) -> str:
        """
        Generate comprehensive yearly astrological forecast.
        
        Args:
            year: Year to forecast
            
        Returns:
            Yearly forecast
        """
        if not self.interpreter.client:
            return "Yearly forecast requires AI API connection."
        
        if not self.chart_history:
            return "Need natal chart data for forecast."
        
        natal_chart = self.chart_history[0]['chart']
        
        prompt = f"""Create a comprehensive astrological forecast for {year}:

NATAL CHART FOUNDATION:
{self.interpreter._format_planets(natal_chart.get('planets', {}))}

Key Themes for {year}:
1. Major cycles completing or beginning
2. Monthly themes and focus areas
3. Key event windows and timing
4. Personal growth opportunities
5. Relationship dynamics emerging
6. Career and financial outlook
7. Health and wellness focus
8. Spiritual development trajectory
9. Recommended actions and practices
10. Challenges to prepare for

Organize by quarter for clarity."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Forecast error: {e}"
    
    def compare_charts_for_growth(self, chart1: Dict, chart2: Dict) -> str:
        """
        Compare two natal charts for growth and compatibility.
        
        Args:
            chart1: First natal chart
            chart2: Second natal chart
            
        Returns:
            Comparative analysis
        """
        if not self.interpreter.client:
            return "Comparative analysis requires AI API connection."
        
        prompt = f"""Compare these two natal charts for mutual growth and partnership potential:

PERSON A CHART:
{self.interpreter._format_planets(chart1.get('planets', {}))}
Aspects: {chart1.get('aspects', [])}

PERSON B CHART:
{self.interpreter._format_planets(chart2.get('planets', {}))}
Aspects: {chart2.get('aspects', [])}

Analyze:
1. Soul contract and karmic connection
2. Complementary strengths
3. Growth triggers for each person
4. Relationship purpose and lessons
5. Communication style compatibility
6. Sexual and emotional compatibility
7. Shared life direction
8. Challenge areas and how to work through them
9. Timeline of relationship evolution
10. Recommendation for partnership alignment

Focus on growth potential and evolution."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Comparative analysis error: {e}"
    
    @staticmethod
    def _extract_planet_evolution() -> str:
        """Extract planetary position evolution."""
        # Placeholder - would analyze planet positions across charts
        return "Planetary movements tracked across chart history"
    
    @staticmethod
    def _extract_aspect_patterns() -> str:
        """Extract recurring aspect patterns."""
        # Placeholder - would find recurring aspects
        return "Aspect patterns identified across time periods"
    
    @staticmethod
    def _extract_moon_phases() -> str:
        """Extract moon phase sequence."""
        # Placeholder - would track moon phase cycles
        return "Moon phase cycles across recorded dates"
    
    @staticmethod
    def _format_events(events: List[Dict]) -> str:
        """Format events for AI processing."""
        lines = []
        for event in events:
            date = event.get('date', 'Unknown')
            description = event.get('description', 'No description')
            intensity = event.get('intensity', 'Moderate')
            lines.append(f"- {date}: {description} (intensity: {intensity})")
        return "\n".join(lines) if lines else "No events provided"


class AstrologicalPredictors:
    """AI-powered predictive analysis."""
    
    def __init__(self, interpreter: AstrologicalInterpreter):
        """Initialize predictor."""
        self.interpreter = interpreter
    
    def predict_relationship_timing(self, natal_chart: Dict) -> str:
        """
        Predict optimal timing for relationship initiation.
        
        Args:
            natal_chart: Natal chart data
            
        Returns:
            Relationship timing forecast
        """
        if not self.interpreter.client:
            return "Predictions require AI API connection."
        
        prompt = f"""Based on this natal chart, predict timing for meaningful relationships:

CHART:
{self.interpreter._format_planets(natal_chart.get('planets', {}))}

Venus Sign Analysis: {self._get_venus_implications(natal_chart)}

Provide:
1. Natural attraction patterns
2. Optimal timing windows
3. Type of partner alignment
4. Relationship growth phases
5. When to expect major connections
6. How to magnetize partnerships
7. Internal alignment work needed

Focus on realistic timing and growth."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Prediction error: {e}"
    
    def predict_career_evolution(self, natal_chart: Dict) -> str:
        """
        Predict career path and timing.
        
        Args:
            natal_chart: Natal chart data
            
        Returns:
            Career evolution forecast
        """
        if not self.interpreter.client:
            return "Career predictions require AI API connection."
        
        prompt = f"""Predict career evolution based on this natal chart:

CHART DATA:
{self.interpreter._format_planets(natal_chart.get('planets', {}))}

Midheaven Analysis: {self._get_midheaven_implications(natal_chart)}

Forecast:
1. Natural career talents
2. Optimal career timing
3. Career transitions and timing
4. Leadership ability timing
5. Financial success windows
6. Entrepreneurship potential
7. Work-life balance needs
8. Success factors and strategies

Provide practical career guidance."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Career forecast error: {e}"
    
    @staticmethod
    def _get_venus_implications(chart: Dict) -> str:
        """Get Venus sign implications."""
        planets = chart.get('planets', {})
        if 'Venus' in planets:
            return f"Venus position: {planets['Venus'].get('zodiac_sign', 'Unknown')}"
        return "Venus not computed"
    
    @staticmethod
    def _get_midheaven_implications(chart: Dict) -> str:
        """Get Midheaven implications."""
        # Usually not in basic planets dict, would need house calculation
        return "Midheaven analysis data not available in this chart"


class RecommendationEngine:
    """AI-powered recommendation system."""
    
    def __init__(self, interpreter: AstrologicalInterpreter):
        """Initialize recommendation engine."""
        self.interpreter = interpreter
    
    def recommend_practices(self, natal_chart: Dict, focus_area: str) -> str:
        """
        Recommend spiritual/wellness practices based on chart.
        
        Args:
            natal_chart: Natal chart data
            focus_area: Area to focus recommendations (health, spirituality, career, etc.)
            
        Returns:
            Customized practice recommendations
        """
        if not self.interpreter.client:
            return "Recommendations require AI API connection."
        
        prompt = f"""Recommend {focus_area} practices for this natal chart:

CHART:
{self.interpreter._format_planets(natal_chart.get('planets', {}))}

ASPECTS:
{self.interpreter._format_aspects(natal_chart.get('aspects', []))}

Recommend specific:
1. Daily practices (meditation, movement, etc.)
2. Weekly rituals
3. Seasonal activities
4. Foods and supplements aligned with chart
5. Energy work compatible with natal configuration
6. Crystals and minerals
7. Timing for practices
8. Books and studies to explore
9. Community and support structures
10. Budget and resources needed

Make recommendations practical and accessible."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Recommendation error: {e}"
    
    def recommend_life_focus(self, natal_chart: Dict, current_age: Optional[int] = None) -> str:
        """
        Recommend life focus areas by age and personal development stage.
        
        Args:
            natal_chart: Natal chart data
            current_age: Optional current age
            
        Returns:
            Age-appropriate recommendations
        """
        if not self.interpreter.client:
            return "Recommendations require AI API connection."
        
        age_context = f"\nCurrent age: {current_age}" if current_age else ""
        
        prompt = f"""Recommend life focus areas for this natal chart development:{age_context}

CHART:
{self.interpreter._format_planets(natal_chart.get('planets', {}))}

Life Development Stages:
1. Foundation years (18-25): Identity and skills
2. Building years (25-35): Career and relationships
3. Mastery years (35-45): Contribution and leadership
4. Integration years (45-55): Wisdom and purpose
5. Culmination years (55+): Legacy and transcendence

Recommend:
1. Current priorities
2. Areas to develop
3. Skills to cultivate
4. Relationships to nurture
5. Creative expression outlets
6. Contribution opportunities
7. Spiritual exploration
8. Next natural milestone
9. How to align with soul purpose
10. Long-term vision alignment

Be age and stage appropriate."""
        
        try:
            return self.interpreter._query_ai(prompt)
        except Exception as e:
            return f"Recommendation error: {e}"
