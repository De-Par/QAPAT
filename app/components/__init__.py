"""
    UI Components Package
    This package contains modular UI components for the Quality And Performance Assessment Tool
"""

# Import all components for easier access
from .input_section import InputSection
from .options_section import OptionsSection
from .time_section import TimeSection
from .log_section import LogSection
from .button_section import ButtonSection
from .status_bar import StatusBar
from .tooltip import Tooltip
from .exit_dialog import ExitConfirmationDialog
from .help_dialog import HelpDialog

__all__ = [
    'InputSection',
    'OptionsSection',
    'TimeSection',
    'LogSection',
    'ButtonSection',
    'StatusBar',
    'Tooltip',
    'ExitConfirmationDialog',
    'HelpDialog'
]