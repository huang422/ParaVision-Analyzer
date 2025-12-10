#!/usr/bin/env python3
"""
Launch GUI application for ParaVision Analyzer

This script starts the graphical user interface for
ParaVision Analyzer - Parathyroid Pattern Recognition System.

Usage:
    python scripts/run_gui.py
"""

import sys
import os

# Add parent directory to path to import paravision_analyzer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from paravision_analyzer.gui import ParathyroidAnalyzerGUI


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    app = ParathyroidAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
