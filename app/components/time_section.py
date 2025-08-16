import tkinter as tk
from tkinter import ttk


def get_tooltip_text(key):
    """Get tooltip text for each time field"""
    tooltips = {
        'delay_time': 'Delay time in seconds before processing starts',
        'bench_time': 'Benchmark time in seconds for performance measurement',
    }
    return tooltips.get(key, 'Time setting')


def validate_integer(value, minimum, maximum):
    if value == "":
        return True  # Allow temporary empty field
    try:
        num = int(value)
        if not (minimum <= num <= maximum):
            return False
        # Check for leading zeros (except single zero)
        if value[0] == '0' and len(value) > 1:
            return False
        return True
    except ValueError:  # Non-integer input
        return False


def delay_validation_wrapper(value):
    """Create wrapper function for delay_time field"""
    return validate_integer(value=value, minimum=0, maximum=180)


def bench_validation_wrapper(value):
    """Create wrapper function for bench_time field"""
    return validate_integer(value=value, minimum=1, maximum=180)


class TimeSection:
    def __init__(self, parent, app):
        self.delay_time_var = None
        self.bench_time_var = None
        self.delay_time_entry = None
        self.bench_time_entry = None
        self.app = app

        # Create the main frame with label
        self.frame = ttk.LabelFrame(parent, text='Time Options', style='Section.TLabelframe')
        self.frame.grid(row=2, column=1, sticky='nsew', padx=(5, 5), pady=10)
        self.frame.grid_columnconfigure(0, weight=1)

        # Create input fields
        self.create_time_input_fields()

    def create_time_input_fields(self):
        """Create delay time and bench time input fields"""
        # Delay time field
        delay_frame = ttk.Frame(self.frame)
        delay_frame.pack(fill='x', padx=10, pady=5)
        delay_frame.grid_columnconfigure(1, weight=1)  # Center the entry field

        delay_label = ttk.Label(delay_frame, text='Delay time:', padding=4, width=12, anchor='center')
        delay_label.grid(row=0, column=0, padx=(0, 10), sticky='w')

        self.delay_time_var = tk.StringVar(value='0')
        self.delay_time_entry = ttk.Entry(delay_frame, textvariable=self.delay_time_var, width=8)
        self.delay_time_entry.grid(row=0, column=1, sticky='ew')

        # Add validation for integer only
        self.delay_time_entry.config(validate='key', validatecommand=(self.app.register(delay_validation_wrapper), '%P'))
        self.delay_time_entry.bind('<FocusOut>', lambda event, w=self.delay_time_entry, d='0': self.handle_focus_out(w, d))

        # Add tooltip
        self.app.add_tooltip(self.delay_time_entry, get_tooltip_text('delay_time'))

        # Bench time field
        bench_frame = ttk.Frame(self.frame)
        bench_frame.pack(fill='x', padx=10, pady=5)
        bench_frame.grid_columnconfigure(1, weight=1)  # Center the entry field

        bench_label = ttk.Label(bench_frame, text='Bench time:', padding=4, width=12, anchor='center')
        bench_label.grid(row=0, column=0, padx=(0, 10), sticky='w')

        self.bench_time_var = tk.StringVar(value='1')
        self.bench_time_entry = ttk.Entry(bench_frame, textvariable=self.bench_time_var, width=8)
        self.bench_time_entry.grid(row=0, column=1, sticky='ew')

        # Add validation for integer only
        self.bench_time_entry.config(validate='key', validatecommand=(self.app.register(bench_validation_wrapper), '%P'))
        self.bench_time_entry.bind('<FocusOut>', lambda event, w=self.bench_time_entry, d='1': self.handle_focus_out(w, d))

        # Add tooltip
        self.app.add_tooltip(self.bench_time_entry, get_tooltip_text('bench_time'))

    def handle_focus_out(self, widget, default_value):
        """Replace empty field with '0' when focus leaves"""
        if widget.get() == "":
            widget.delete(0, tk.END)
            widget.insert(0, default_value)

    def get_delay_time(self):
        """Get delay time value"""
        try:
            return int(self.delay_time_var.get() or '0')
        except ValueError:
            return 0

    def get_bench_time(self):
        """Get bench time value"""
        try:
            return int(self.bench_time_var.get() or '1')
        except ValueError:
            return 0

    def reset(self):
        """Reset all time fields"""
        self.delay_time_var.set('0')
        self.bench_time_var.set('1')

    def update_theme(self, theme):
        """Update theme colors"""
        pass  # Handled by style configuration
