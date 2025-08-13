import tkinter as tk
from tkinter import ttk


class ExitConfirmationDialog:
    """Exit confirmation dialog with smart session detection"""
    def __init__(self, parent, theme=None):
        self.parent = parent
        self.yes_callback = None
        self.theme = theme or {}
        self.dialog = None
        self.width = 400
        self.height = 200
        
    def show(self, message, is_processing=False):
        """Show exit confirmation dialog"""
        # Create confirmation dialog
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title('Confirm Exit')
        self.dialog.geometry(f'{self.width}x{self.height}')
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)  # Make dialog modal
        self.dialog.grab_set()  # Grab all events
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.parent.winfo_screenwidth() // 2) - (self.width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (self.height // 2)
        self.dialog.geometry(f'{self.width}x{self.height}+{x}+{y}')
        
        # Configure dialog theme
        self.dialog.configure(bg=self.theme['primary_bg'])
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Icon and title frame
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(15, 15))
        
        # Warning icon (using text symbol)
        warning_label = ttk.Label(
            title_frame,
            background=self.theme['primary_bg'],
            text='⚠️',
            font=('Arial', 30)
        )
        warning_label.pack(side='left', padx=(0, 10))
        
        # Message label
        message_label = ttk.Label(
            title_frame,
            text=message,
            wraplength=self.width,
            justify='center',
            background=self.theme['primary_bg'],
            font=('Arial', 12, 'bold')
        )
        message_label.pack(side='left', fill='x', expand=True)
        
        # Additional info for processing
        if is_processing:
            info_label = ttk.Label(
                main_frame,
                text='Note: Stopping the session will terminate any running processes!',
                wraplength=self.width,
                justify='center',
                font=('Arial', 12),
                background=self.theme['primary_bg'],
                foreground=self.theme.get('warning_fg', "#ff6600")
            )
            info_label.pack(pady=(0, 20))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 10))
        
        # Yes button (exit) - styled as danger button
        yes_btn = ttk.Button(
            button_frame,
            text='Yes',
            command=self._on_yes_clicked,
            style='TButton'
        )
        yes_btn.pack(side='right', padx=(10, 0))
        
        # No button (cancel) - styled as primary button
        no_btn = ttk.Button(
            button_frame,
            text='No',
            command=self._on_no_clicked,
            style='TButton'
        )
        no_btn.pack(side='right')
        
        # Bind Escape key to cancel
        self.dialog.bind('<Escape>', lambda e: self._on_no_clicked())
        
        # Bind Enter key to confirm exit
        self.dialog.bind('<Return>', lambda e: self._on_yes_clicked())
        
        # Focus on No button by default (safer choice)
        no_btn.focus_set()
        
        # Store callback for yes action
        self.yes_callback = None
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        
        # Return result
        return getattr(self, 'result', False)
    
    def _on_yes_clicked(self):
        """Handle yes button click"""
        self.result = True
        if self.dialog:
            self.dialog.destroy()
    
    def _on_no_clicked(self):
        """Handle no button click"""
        self.result = False
        if self.dialog:
            self.dialog.destroy()
    
    def update_theme(self, theme):
        """Update dialog theme colors"""
        self.theme = theme
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.configure(bg=theme['primary_bg'])
            # Update other theme elements if needed
            for widget in self.dialog.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Label) and 'warning' in str(child):
                            child.configure(foreground=theme.get('warning_fg', "#ff6600"))
    
    def destroy(self):
        """Destroy the dialog if it exists"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()
            self.dialog = None
