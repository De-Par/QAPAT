import tkinter as tk
from tkinter import Text, Button, Frame, Scrollbar
from app.data import help_text
from app.style import font


class HelpDialog:
    """Help dialog component for displaying application documentation"""
    def __init__(self, parent, theme, sw, sh):
        self.parent = parent
        self.theme = theme
        self.sw = sw
        self.sh = sh
        self.help_window = None
        
    def show(self):
        """Show the help dialog"""
        # Prevent multiple help windows
        if self.help_window and self.help_window.winfo_exists():
            self.destroy()
            return

        self.help_window = tk.Toplevel(self.parent)
        self.help_window.title('Help Documentation')
        self.help_window.geometry(f'{int(0.4 * self.sw)}x{int(0.7 * self.sh)}')
        self.help_window.protocol('WM_DELETE_WINDOW', self.destroy)

        # Create frame
        frame = Frame(self.help_window, bg=self.theme['help_bg'])
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create scrollbar
        scrollbar = Scrollbar(
            frame,
            background=self.theme['scrollbar_bg'],
            troughcolor=self.theme['scrollbar_bg'],
            activebackground=self.theme['scrollbar_active']
        )
        scrollbar.pack(side='right', fill='y')

        # Create text area
        text_area = Text(
            frame,
            wrap='word',
            yscrollcommand=scrollbar.set,
            font=('Arial', font['help_window']),
            padx=10,
            pady=10,
            bg=self.theme['help_bg'],
            fg=self.theme['help_fg'],
            insertbackground=self.theme['help_fg'],
            selectbackground=self.theme['text_widget_selection'],
            relief='solid',
            borderwidth=1,
            highlightbackground=self.theme['help_border']
        )
        text_area.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text_area.yview)

        # Insert content
        text_area.insert('1.0', help_text.strip())
        text_area.config(state='disabled')  # Make read-only

        # Create close button
        if 'button_focus' in self.theme:
            hc = self.theme['button_focus']
        else:
            hc = self.theme['button_bg']
        close_btn = Button(
            self.help_window,
            text='Close',
            command=self.destroy,
            padx=20,
            pady=5,
            bg=self.theme['button_bg'],
            fg=self.theme['button_fg'],
            activebackground=self.theme['button_active'],
            activeforeground=self.theme['button_fg'],
            relief='raised',
            borderwidth=1,
            highlightbackground=self.theme['button_bg'],
            highlightcolor=hc,
            cursor='hand2'
        )
        close_btn.pack(pady=10)

        # Center window
        self.help_window.update_idletasks()
        width = self.help_window.winfo_width()
        height = self.help_window.winfo_height()
        x = (self.parent.winfo_screenwidth() // 2) - (width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (height // 2)
        self.help_window.geometry(f'+{x}+{y}')
        
    def destroy(self):
        """Destroy the help window"""
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.destroy()
            self.help_window = None
            
    def update_theme(self, theme):
        """Update the help dialog theme"""
        self.theme = theme
        if self.help_window and self.help_window.winfo_exists():
            try:
                # Update help window background
                self.help_window.configure(bg=self.theme['help_bg'])
                
                # Find and update all widgets in the help window
                for widget in self.help_window.winfo_children():
                    if isinstance(widget, tk.Frame):
                        widget.configure(bg=self.theme['help_bg'])
                        # Update scrollbar if it exists
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Scrollbar):
                                child.configure(
                                    background=self.theme['scrollbar_bg'],
                                    troughcolor=self.theme['scrollbar_bg'],
                                    activebackground=self.theme['scrollbar_active']
                                )
                            elif isinstance(child, tk.Text):
                                child.configure(
                                    bg=self.theme['help_bg'],
                                    fg=self.theme['help_fg'],
                                    insertbackground=self.theme['help_fg'],
                                    selectbackground=self.theme['text_widget_selection'],
                                    highlightbackground=self.theme['help_border']
                                )
                    elif isinstance(widget, tk.Button):
                        if 'button_focus' in self.theme:
                            hc = self.theme['button_focus']
                        else:
                            hc = self.theme['button_bg']
                        widget.configure(
                            bg=self.theme['button_bg'],
                            fg=self.theme['button_fg'],
                            activebackground=self.theme['button_active'],
                            activeforeground=self.theme['button_fg'],
                            highlightbackground=self.theme['button_bg'],
                            highlightcolor=hc
                        )
            except Exception as e:
                # Log error but don't crash the application
                print(f'Error updating help window theme: {e}')
                
    def exists(self):
        """Check if help window exists and is visible"""
        return self.help_window and self.help_window.winfo_exists()
