from tkinter import ttk


class ButtonSection:
    def __init__(self, parent, app):
        self.reset_btn = None
        self.start_btn = None
        self.theme_btn = None
        self.help_btn = None
        self.app = app
        self.frame = ttk.Frame(parent)
        self.frame.grid(row=4, column=0, columnspan=2, sticky='ew', padx=5, pady=15)
        self.frame.grid_columnconfigure(0, weight=1)  # Left side
        self.frame.grid_columnconfigure(1, weight=1)  # Middle
        self.frame.grid_columnconfigure(2, weight=1)  # Right side

        # Create buttons
        self.create_buttons()

    def create_buttons(self):
        """Create all buttons in the section"""
        # Left buttons frame (Help and Theme)
        left_frame = ttk.Frame(self.frame)
        left_frame.grid(row=0, column=0, sticky='w')  # Align to west (left)

        # Theme button
        self.theme_btn = ttk.Button(
            left_frame,
            text='☀️' if self.app.theme_mode == 'light' else '🌙',
            command=self.app.toggle_theme,
            width=3
        )
        self.theme_btn.pack(side='left', padx=5)
        self.app.add_tooltip(self.theme_btn, 'Toggle light/dark mode')

        # Help button
        self.help_btn = ttk.Button(
            left_frame,
            text='Help',
            command=self.app.show_help
        )
        self.help_btn.pack(side='left', padx=5)
        self.app.add_tooltip(self.help_btn, 'View help documentation')

        # Right buttons frame (Reset and Start)
        right_frame = ttk.Frame(self.frame)
        right_frame.grid(row=0, column=2, sticky='e')  # Align to east (right)

        # Start button
        self.start_btn = ttk.Button(
            right_frame,
            text='Start',
            command=self.app.start_process
        )
        self.start_btn.pack(side='right', padx=5)  # Pack right-to-left
        self.app.add_tooltip(self.start_btn, 'Begin processing with selected options')

        # Reset button
        self.reset_btn = ttk.Button(
            right_frame,
            text='Reset',
            command=self.app.reset_all
        )
        self.reset_btn.pack(side='right', padx=5)  # Pack right-to-left
        self.app.add_tooltip(self.reset_btn, 'Clear all inputs and logs')

    def disable_buttons(self):
        """Disable all buttons"""
        for widget in self.frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')
            elif isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.configure(state='disabled')

    def enable_buttons(self):
        """Enable all buttons"""
        for widget in self.frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='normal')
            elif isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.configure(state='normal')

    def update_theme_button(self, theme_mode):
        """Update theme button icon"""
        self.theme_btn.config(text='☀️' if theme_mode == 'light' else '🌙')

    def update_theme(self, theme):
        """Update theme colors"""
        pass  # Handled by style configuration
