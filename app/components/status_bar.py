import tkinter as tk
from tkinter import ttk


class StatusBar:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        # Pin to bottom using pack - always stays at bottom of window with FIXED HEIGHT
        self.frame.pack(side='bottom', fill='x', padx=5, pady=0)
        self.frame.grid_columnconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set('Ready')
        self.bar = ttk.Label(
            self.frame,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w',
            padding=(8, 8),
            background=self.app.current_theme['status_bg'],
            foreground=self.app.current_theme['text_fg']
        )
        self.bar.grid(row=0, column=0, sticky='ew')
        
        # Ensure the frame has the same background as the status bar
        # For ttk widgets, we need to use style configuration
        style = ttk.Style()
        style.configure('StatusBar.TFrame', background=self.app.current_theme['status_bg'])
        self.frame.configure(style='StatusBar.TFrame')

    def set_status(self, status):
        """Set status text"""
        self.status_var.set(status)

    def update_theme(self, theme):
        """Update theme colors"""
        self.bar.configure(
            background=theme['status_bg'],
            foreground=theme['text_fg']
        )
        