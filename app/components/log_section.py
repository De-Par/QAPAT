import tkinter as tk
from tkinter import ttk


class LogSection:
    def __init__(self, parent, app):
        self.log_area = None

        self.app = app

        self.frame = ttk.LabelFrame(parent, text="Processing Log", style="Section.TLabelframe")
        # Expand to fill available space above status bar but with MAXIMUM HEIGHT
        self.frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        # Create log area
        self.create_log_area()

    def create_log_area(self):
        """Create the log area with scrollbars"""
        text_frame = ttk.Frame(self.frame)
        text_frame.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        # Vertical scrollbar
        y_scroll = ttk.Scrollbar(text_frame)
        y_scroll.grid(row=0, column=1, sticky='ns')

        # Horizontal scrollbar
        x_scroll = ttk.Scrollbar(text_frame, orient='horizontal')
        x_scroll.grid(row=1, column=0, sticky='ew')

        # Text area
        self.log_area = tk.Text(
            text_frame,
            wrap='none',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            bg=self.app.current_theme['log_bg'],
            fg=self.app.current_theme['log_fg'],
            insertbackground=self.app.current_theme['log_fg'],
            font=('Arial', self.app.log_font_size),
            padx=10,
            pady=10,
            highlightcolor=self.app.current_theme['text_widget_highlight'],
            highlightbackground=self.app.current_theme['log_border'],
            selectbackground=self.app.current_theme['text_widget_selection']
        )
        self.log_area.grid(row=0, column=0, sticky='nsew')

        # Configure scrollbars
        y_scroll.config(command=self.log_area.yview)
        x_scroll.config(command=self.log_area.xview)

        self.log_area.configure(state='disabled')

    def toggle_visibility(self, visible):
        """Toggle visibility of the log section"""
        if visible:
            self.frame.grid()
            # Make log expandable to fill available space above status bar
            self.app.content_frame.grid_rowconfigure(3, weight=1)

        else:
            self.frame.grid_remove()
            # Remove expansion when hidden
            self.app.content_frame.grid_rowconfigure(3, weight=0)

    def update_font_size(self, size):
        """Update font size of the log area"""
        self.log_area.configure(font=('Arial', size))

    def reset(self):
        """Clear log content"""
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', 'end')
        self.log_area.configure(state='disabled')

    def update_theme(self, theme):
        """Update theme colors"""
        self.log_area.config(
            bg=theme['log_bg'],
            fg=theme['log_fg'],
            insertbackground=theme['log_fg'],
            highlightbackground=theme['log_border'],
            selectbackground=theme['text_widget_selection']
        )
