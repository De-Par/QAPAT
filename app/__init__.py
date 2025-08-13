"""
Quality And Performance Assessment Tool Package

This package contains the main application for quality and performance assessment analysis.
It provides a GUI interface for configuring and running quality analysis processes.

Modules:
    main: Application entry point
    gui: Main GUI application class
    utils: Utility functions and processing logic
    data: Application data class

Subpackages:
    components: UI component modules
    components: UI style modules
"""

# Import main application function for easier access
from .main import main

# Make components package accessible
from . import components

# Make style package accessible
from . import style

__all__ = ['main', 'gui', 'data', 'utils', 'style', 'components']
