#!/usr/bin/env python3
"""
Astrologico CLI - Command-line interface for astrological calculations.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from astrologico import AstrologicalCalculator, format_chart_output


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Astrologico - Professional Astrological Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s chart --now --lat 40.7128 --lon -74.0060
  %(prog)s chart --date "2026-03-29 12:00:00" --lat 51.5074 --lon -0.1278
  %(prog)s chart --now --json > chart.json
  %(prog)s planets --now
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
    aspects_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # Moon phase command
    moon_parser = subparsers.add_parser('moon', help='Get moon phase')
    moon_parser.add_argument('--now', action='store_true', help='Use current UTC time')
    moon_parser.add_argument('--date', type=str, help='Date/time in UTC (YYYY-MM-DD HH:MM:SS)')
    moon_parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Parse datetime
    if args.now:
        dt = datetime.utcnow()
    elif hasattr(args, 'date') and args.date:
        try:
            dt = datetime.fromisoformat(args.date)
        except ValueError:
            print(f"Error: Invalid datetime format. Use YYYY-MM-DD HH:MM:SS", file=sys.stderr)
            return 1
    else:
        print("Error: Specify --now or --date", file=sys.stderr)
        return 1

    calc = AstrologicalCalculator()
    lat = getattr(args, 'lat', 0.0)
    lon = getattr(args, 'lon', 0.0)

    if args.command == 'chart':
        chart = calc.generate_chart(dt, lat, lon)
        if args.json:
            output = {
                'datetime_utc': chart.datetime_utc,
                'location': {'lat': chart.location_lat, 'lon': chart.location_lon},
                'moon_phase': chart.moon_phase,
                'planets': {
                    name: {
                        'longitude': pos.longitude,
                        'latitude': pos.latitude,
                        'distance': pos.distance,
                        'ra': pos.right_ascension,
                        'dec': pos.declination
                    }
                    for name, pos in chart.planets.items()
                },
                'aspects': chart.aspects
            }
            print(json.dumps(output, indent=2))
        else:
            print(format_chart_output(chart))

    elif args.command == 'planets':
        positions = calc.calculate_planetary_positions(dt, lat, lon)
        if args.json:
            output = {
                'datetime_utc': dt.isoformat(),
                'location': {'lat': lat, 'lon': lon},
                'planets': {
                    name: {
                        'longitude': pos.longitude,
                        'latitude': pos.latitude,
                        'distance': pos.distance
                    }
                    for name, pos in positions.items()
                }
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\nPlanetary Positions - {dt.isoformat()} UTC")
            print(f"Location: {lat}°, {lon}°\n")
            for name, pos in positions.items():
                sign, sign_pos = calc.get_zodiac_sign(pos.longitude)
                print(f"{name:10} | {pos.longitude:7.2f}° ({sign} {sign_pos:5.2f}°) | Distance: {pos.distance:7.4f} AU")

    elif args.command == 'aspects':
        positions = calc.calculate_planetary_positions(dt, lat, lon)
        aspects = calc.calculate_aspects(positions)
        if args.json:
            output = {
                'datetime_utc': dt.isoformat(),
                'location': {'lat': lat, 'lon': lon},
                'aspects': aspects
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\nPlanetary Aspects - {dt.isoformat()} UTC\n")
            if aspects:
                for aspect in aspects:
                    print(f"{aspect['planet1']:10} {aspect['aspect']:12} {aspect['planet2']:10} "
                          f"| Angle: {aspect['angle']:6.2f}° (Orb: {aspect['orb']:5.2f}°)")
            else:
                print("No major aspects found.")

    elif args.command == 'moon':
        phase = calc.calculate_moon_phase(dt)
        if args.json:
            output = {
                'datetime_utc': dt.isoformat(),
                'moon_phase': phase,
                'illumination': f"{phase:.2%}"
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\nMoon Phase - {dt.isoformat()} UTC")
            print(f"Illumination: {phase:.2%}")
            if phase < 0.25:
                print("Phase: Waxing Crescent")
            elif phase < 0.5:
                print("Phase: Waxing Gibbous")
            elif phase < 0.75:
                print("Phase: Waning Gibbous")
            else:
                print("Phase: Waning Crescent")

    return 0


if __name__ == '__main__':
    sys.exit(main())
