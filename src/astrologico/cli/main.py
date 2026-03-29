"""
Astrologico CLI - Command-line interface for astrological calculations.

Provides command-line access to core astrological functions including:
- Chart generation with planetary positions and aspects
- Individual planetary position queries
- Aspect calculations
- Moon phase information
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

from src.astrologico.core import AstrologicalCalculator, format_chart_output


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Astrologico - Professional Astrological Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  astrologico chart --now --lat 40.7128 --lon -74.0060
  astrologico chart --date "2026-03-29 12:00:00" --lat 51.5074 --lon -0.1278
  astrologico chart --now --json > chart.json
  astrologico planets --now
  astrologico aspects --now --lat 48.8566 --lon 2.3522
  astrologico moon --now --json
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Chart command
    chart_parser = subparsers.add_parser('chart', help='Generate astrological chart')
    chart_parser.add_argument('--now', action='store_true', help='Use current UTC time')
    chart_parser.add_argument('--date', type=str, help='Date/time in UTC (YYYY-MM-DD HH:MM:SS)')
    chart_parser.add_argument('--lat', type=float, default=0.0, help='Observer latitude (default: 0)')
    chart_parser.add_argument('--lon', type=float, default=0.0, help='Observer longitude (default: 0)')
    chart_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Planets command
    planets_parser = subparsers.add_parser('planets', help='Get planetary positions')
    planets_parser.add_argument('--now', action='store_true', help='Use current UTC time')
    planets_parser.add_argument('--date', type=str, help='Date/time in UTC (YYYY-MM-DD HH:MM:SS)')
    planets_parser.add_argument('--lat', type=float, default=0.0, help='Observer latitude')
    planets_parser.add_argument('--lon', type=float, default=0.0, help='Observer longitude')
    planets_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Aspects command
    aspects_parser = subparsers.add_parser('aspects', help='Calculate planetary aspects')
    aspects_parser.add_argument('--now', action='store_true', help='Use current UTC time')
    aspects_parser.add_argument('--date', type=str, help='Date/time in UTC (YYYY-MM-DD HH:MM:SS)')
    aspects_parser.add_argument('--lat', type=float, default=0.0, help='Observer latitude')
    aspects_parser.add_argument('--lon', type=float, default=0.0, help='Observer longitude')
    aspects_parser.add_argument('--orb', type=float, default=8.0, help='Aspect orb in degrees (default: 8)')
    aspects_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Moon phase command
    moon_parser = subparsers.add_parser('moon', help='Get moon phase')
    moon_parser.add_argument('--now', action='store_true', help='Use current UTC time')
    moon_parser.add_argument('--date', type=str, help='Date/time in UTC (YYYY-MM-DD HH:MM:SS)')
    moon_parser.add_argument('--json', action='store_true', help='Output as JSON')

    return parser.parse_args()


def parse_datetime(args) -> Optional[datetime]:
    """
    Parse datetime from command-line arguments.
    
    Args:
        args: Parsed arguments with 'now' and 'date' fields
        
    Returns:
        Parsed datetime object or None if invalid
    """
    if args.now:
        return datetime.utcnow()
    elif hasattr(args, 'date') and args.date:
        try:
            return datetime.fromisoformat(args.date)
        except ValueError:
            print("Error: Invalid datetime format. Use YYYY-MM-DD HH:MM:SS", file=sys.stderr)
            return None
    else:
        print("Error: Specify --now or --date", file=sys.stderr)
        return None


def handle_chart_command(args, calc: AstrologicalCalculator) -> int:
    """Handle 'chart' command."""
    dt = parse_datetime(args)
    if not dt:
        return 1
    
    chart = calc.generate_chart(dt, args.lat, args.lon)
    
    if args.json:
        output = {
            'datetime_utc': chart.datetime_utc,
            'location': {'lat': chart.location_lat, 'lon': chart.location_lon},
            'moon_phase': chart.moon_phase,
            'moon_phase_name': _get_moon_phase_name(chart.moon_phase),
            'planets': {
                name: {
                    'longitude': pos.longitude,
                    'latitude': pos.latitude,
                    'distance_au': pos.distance,
                    'right_ascension': pos.right_ascension,
                    'declination': pos.declination,
                    'zodiac_sign': calc.get_zodiac_sign(pos.longitude)[0],
                    'sign_position': round(calc.get_zodiac_sign(pos.longitude)[1], 2)
                }
                for name, pos in chart.planets.items()
            },
            'aspects': chart.aspects
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_chart_output(chart))
    
    return 0


def handle_planets_command(args, calc: AstrologicalCalculator) -> int:
    """Handle 'planets' command."""
    dt = parse_datetime(args)
    if not dt:
        return 1
    
    positions = calc.calculate_planetary_positions(dt, args.lat, args.lon)
    
    if args.json:
        output = {
            'datetime_utc': dt.isoformat(),
            'location': {'lat': args.lat, 'lon': args.lon},
            'planets': {
                name: {
                    'longitude': pos.longitude,
                    'latitude': pos.latitude,
                    'distance_au': pos.distance,
                    'zodiac_sign': calc.get_zodiac_sign(pos.longitude)[0],
                    'sign_position': round(calc.get_zodiac_sign(pos.longitude)[1], 2)
                }
                for name, pos in positions.items()
            }
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nPlanetary Positions - {dt.isoformat()} UTC")
        print(f"Location: {args.lat}°, {args.lon}°\n")
        for name, pos in positions.items():
            sign, sign_pos = calc.get_zodiac_sign(pos.longitude)
            print(f"{name:10} | {pos.longitude:7.2f}° ({sign} {sign_pos:5.2f}°) | Distance: {pos.distance:7.4f} AU")
    
    return 0


def handle_aspects_command(args, calc: AstrologicalCalculator) -> int:
    """Handle 'aspects' command."""
    dt = parse_datetime(args)
    if not dt:
        return 1
    
    positions = calc.calculate_planetary_positions(dt, args.lat, args.lon)
    aspects = calc.calculate_aspects(positions, orb=args.orb)
    
    if args.json:
        output = {
            'datetime_utc': dt.isoformat(),
            'location': {'lat': args.lat, 'lon': args.lon},
            'orb': args.orb,
            'aspects_count': len(aspects),
            'aspects': aspects
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nPlanetary Aspects - {dt.isoformat()} UTC (Orb: {args.orb}°)\n")
        if aspects:
            for aspect in aspects:
                print(f"{aspect['planet1']:10} {aspect['aspect']:12} {aspect['planet2']:10} "
                      f"Angle: {aspect['angle']:6.2f}° (Orb: {aspect['orb']:5.2f}°)")
        else:
            print("No major aspects found within the specified orb.")
    
    return 0


def handle_moon_command(args, calc: AstrologicalCalculator) -> int:
    """Handle 'moon' command."""
    dt = parse_datetime(args)
    if not dt:
        return 1
    
    phase = calc.calculate_moon_phase(dt)
    phase_name = _get_moon_phase_name(phase)
    
    if args.json:
        output = {
            'datetime_utc': dt.isoformat(),
            'moon_phase': round(phase, 4),
            'moon_phase_name': phase_name,
            'illumination': f"{phase * 100:.1f}%"
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nMoon Phase - {dt.isoformat()} UTC")
        print(f"Phase: {phase_name}")
        print(f"Illumination: {phase * 100:.1f}%")
    
    return 0


def _get_moon_phase_name(phase: float) -> str:
    """Get moon phase name from 0-1 value."""
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


def main() -> int:
    """Main CLI entry point."""
    args = parse_arguments()
    
    if not args.command:
        parse_arguments().print_help()
        return 0
    
    calc = AstrologicalCalculator()
    
    try:
        if args.command == 'chart':
            return handle_chart_command(args, calc)
        elif args.command == 'planets':
            return handle_planets_command(args, calc)
        elif args.command == 'aspects':
            return handle_aspects_command(args, calc)
        elif args.command == 'moon':
            return handle_moon_command(args, calc)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
