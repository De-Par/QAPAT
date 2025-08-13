import tkinter as tk
from tkinter import ttk


def get_tooltip_text(key):
    """Get tooltip text for each option"""
    tooltips = {
        'quality_report': 'Generate a detailed analysis report with quality metrics',
        'frames_comparison': 'Create HTML page with frames comparison',
        'merge_movies': 'Merge dist and ref movies into a single file',
        'merge_plots': 'Merge resulting plots into a single report file',
        'perf_report': 'Generate a detailed analysis report with performance metrics',
    }
    return tooltips.get(key, 'Processing option')


class OptionsSection:
    def __init__(self, parent, app):
        self.log_visibility_chk = None
        self.app = app
        self.check_vars = {}
        self.frame = ttk.LabelFrame(parent, text='Processing Options', style='Section.TLabelframe')
        self.frame.grid(row=2, column=0, sticky='ew', padx=5, pady=10)
        self.frame.grid_columnconfigure(0, weight=1)

        # Create checkboxes
        self.create_checkbox('Quality report', 'quality_report')
        self.create_checkbox('Frames comparison', 'frames_comparison')
        self.create_checkbox('Merge movies', 'merge_movies')
        self.create_checkbox('Merge plots', 'merge_plots')
        self.create_checkbox('Performance report', 'perf_report')

        # Add log visibility checkbox
        self.create_log_visibility_checkbox()

    def create_checkbox(self, text, key):
        """Create a checkbox with tooltip"""
        var = tk.IntVar()
        self.check_vars[key] = var

        # Create frame to contain checkbox (transparent)
        chk_frame = ttk.Frame(self.frame, style='Transparent.TFrame')
        chk_frame.pack(fill='x', padx=10, pady=4)

        chk = ttk.Checkbutton(chk_frame, text=text, variable=var)
        chk.pack(side='left')

        # Add tooltip
        self.app.add_tooltip(chk, get_tooltip_text(key))

    def create_log_visibility_checkbox(self):
        """Create checkbox for log visibility"""
        chk_frame = ttk.Frame(self.frame, style='Transparent.TFrame')
        chk_frame.pack(fill='x', padx=10, pady=4)

        self.log_visibility_chk = ttk.Checkbutton(
            chk_frame,
            text='Show log panel',
            variable=self.app.log_visible_var,
            command=self.app.toggle_log_visibility
        )
        self.log_visibility_chk.pack(side='left')
        self.app.add_tooltip(self.log_visibility_chk, 'Toggle visibility of the log panel')

    def get_selected_options(self):
        """Get selected options"""
        return [opt for opt, var in self.check_vars.items() if var.get()]

    def reset(self):
        """Reset all options"""
        for var in self.check_vars.values():
            var.set(0)

    def update_theme(self, theme):
        """Update theme colors"""
        pass  # Handled by style configuration
