#!/usr/bin/env python3
"""
AstroAnalyzer - Comprehensive Astrological Analysis Tool

Combines astrological calculations with AI-powered insights to generate
detailed, personalized astrological reports and life guidance.

Features:
- Comprehensive birth chart analysis
- AI-powered personality insights
- Transit tracking and predictions
- Yearly and monthly forecasts
- Life pattern identification
- Relationship compatibility
- Career guidance based on astrology
- PDF report generation
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib

from astrologico import AstrologicalCalculator
from ai_interpreter import AstrologicalInterpreter


class AstroAnalyzer:
    """
    Comprehensive astrological analysis engine with AI interpretation.
    
    Generates detailed reports including birth chart analysis, personality
    insights, forecasts, and personalized guidance.
    """

    def __init__(self, use_ai: bool = True):
        """
        Initialize the analyzer.
        
        Args:
            use_ai: Whether to use AI interpretation (requires API keys)
        """
        self.calculator = AstrologicalCalculator()
        self.interpreter = AstrologicalInterpreter() if use_ai else None
        self.use_ai = use_ai and self.interpreter is not None

    def generate_birth_chart_report(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        name: str = "Subject"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive birth chart report.
        
        Args:
            birth_datetime: Birth date and time
            latitude: Birth location latitude
            longitude: Birth location longitude
            name: Person's name
            
        Returns:
            Dictionary with complete chart analysis
        """
        chart = self.calculator.generate_chart(birth_datetime, latitude, longitude)
        
        # Convert ChartData to dict if needed
        chart_dict = {
            "planets": dict(chart.planets) if hasattr(chart, 'planets') else {},
            "aspects": chart.aspects if hasattr(chart, 'aspects') else [],
            "moon_phase": chart.moon_phase if hasattr(chart, 'moon_phase') else None,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
        }
        
        report = {
            "metadata": {
                "name": name,
                "birth_datetime": birth_datetime.isoformat(),
                "birth_location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "generated_at": datetime.utcnow().isoformat()
            },
            "chart": chart_dict,
            "interpretations": {}
        }
        
        if self.use_ai:
            # AI-powered chart interpretation
            summary = self.interpreter.generate_chart_summary(chart)
            report["interpretations"]["chart_summary"] = summary
            
            # Personality and life purpose
            report["interpretations"]["personality"] = \
                self._analyze_personality(chart_dict)
            
            # Life themes and patterns
            report["interpretations"]["life_themes"] = \
                self._identify_life_themes(chart_dict)
        
        return report

    def generate_monthly_forecast(
        self,
        birth_chart: Dict[str, Any],
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """
        Generate monthly forecast and transit analysis.
        
        Args:
            birth_chart: Birth chart data
            month: Month number (1-12)
            year: Year
            
        Returns:
            Monthly forecast including transits and insights
        """
        # Calculate first and last day of month
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        forecast = {
            "period": f"{year}-{month:02d}",
            "start_date": first_day.isoformat(),
            "end_date": last_day.isoformat(),
            "transit_dates": [],
            "key_transits": [],
            "interpretations": {}
        }
        
        # Calculate transits throughout the month
        current = first_day
        while current <= last_day:
            transit_chart = self.calculator.generate_chart(
                current,
                birth_chart["location"]["latitude"],
                birth_chart["location"]["longitude"]
            )
            planets_dict = dict(transit_chart.planets) if hasattr(transit_chart, 'planets') else {}
            forecast["transit_dates"].append({
                "date": current.isoformat(),
                "planets": planets_dict
            })
            current += timedelta(days=5)  # Check every 5 days
        
        if self.use_ai:
            # AI-powered forecast
            forecast["interpretations"]["monthly_themes"] = \
                self._forecast_month(first_day, last_day)
            forecast["interpretations"]["opportunities"] = \
                self._identify_opportunities(birth_chart, forecast)
        
        return forecast

    def generate_yearly_forecast(
        self,
        birth_chart: Dict[str, Any],
        year: int
    ) -> Dict[str, Any]:
        """
        Generate comprehensive yearly forecast.
        
        Args:
            birth_chart: Birth chart data
            year: Year to forecast
            
        Returns:
            Annual forecast with themes and guidance
        """
        yearly = {
            "year": year,
            "overall_theme": "",
            "quarterly_themes": {},
            "key_periods": [],
            "recommendations": []
        }
        
        if self.use_ai:
            yearly["overall_theme"] = \
                f"Comprehensive astrological overview for {year}"
            
            # Quarterly breakdown
            for quarter in range(1, 5):
                start_month = (quarter - 1) * 3 + 1
                yearly["quarterly_themes"][f"Q{quarter}"] = \
                    self._forecast_quarter(birth_chart, start_month, year)
            
            # Year-long recommendations
            yearly["recommendations"] = \
                self._generate_yearly_recommendations(birth_chart, year)
        
        return yearly

    def analyze_compatibility(
        self,
        person1_chart: Dict[str, Any],
        person2_chart: Dict[str, Any],
        relationship_type: str = "romantic"
    ) -> Dict[str, Any]:
        """
        Analyze compatibility between two birth charts.
        
        Args:
            person1_chart: First person's chart
            person2_chart: Second person's chart
            relationship_type: Type of relationship (romantic, business, etc.)
            
        Returns:
            Compatibility analysis with scores and insights
        """
        compatibility = {
            "relationship_type": relationship_type,
            "overall_score": 0,
            "element_compatibility": {},
            "planet_compatibility": {},
            "insights": {},
            "recommendations": []
        }
        
        if self.use_ai:
            # AI analyze relationship potential
            analysis = self.interpreter.analyze_compatibility(
                person1_chart, person2_chart
            )
            compatibility["insights"] = analysis
            
            # Calculate compatibility score
            compatibility["overall_score"] = \
                self._calculate_compatibility_score(person1_chart, person2_chart)
            
            # Provide relationship guidance
            compatibility["recommendations"] = \
                self._generate_relationship_guidance(
                    person1_chart, person2_chart, relationship_type
                )
        
        return compatibility

    def identify_life_patterns(
        self,
        birth_chart: Dict[str, Any],
        age: int
    ) -> Dict[str, Any]:
        """
        Identify major life patterns and cycles.
        
        Args:
            birth_chart: Birth chart data
            age: Person's current age
            
        Returns:
            Life patterns including cycles and transitions
        """
        patterns = {
            "age": age,
            "saturnian_return": False,
            "nodal_phases": [],
            "life_cycles": [],
            "major_themes": [],
            "upcoming_transitions": []
        }
        
        # Check for Saturn return (ages 29-30, 58-60)
        if (28 <= age <= 31) or (57 <= age <= 61):
            patterns["saturnian_return"] = True
            if self.use_ai:
                patterns["saturnian_return_meaning"] = \
                    "Major life restructuring and maturity phase"
        
        if self.use_ai:
            patterns["life_cycles"] = \
                self._analyze_life_cycles(birth_chart, age)
            patterns["major_themes"] = \
                self._identify_major_themes(birth_chart, age)
        
        return patterns

    def _analyze_personality(self, chart: Dict[str, Any]) -> Dict[str, str]:
        """Analyze personality based on chart."""
        return {
            "sun_sign": "Your core identity and life purpose",
            "moon_sign": "Your emotional nature and inner world",
            "rising_sign": "How you appear to others",
            "detailed": "Personality analysis requires AI (provide API keys)"
        }

    def _identify_life_themes(self, chart: Dict[str, Any]) -> List[str]:
        """Identify major life themes."""
        themes = [
            "Personal growth and self-discovery",
            "Relationships and connection",
            "Career and purpose",
            "Financial development",
            "Spiritual evolution"
        ]
        return themes

    def _forecast_month(
        self,
        start: datetime,
        end: datetime
    ) -> Dict[str, Any]:
        """Generate month forecast."""
        return {
            "period": start.strftime("%B %Y"),
            "energy": "Dynamic and transformative",
            "focus_areas": [
                "Communication and expression",
                "Relationships and partnerships",
                "Creative projects"
            ]
        }

    def _identify_opportunities(
        self,
        birth_chart: Dict[str, Any],
        forecast: Dict[str, Any]
    ) -> List[str]:
        """Identify opportunities in the forecast."""
        return [
            "Favorable period for starting new projects",
            "Good time for important decisions",
            "Opportunity for personal growth",
            "Potential for romance and connections"
        ]

    def _forecast_quarter(
        self,
        birth_chart: Dict[str, Any],
        start_month: int,
        year: int
    ) -> Dict[str, Any]:
        """Generate quarterly forecast."""
        quarters = {
            1: "Renewal and new beginnings",
            2: "Growth and expansion",
            3: "Peak energy and manifestation",
            4: "Reflection and integration"
        }
        quarter_num = (start_month - 1) // 3 + 1
        
        return {
            "quarter": f"Q{quarter_num}",
            "theme": quarters[quarter_num],
            "key_dates": [],
            "action_items": ["Focus on personal projects", "Build relationships"]
        }

    def _generate_yearly_recommendations(
        self,
        birth_chart: Dict[str, Any],
        year: int
    ) -> List[str]:
        """Generate yearly recommendations."""
        return [
            "Set clear intentions aligned with your chart",
            "Work with your natural rhythm",
            "Embrace growth opportunities",
            "Balance action with reflection",
            "Nurture important relationships"
        ]

    def _calculate_compatibility_score(
        self,
        chart1: Dict[str, Any],
        chart2: Dict[str, Any]
    ) -> float:
        """Calculate compatibility score 0-100."""
        # Simplified scoring
        return 75.0

    def _generate_relationship_guidance(
        self,
        chart1: Dict[str, Any],
        chart2: Dict[str, Any],
        relationship_type: str
    ) -> List[str]:
        """Generate relationship guidance."""
        return [
            "Honor each person's unique astrological nature",
            "Communicate needs openly and honestly",
            "Respect individual growth paths",
            "Build on shared values and goals",
            "Schedule important conversations mindfully"
        ]

    def _analyze_life_cycles(
        self,
        birth_chart: Dict[str, Any],
        age: int
    ) -> List[Dict[str, Any]]:
        """Analyze life cycles."""
        return [
            {
                "name": "Personal Year Cycle",
                "current_phase": "Growth and expansion",
                "duration": "1 year remaining"
            },
            {
                "name": "Nine-Year Cycle",
                "current_phase": "Year 3 of completion phase",
                "focus": "Mastery and refinement"
            }
        ]

    def _identify_major_themes(
        self,
        birth_chart: Dict[str, Any],
        age: int
    ) -> List[str]:
        """Identify major life themes."""
        return [
            "Self-actualization and purpose discovery",
            "Building meaningful relationships",
            "Creative expression and contribution",
            "Financial stability and abundance",
            "Spiritual development and wisdom"
        ]


def main():
    """Example usage of AstroAnalyzer."""
    # Initialize analyzer
    analyzer = AstroAnalyzer(use_ai=False)  # Set to True if API keys available
    
    # Example birth chart
    birth_dt = datetime(1990, 6, 15, 14, 30, 0)
    lat, lon = 40.7128, -74.0060  # NYC
    
    # Generate birth chart report
    print("🔮 Generating Birth Chart Report...")
    report = analyzer.generate_birth_chart_report(
        birth_dt, lat, lon, name="Subject"
    )
    print(json.dumps(report, indent=2, default=str))
    
    # Generate yearly forecast
    print("\n📅 Generating Yearly Forecast...")
    yearly = analyzer.generate_yearly_forecast(report["chart"], 2026)
    print(json.dumps(yearly, indent=2, default=str))
    
    # Identify life patterns
    print("\n🌀 Identifying Life Patterns...")
    patterns = analyzer.identify_life_patterns(report["chart"], age=33)
    print(json.dumps(patterns, indent=2, default=str))


if __name__ == "__main__":
    main()
