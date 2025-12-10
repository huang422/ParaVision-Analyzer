#!/usr/bin/env python3
"""
Command-line interface for ParaVision Analyzer

This script provides a command-line interface for batch processing
of parathyroid tumor images.

Usage:
    python scripts/run_cli.py --image-dir IMAGE_DIR --annotation-dir ANNOTATION_DIR --output-dir OUTPUT_DIR [--px-per-mm PX_PER_MM]

Example:
    python scripts/run_cli.py --image-dir data/images --annotation-dir data/annotations --output-dir data/results --px-per-mm 19
"""

import sys
import os
import argparse

# Add parent directory to path to import paravision_analyzer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paravision_analyzer import ParathyroidTumorAnalyzer


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='ParaVision Analyzer - Parathyroid Pattern Recognition System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python scripts/run_cli.py --image-dir data/images --annotation-dir data/annotations --output-dir data/results

  # Custom conversion ratio
  python scripts/run_cli.py --image-dir data/images --annotation-dir data/annotations --output-dir data/results --px-per-mm 20

For more information, see the README.md file.
        """
    )

    parser.add_argument(
        '--image-dir',
        type=str,
        required=True,
        help='Directory containing medical images (JPG, PNG, BMP)'
    )

    parser.add_argument(
        '--annotation-dir',
        type=str,
        required=True,
        help='Directory containing LabelMe JSON annotation files'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='Directory for output results (CSV and visualizations)'
    )

    parser.add_argument(
        '--px-per-mm',
        type=float,
        default=19,
        help='Pixel to millimeter conversion ratio (default: 19, meaning 1mm = 19px)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='ParaVision Analyzer 1.0.0'
    )

    return parser.parse_args()


def progress_callback(current, total, message):
    """Print progress to console"""
    progress = int((current + 1) / total * 100)
    print(f"[{progress:3d}%] {message}")


def main():
    """Main entry point for CLI"""
    args = parse_args()

    # Validate directories
    if not os.path.exists(args.image_dir):
        print(f"Error: Image directory does not exist: {args.image_dir}")
        sys.exit(1)

    if not os.path.exists(args.annotation_dir):
        print(f"Error: Annotation directory does not exist: {args.annotation_dir}")
        sys.exit(1)

    # Validate conversion ratio
    if args.px_per_mm <= 0:
        print(f"Error: Pixel to millimeter ratio must be positive, got: {args.px_per_mm}")
        sys.exit(1)

    print("=" * 60)
    print("ParaVision Analyzer")
    print("Parathyroid Pattern Recognition System")
    print("=" * 60)
    print(f"Image directory:      {args.image_dir}")
    print(f"Annotation directory: {args.annotation_dir}")
    print(f"Output directory:     {args.output_dir}")
    print(f"Conversion ratio:     1mm = {args.px_per_mm}px")
    print("=" * 60)
    print()

    try:
        # Create analyzer
        analyzer = ParathyroidTumorAnalyzer(
            image_dir=args.image_dir,
            json_dir=args.annotation_dir,
            output_dir=args.output_dir,
            px_per_mm=args.px_per_mm,
            progress_callback=progress_callback
        )

        # Run analysis
        print("Starting analysis...")
        analyzer.analyze_all_images()

        print()
        print("=" * 60)
        print("Analysis completed successfully!")
        print(f"Results saved to: {args.output_dir}")
        print(f"  - CSV file: {os.path.join(args.output_dir, 'parathyroid_analysis_results.csv')}")
        print(f"  - Visualizations: {os.path.join(args.output_dir, 'visualizations')}")
        print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"Error during analysis: {str(e)}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
