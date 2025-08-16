import tkinter as tk
from app.style import font


class Tooltip:
    def __init__(self, parent, delay=500):
        self.parent = parent
        self.delay = delay
        self.tooltip_window = None
        self.tooltip_label = None
        self.scheduled_id = None
        self.current_widget = None
        self.current_text = None
        self.theme = getattr(parent, 'current_theme', None)
        
    def create_tooltip_window(self):
        """Create the tooltip window if it doesn't exist"""
        if self.tooltip_window is None:
            self.tooltip_window = tk.Toplevel(self.parent)
            self.tooltip_window.withdraw()
            self.tooltip_window.overrideredirect(True)
            self.tooltip_window.attributes('-topmost', True)
            
            # Get theme colors
            theme = getattr(self.parent, 'current_theme', self.theme) or {}
            
            self.tooltip_label = tk.Label(
                self.tooltip_window,
                background=theme.get('tooltip_bg', "#eeeeee"),
                relief='solid',
                borderwidth=1,
                padx=8,
                pady=4,
                foreground=theme.get('tooltip_fg', "#000000"),
                font=('Arial', font['tooltip_label']),
                justify='left'
            )
            self.tooltip_label.pack()
    
    def update_theme(self, theme):
        """Update tooltip colors when theme changes"""
        self.theme = theme
        if self.tooltip_label:
            self.tooltip_label.configure(
                background=theme.get('tooltip_bg', "#eeeeee"),
                foreground=theme.get('tooltip_fg', "#000000")
            )
    
    def schedule_show(self, widget, text):
        """Schedule tooltip to show after delay"""
        self.cancel_scheduled()
        self.current_widget = widget
        self.current_text = text
        
        if self.delay > 0:
            self.scheduled_id = self.parent.after(self.delay, self.show_tooltip)
    
    def cancel_scheduled(self):
        """Cancel any scheduled tooltip display"""
        if self.scheduled_id:
            self.parent.after_cancel(self.scheduled_id)
            self.scheduled_id = None
    
    def show_tooltip(self):
        """Show the tooltip at the current mouse position"""
        if not self.current_widget or not self.current_text:
            return
            
        self.create_tooltip_window()
        
        # Get mouse position
        x = self.parent.winfo_pointerx() + 15
        y = self.parent.winfo_pointery() + 15
        
        # Update tooltip content
        self.tooltip_label.config(text=self.current_text)
        
        # Position tooltip
        self.tooltip_window.geometry(f"+{x}+{y}")
        self.tooltip_window.deiconify()
        
        # Ensure tooltip is visible on screen
        self.tooltip_window.update_idletasks()
        self.adjust_position()
    
    def adjust_position(self):
        """Adjust tooltip position to ensure it's visible on screen"""
        if not self.tooltip_window:
            return
            
        # Get screen dimensions
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        # Get tooltip dimensions
        tooltip_width = self.tooltip_window.winfo_width()
        tooltip_height = self.tooltip_window.winfo_height()
        
        # Get current position
        x = self.tooltip_window.winfo_x()
        y = self.tooltip_window.winfo_y()
        
        # Adjust if tooltip goes off-screen
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        
        if y + tooltip_height > screen_height:
            y = self.parent.winfo_pointery() - tooltip_height - 10
        
        # Ensure minimum position
        x = max(0, x)
        y = max(0, y)
        
        self.tooltip_window.geometry(f"+{x}+{y}")
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        self.cancel_scheduled()
        if self.tooltip_window:
            self.tooltip_window.withdraw()
        self.current_widget = None
        self.current_text = None
    
    def destroy(self):
        """Clean up tooltip resources"""
        self.cancel_scheduled()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
        self.tooltip_label = None
