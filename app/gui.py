import tkinter as tk
from tkinter import ttk
import threading
import queue

from .style import light_theme, dark_theme, font
from .utils import log_message
from .components import (
    InputSection, OptionsSection, TimeSection, LogSection,
    ButtonSection, StatusBar, Tooltip, ExitConfirmationDialog, HelpDialog
)


def get_screen_dim():
    """Get width and height of screen"""
    root = tk.Tk()
    root.withdraw()  
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy() 
    return screen_width, screen_height


# Screen dimensions
screen_w, screen_h = get_screen_dim()


# Minimal dimensions for application
dimensions = {
    'with_log': {
        'min_w': int(0.3 * screen_w),
        'min_h': screen_h // 2
    },
    'without_log': {
        'min_w': int(0.3 * screen_w),
        'min_h': int((screen_h // 2) * 0.85)
    }
}


class QATAP(tk.Tk):
    def __init__(self):
        super().__init__()
        self.style = None
        self.tooltip = None
        self.exit_dialog = None
        self.help_dialog = None
        self.processing_active = None
        self.log_queue = queue.Queue()

        self.title('Quality And Performance Assessment Tool')
        min_w, min_h = dimensions['with_log']['min_w'], dimensions['with_log']['min_h']
        self.geometry(f"{min_w}x{min_h}")
        self.minsize(min_w, min_h)

        # Initialize theme
        self.current_theme = light_theme
        self.theme_mode = 'light'
        self.configure_theme()

        # Initialize log visibility state
        self.log_visible = True
        self.log_visible_var = tk.BooleanVar(value=True)

        # Log font settings
        self.log_font_size = font['log_section']

        # Create main container
        self.main_container = ttk.Frame(self)
        # Fill entire window and expand
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Create content frame for grid-based components
        self.content_frame = ttk.Frame(self.main_container)
        # Pack with fill="both" and expand=True to fill available space above status bar
        self.content_frame.pack(fill='both', expand=True, side='top', padx=0, pady=0)
        
        # Configure grid rows and columns for content frame
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)  # Time section column
        self.content_frame.grid_rowconfigure(1, weight=0)  # Input
        self.content_frame.grid_rowconfigure(2, weight=0)  # Options
        self.content_frame.grid_rowconfigure(3, weight=1)  # Log (expandable) - fills available space
        self.content_frame.grid_rowconfigure(4, weight=0)  # Buttons

        # Initialize tooltips, exit dialog, and help dialog
        self.create_tooltip()
        self.create_exit_dialog()
        self.create_help_dialog()

        # Initialize components in content frame
        self.input_section = InputSection(self.content_frame, self)
        self.options_section = OptionsSection(self.content_frame, self)
        self.time_section = TimeSection(self.content_frame, self)
        self.log_section = LogSection(self.content_frame, self)
        self.button_section = ButtonSection(self.content_frame, self)
        
        # Status bar goes in main container with pack (bottom) - FIXED HEIGHT
        self.status_bar = StatusBar(self.main_container, self)
        
        # Force the status bar to be visible by updating the layout
        self.update_idletasks()

        # Bind hotkeys
        self.bind_hotkeys()

        # Start log queue processing
        self.process_log_queue()

        # Log startup message
        log_message(self.log_section.log_area, 'Application initialized. Ready to process files.', 'INFO', self.current_theme)
        log_message(self.log_section.log_area, 'Hotkeys: Ctrl+/Ctrl- to adjust font size, Ctrl+Q to exit', 'INFO', self.current_theme)
        
        # Bind window close event
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        # Bind window state changes
        self.bind('<Configure>', self.on_window_configure)
        
        # Ensure initial layout configuration
        self.configure_layout()

    def configure_layout(self):
        """Configure the layout to ensure proper component positioning"""
        # Ensure log section expands to fill available space above status bar
        if self.log_visible:
            self.content_frame.grid_rowconfigure(3, weight=1)
        else:
            self.content_frame.grid_rowconfigure(3, weight=0)
        
        # Force layout update
        self.content_frame.update_idletasks()

    def create_tooltip(self):
        """Initialize tooltips"""
        self.tooltip = Tooltip(self, delay=500)  
    
    def create_exit_dialog(self):
        """Initialize exit confirmation dialog"""
        self.exit_dialog = ExitConfirmationDialog(self, self.current_theme, screen_w, screen_h)
    
    def create_help_dialog(self):
        """Initialize help dialog"""
        self.help_dialog = HelpDialog(self, self.current_theme, screen_w, screen_h)
    
    def on_closing(self):
        """Handle application closing with confirmation dialog"""
        # Check if there's an active process running
        if hasattr(self, 'processing_active') and self.processing_active:
            message = 'A process is currently running.\nAre you sure you want to stop the session?'
            is_processing = True

        else:
            message = 'Are you sure you want to close the application?'
            is_processing = False
        
        # Show exit confirmation dialog
        if self.exit_dialog.show(message, is_processing):
            self.confirm_exit()
    
    def on_window_configure(self, event):
        """Handle window configuration changes"""
        # Ensure proper layout when window is resized
        if event.widget == self:
            # Force grid geometry update to ensure proper sizing
            self.content_frame.update_idletasks()
            
            # Ensure log section maintains proper expansion
            if self.log_visible:
                self.content_frame.grid_rowconfigure(3, weight=1)
    
    def confirm_exit(self):
        """Confirm and proceed with exit"""
        # If processing is active, log that it was stopped
        if hasattr(self, 'processing_active') and self.processing_active:
            log_message(self.log_section.log_area, 'Session stopped by user during processing', 'WARNING', self.current_theme)
        
        # Log the exit
        log_message(self.log_section.log_area, 'Application exit confirmed by user', 'INFO', self.current_theme)
        
        # Clean up resources
        self.cleanup()
        
        # Destroy the main window
        self.quit()
        self.destroy()
    
    def cleanup(self):
        """Clean up resources before exit"""
        if self.tooltip:
            self.tooltip.destroy()
        if self.exit_dialog:
            self.exit_dialog.destroy()
        if self.help_dialog:
            self.help_dialog.destroy()

    def add_tooltip(self, widget, text):
        """Add a tooltip to a widget"""
        widget.bind('<Enter>', lambda e, w=widget, t=text: self.tooltip.schedule_show(w, t))
        widget.bind('<Leave>', lambda e: self.tooltip.hide_tooltip())
        widget.bind('<Motion>', lambda e, w=widget, t=text: self.tooltip.schedule_show(w, t))

    def process_log_queue(self):
        """Process log messages from the queue (thread-safe)"""
        try:
            while True:
                message_data = self.log_queue.get_nowait()
                log_message(
                    self.log_section.log_area,
                    message_data['message'],
                    message_data['level'],
                    message_data['theme']
                )
        except queue.Empty:
            pass
        finally:
            # Schedule next check
            self.after(100, self.process_log_queue)

    def bind_hotkeys(self):
        """Bind keyboard shortcuts for font size adjustment"""
        # Increase font size: Ctrl+Plus or Ctrl+Equal
        self.bind('<Control-plus>', self.increase_font_size)
        self.bind('<Control-equal>', self.increase_font_size)  # Equal is same as plus without shift

        # Decrease font size: Ctrl+Minus
        self.bind('<Control-minus>', self.decrease_font_size)

        # Show/hide log: Ctrl+L
        self.bind('<Control-l>', lambda e: self.toggle_log_visibility(e))
        self.bind('<Control-L>', lambda e: self.toggle_log_visibility(e))
        
        # Exit application: Ctrl+Q
        self.bind('<Control-q>', lambda e: self.on_closing())
        self.bind('<Control-Q>', lambda e: self.on_closing())

    def increase_font_size(self, event=None):
        """Increase log font size with maximum limit"""
        if self.log_font_size < 20:
            self.log_font_size += 1
            self.log_section.update_font_size(self.log_font_size)

    def decrease_font_size(self, event=None):
        """Decrease log font size with minimum limit"""
        if self.log_font_size > 6:
            self.log_font_size -= 1
            self.log_section.update_font_size(self.log_font_size)

    def configure_theme(self):
        """Apply the current theme to the root window"""
        theme = self.current_theme
        self.configure(bg=theme['primary_bg'])

        # Create style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure main frame styles
        self.style.configure(
            'TFrame',
            background=theme['frame_bg']
        )
        
        # Configure transparent frame for options section
        self.style.configure(
            'Transparent.TFrame',
            background=theme['primary_bg']
        )

        self.style.configure(
            'Section.TLabelframe',
            background=theme['primary_bg'],
            borderwidth=1,
            relief='solid',
            padding=5,
            bordercolor=theme['border']
        )

        self.style.configure(
            'Section.TLabelframe.Label',
            background=theme['primary_bg'],
            foreground=theme['text_fg'],
            font=('Arial', font['frame_label'], 'bold')
        )

        # Configure button styles
        self.style.configure(
            'TButton',
            font=('Arial', font['main_button']),
            padding=6,
            background=theme['button_bg'],
            foreground=theme['button_fg'],
            bordercolor=theme['border'],
            focuscolor=theme['button_focus'] if 'button_focus' in theme else theme['button_bg']
        )

        self.style.map(
            'TButton',
            background=[
                ('active', theme['button_active']),
                ('pressed', theme['button_active']),
                ('hover', theme['button_hover'])
            ],
            foreground=[
                ('disabled', theme['button_disabled_fg'])
            ]
        )

        # Configure entry styles
        self.style.configure(
            'TEntry',
            padding=5,
            fieldbackground=theme['entry_bg'],
            foreground=theme['entry_fg'],
            bordercolor=theme['border'],
            focuscolor=theme['text_widget_highlight']
        )

        # Configure checkbox styles
        self.style.configure(
            'TCheckbutton',
            background=theme['primary_bg'],
            foreground=theme['checkbox_fg'],
            font=('Arial', font['options_section']),
            indicatorcolor=theme['checkbox_bg'],
            indicatorrelief='flat',
            indicatordiameter=12,
        )

        self.style.map(
            'TCheckbutton',
            indicatorcolor=[
                ('selected', theme['checkbox_selected']),
                ('active', theme['checkbox_selected'])
            ],
            background=[
                ('active', theme['checkbox_bg']),
                ('pressed', theme['checkbox_bg'])
            ],
            foreground=[
                ('active', theme['checkbox_fg']),
                ('pressed', theme['checkbox_fg'])
            ],
            focuscolor=[
                ('focus', theme['text_widget_highlight'])
            ]
        )

        # Configure label styles
        self.style.configure(
            'TLabel',
            background=theme['label_bg'],
            foreground=theme['label_fg']
        )

        # Configure scrollbar styles
        self.style.configure(
            'Vertical.TScrollbar',
            background=theme['scrollbar_bg'],
            bordercolor=theme['border'],
            arrowcolor=theme['scrollbar_fg'],
            troughcolor=theme['scrollbar_bg']
        )

        self.style.map(
            'Vertical.TScrollbar',
            background=[
                ('active', theme['scrollbar_active']),
                ('pressed', theme['scrollbar_active'])
            ]
        )

        self.style.configure(
            'Horizontal.TScrollbar',
            background=theme['scrollbar_bg'],
            bordercolor=theme['border'],
            arrowcolor=theme['scrollbar_fg'],
            troughcolor=theme['scrollbar_bg']
        )

        self.style.map(
            'Horizontal.TScrollbar',
            background=[
                ('active', theme['scrollbar_active']),
                ('pressed', theme['scrollbar_active'])
            ]
        )

    def toggle_log_visibility(self, event=None):
        """Toggle the visibility of the log section"""
        if event:
            self.log_visible_var.set(not self.log_visible_var.get())

        self.log_visible = self.log_visible_var.get()
        self.log_section.toggle_visibility(self.log_visible)

        # Reconfigure layout to ensure proper positioning
        self.configure_layout()

        # Adjust window size based on log visibility
        self.update_window_size()

    def update_window_size(self):
        """Adjust window size based on log visibility"""
        self.update_idletasks()
        current_width = self.winfo_width()
        current_height = self.winfo_height()

        if self.log_visible:
            min_width = dimensions['with_log']['min_w']
            min_height = dimensions['with_log']['min_h']
        else:
            min_width = dimensions['without_log']['min_w']
            min_height = dimensions['without_log']['min_h']
            current_height = min_height
        
        self.minsize(min_width, min_height)
        self.geometry(f"{current_width}x{current_height}")

    def validate_data(self):
        """Validate user inputs before processing"""
        return self.input_section.validate()

    def start_process(self):
        """Handle start button click"""
        if not self.validate_data():
            return

        # Get input values
        ref_dirs = self.input_section.get_ref_dirs()
        dis_dirs = self.input_section.get_dis_dirs()
        app_path = self.input_section.get_app_path()
        output_path = self.input_section.get_output_path()

        # Get selected options
        options = self.options_section.get_selected_options()

        # Get time values
        delay_time = self.time_section.get_delay_time()
        bench_time = self.time_section.get_bench_time()

        # Update UI state
        self.status_bar.set_status('Processing...')
        log_message(self.log_section.log_area, f'Starting analysis with {app_path}', 'INFO', self.current_theme)
        log_message(self.log_section.log_area, f'Reference driver directories: {', '.join(ref_dirs)}', 'INFO', self.current_theme)
        log_message(self.log_section.log_area, f'Distorted driver directories: {', '.join(dis_dirs)}', 'INFO', self.current_theme)
        log_message(self.log_section.log_area, f'Output directory: {output_path}', 'INFO', self.current_theme)
        log_message(self.log_section.log_area, f'Selected options: {', '.join(options) if options else 'None'}', 'INFO', self.current_theme)
        log_message(self.log_section.log_area, f'Delay time: {delay_time}s, Bench time: {bench_time}s', 'INFO', self.current_theme)

        # Set processing flag
        self.processing_active = True
        
        # Disable buttons during processing
        self.button_section.disable_buttons()

        # Create callback that both enables buttons and clears processing flag
        def enable_buttons_and_clear_flag():
            self.button_section.enable_buttons()
            self.processing_active = False
            self.status_bar.set_status('Ready')

        # Run processing in a separate thread
        from .utils import run_analysis
        threading.Thread(
            target=run_analysis,
            args=(
                self.log_queue,
                self.status_bar.status_var,
                ref_dirs,
                dis_dirs,
                app_path,
                output_path,
                options,
                delay_time,
                bench_time,
                self.current_theme,
                enable_buttons_and_clear_flag
            ),
            daemon=True
        ).start()

    def reset_all(self):
        """Handle reset button click"""
        try:
            # Reset all sections
            self.input_section.reset()
            self.options_section.reset()
            self.time_section.reset()
            self.log_section.reset()

            # Reset log visibility to default
            self.log_visible = True
            self.log_visible_var.set(True)
            self.toggle_log_visibility()

            # Add reset confirmation
            log_message(self.log_section.log_area, 'System reset completed. Ready for new input.', 'INFO', self.current_theme)
            self.status_bar.set_status('Ready')

            # Focus on first input
            self.input_section.ref_driver_text.focus()

            # Reset log font size
            self.log_section.update_font_size(font['log_section'])

        except Exception as e:
            log_message(self.log_section.log_area, f'Reset error: {str(e)}', 'ERROR', self.current_theme)
            self.status_bar.set_status('Error during reset')

    def show_help(self):
        """Show scrollable help information"""
        self.help_dialog.show()
        self.help_dialog.update_theme(self.current_theme)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme_mode = 'dark' if self.theme_mode == 'light' else 'light'
        self.current_theme = dark_theme if self.theme_mode == 'dark' else light_theme
        self.button_section.update_theme_button(self.theme_mode)

        # Update tooltip and exit dialog colors
        if self.tooltip:
            self.tooltip.update_theme(self.current_theme)
        if self.exit_dialog:
            self.exit_dialog.update_theme(self.current_theme)

        # Reconfigure the theme
        self.configure_theme()

        # Update all components
        self.input_section.update_theme(self.current_theme)
        self.options_section.update_theme(self.current_theme)
        self.time_section.update_theme(self.current_theme)
        self.log_section.update_theme(self.current_theme)
        self.button_section.update_theme(self.current_theme)
        self.status_bar.update_theme(self.current_theme)

        # Update help dialog if it exists
        if self.help_dialog:
            self.help_dialog.update_theme(self.current_theme)

        log_message(self.log_section.log_area, f'Switched to {self.theme_mode} theme', 'INFO', self.current_theme)
