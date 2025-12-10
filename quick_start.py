#!/usr/bin/env python3
"""
ParaVision Analyzer - Main Entry Point

Usage:
    python quick_start.py           # Launch GUI (default)
    python quick_start.py --gui     # Launch GUI
    python quick_start.py --cli     # Launch CLI mode
"""

import sys
import os

def check_dependencies():
    """Check all required dependencies"""
    print("=" * 60)
    print("Checking Dependencies...")
    print("=" * 60)

    required_packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'scipy': 'scipy',
        'skimage': 'scikit-image',
        'PIL': 'Pillow',
        'tkinter': 'tkinter (usually built-in)'
    }

    missing = []

    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[X] {package} - MISSING")
            missing.append(package)

    if missing:
        print("\n" + "=" * 60)
        print("WARNING: Missing Dependencies")
        print("=" * 60)
        print("\nPlease run the following command to install:\n")
        print("    pip install -r requirements.txt\n")
        return False

    print("\n[OK] All dependencies installed!")
    return True

def check_data_structure():
    """Check data directory structure"""
    print("\n" + "=" * 60)
    print("Checking Data Directories...")
    print("=" * 60)

    data_dirs = ['data/images', 'data/annotations', 'data/results']

    for dir_path in data_dirs:
        if os.path.exists(dir_path):
            count = len([f for f in os.listdir(dir_path) if not f.startswith('.')])
            print(f"[OK] {dir_path} - {count} files")
        else:
            print(f"[WARN] {dir_path} - Does not exist (will be created)")
            os.makedirs(dir_path, exist_ok=True)

def main():
    """Main entry point"""
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install dependencies first")
        sys.exit(1)

    # Check data structure
    check_data_structure()

    # Determine execution mode
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # CLI mode
        print("\n" + "=" * 60)
        print("Launching CLI Mode...")
        print("=" * 60)

        # Check if data exists
        if not os.path.exists('data/images') or not os.path.exists('data/annotations'):
            print("\nWARNING: Please prepare data in data/images/ and data/annotations/")
            sys.exit(1)

        # Execute CLI
        from scripts.run_cli import main as cli_main
        sys.argv = [
            'run_cli.py',
            '--image-dir', 'data/images',
            '--annotation-dir', 'data/annotations',
            '--output-dir', 'data/results',
            '--px-per-mm', '19'
        ]
        cli_main()
    else:
        # GUI mode (default)
        print("\n" + "=" * 60)
        print("Launching GUI...")
        print("=" * 60)

        # Execute GUI
        from scripts.run_gui import main as gui_main
        gui_main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nFor help, see README.md or README_zh-TW.md")
        sys.exit(1)
