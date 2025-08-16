import tkinter as tk
from tkinter import ttk
from app.style import font  # Ensure this module exists


class ExitConfirmationDialog:
    """Exit confirmation dialog with smart session detection"""
    def __init__(self, parent, theme):
        self.parent = parent
        self.yes_callback = None
        self.theme = theme or {}
        self.dialog = None

    def show(self, message, is_processing=False):
        """Show exit confirmation dialog"""
        # Create confirmation dialog
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title('Confirm Exit')
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=self.theme['primary_bg'])

        # Handle window closing via title bar
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_no_clicked)

        # Create main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)

        # Icon and title frame
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(15, 15))

        # Warning icon
        warning_label = ttk.Label(
            title_frame,
            background=self.theme['primary_bg'],
            text='⚠️',
            padding=10,
            font=('Arial', 32)
        )
        warning_label.pack(side='left', padx=(0, 10))

        # Message label (with dynamic wrapping)
        message_label = ttk.Label(
            title_frame,
            padding=20,
            text=message,
            justify='center',
            background=self.theme['primary_bg'],
            font=('Arial', font['exit_window'], 'bold')
        )
        message_label.pack(side='left', fill='x', expand=True)

        # Additional info for processing
        if is_processing:
            info_label = ttk.Label(
                main_frame,
                text='Note: Stopping the session will terminate any running processes!',
                justify='center',
                padding=20,
                font=('Arial', font['exit_window'], 'bold'),
                background=self.theme['primary_bg'],
                foreground=self.theme.get('warning_fg', "#ff6600")
            )
            info_label.pack(pady=(0, 20))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 10))

        # Yes button
        yes_btn = ttk.Button(
            button_frame,
            text='Yes',
            command=self._on_yes_clicked
        )
        yes_btn.pack(side='right', padx=(10, 0))

        # No button
        no_btn = ttk.Button(
            button_frame,
            text='No',
            command=self._on_no_clicked
        )
        no_btn.pack(side='right')

        # Key bindings
        self.dialog.bind('<Escape>', lambda e: self._on_no_clicked())
        self.dialog.bind('<Return>', lambda e: self._on_yes_clicked())
        no_btn.focus_set()

        # Calculate size AFTER widgets are rendered
        self.dialog.update_idletasks()  # Critical for accurate sizing
        self._center_dialog()

        # Store callback for yes action
        self.yes_callback = None

        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        return getattr(self, 'result', False)

    def _center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_reqwidth()
        height = self.dialog.winfo_reqheight()

        # Calculate position
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)

        self.dialog.geometry(f"+{x}+{y}")

    def _on_yes_clicked(self):
        """Handle yes button click"""
        self.result = True
        self._safe_destroy()

    def _on_no_clicked(self):
        """Handle no button click"""
        self.result = False
        self._safe_destroy()

    def _safe_destroy(self):
        """Safely destroy dialog window"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()
        self.dialog = None  # Clear reference to prevent ghost windows

    def update_theme(self, theme):
        """Update dialog theme colors"""
        self.theme = theme
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.configure(bg=theme['primary_bg'])
            # Update child widgets
            for widget in self.dialog.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, (ttk.Label, ttk.Button)):
                            child.configure(background=theme['primary_bg'])

    def destroy(self):
        """Public destroy method"""
        self._safe_destroy()
