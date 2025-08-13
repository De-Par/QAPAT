import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from app.utils import log_message, configure_scrollbar_colors, configure_text_widget_theme
from app.style import font
import os


class InputSection:
    def __init__(self, parent, app):
        self.app_entry = None
        self.output_entry = None
        self.dis_driver_text = None
        self.ref_driver_text = None
        self.app = app
        self.frame = ttk.LabelFrame(parent, text='Input Configuration', style='Section.TLabelframe')
        self.frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.frame.grid_columnconfigure(0, weight=1)

        # Create driver directories fields
        self.create_driver_field('Reference driver:', 'reference_driver', 0)
        self.create_driver_field('Distorted driver:', 'distorted_driver', 1)

        # Create application path field
        self.create_path_field('Application:', 2, 'file')

        # Create output directory field
        self.create_path_field('Output directory:', 3, 'dir')

    def create_driver_field(self, label_text, driver_type, row):
        """Create a driver directory field with multiple path support"""
        frame = ttk.Frame(self.frame)
        frame.grid(row=row, column=0, sticky='ew', padx=10, pady=(8 if row == 0 else 4))
        frame.grid_columnconfigure(1, weight=1)

        # Label
        lbl = ttk.Label(frame, padding=4, text=label_text, width=12, anchor='center')
        lbl.grid(row=0, column=0, padx=(0, 10), sticky='w')

        # Text frame for scrollable area
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=0, column=1, sticky='ew', padx=(0, 10))
        text_frame.grid_columnconfigure(0, weight=1)

        # Create a text widget for multiple paths
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            height=3,
            highlightcolor=self.app.current_theme['text_widget_highlight'],
            wrap='none',
            font=('TkDefaultFont', font['dri_field_input']),
            bg=self.app.current_theme['text_widget_bg'],
            fg=self.app.current_theme['text_widget_fg'],
            insertbackground=self.app.current_theme['text_widget_fg'],
            selectbackground=self.app.current_theme['text_widget_selection'],
            highlightbackground=self.app.current_theme['border'],
            relief='solid',
            borderwidth=1
        )
        text_widget.grid(row=0, column=0, sticky='ew')

        # Configure scrollbar colors to match theme
        configure_scrollbar_colors(text_widget.vbar, self.app.current_theme)

        # Also configure the horizontal scrollbar if it exists
        if hasattr(text_widget, 'hbar') and text_widget.hbar:
            configure_scrollbar_colors(text_widget.hbar, self.app.current_theme)

        # Button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=0, column=2, sticky='e')

        # Add button
        add_btn = ttk.Button(
            btn_frame,
            text='+',
            width=3,
            command=lambda: self.browse_and_append_dir(text_widget)
        )
        add_btn.grid(row=0, column=0, padx=(0, 5))
        self.app.add_tooltip(add_btn, 'Add a directory path')

        # Clear button
        clear_btn = ttk.Button(
            btn_frame,
            text='×',
            width=3,
            command=lambda: self.clear_text_widget(text_widget)
        )
        clear_btn.grid(row=0, column=1)
        self.app.add_tooltip(clear_btn, 'Clear all paths')

        # Store reference
        if driver_type == 'reference_driver':
            self.ref_driver_text = text_widget
            self.app.add_tooltip(text_widget, 'Path(s) to reference driver')

        else:
            self.dis_driver_text = text_widget
            self.app.add_tooltip(text_widget, 'Path(s) to distorted driver')

    def create_path_field(self, label_text, row, field_type):
        """Create application / dir path field"""
        frame = ttk.Frame(self.frame)
        frame.grid(row=row, column=0, sticky='ew', padx=10, pady=8)
        frame.grid_columnconfigure(1, weight=1)

        # Label
        lbl = ttk.Label(frame, padding=4, text=label_text, width=12, anchor='center')
        lbl.grid(row=0, column=0, padx=(0, 10), sticky='w')

        # Define type of field
        if field_type == 'file':
            self.app_entry = ttk.Entry(frame)
            self.app_entry.grid(row=0, column=1, sticky='ew', padx=(0, 10))
            self.app.add_tooltip(self.app_entry, 'Path to application executable')
            btn_tooltip_text = 'Select application executable'

        else:
            self.output_entry = ttk.Entry(frame)
            self.output_entry.grid(row=0, column=1, sticky='ew', padx=(0, 10))
            self.app.add_tooltip(self.output_entry, 'Path to output directory')
            btn_tooltip_text = 'Select output directory'

        # Browse button
        browse_btn = ttk.Button(
            frame,
            text='Browse',
            width=10,
            command=lambda: (
                self.browse_application()
                if field_type == 'file' else
                self.browse_output_directory()
            )
        )
        browse_btn.grid(row=0, column=2, sticky='e')
        self.app.add_tooltip(browse_btn,  btn_tooltip_text)

    def browse_and_append_dir(self, text_widget):
        """Open directory dialog and append selected directory path"""
        try:
            dir_path = filedialog.askdirectory(title='Select Driver Directory')
            if dir_path:
                # Get current content
                current_content = text_widget.get('1.0', 'end-1c').strip()

                # Append new path
                if current_content:
                    new_content = current_content + '\n' + dir_path
                else:
                    new_content = dir_path

                # Update text widget
                text_widget.configure(state='normal')
                text_widget.delete('1.0', 'end')
                text_widget.insert('1.0', new_content)
                text_widget.configure(state='normal')

        except Exception as e:
            log_message(self.app.log_section.log_area, f'Error selecting directory: {str(e)}', 'ERROR', self.app.current_theme)

    def clear_text_widget(self, text_widget):
        """Clear all content in a text widget"""
        text_widget.configure(state='normal')
        text_widget.delete('1.0', 'end')
        text_widget.configure(state='normal')

    def browse_application(self):
        """Open file dialog to select application executable"""
        try:
            file_path = filedialog.askopenfilename(
                title='Select Application Executable',
                filetypes=(
                    ('Executable files', '*.exe *.bin *.app'),
                    ('Script files', '*.sh')
                )
            )
            if file_path:
                self.app_entry.delete(0, tk.END)
                self.app_entry.insert(0, file_path)

        except Exception as e:
            log_message(self.app.log_section.log_area, f'Error selecting application: {str(e)}','ERROR', self.app.current_theme)

    def browse_output_directory(self):
        """Open directory dialog to select output directory and check permissions"""
        try:
            dir_path = filedialog.askdirectory(title='Select Output Directory')
            if dir_path:
                # Check if we can create a 'results' folder in the selected directory
                test_results_path = os.path.join(dir_path, 'results')
                try:
                    # Try to create a temporary directory to test permissions
                    if not os.path.exists(test_results_path):
                        os.makedirs(test_results_path, exist_ok=True)
                        # If successful, remove the test directory
                        os.rmdir(test_results_path)
                    else:
                        # Directory already exists, check if we can write to it
                        test_file = os.path.join(test_results_path, '.test_write')
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)

                    # If we get here, permissions are good
                    self.output_entry.delete(0, tk.END)
                    self.output_entry.insert(0, dir_path)
                    log_message(self.app.log_section.log_area, f'Output directory set: {dir_path}', 'INFO', self.app.current_theme)

                except (OSError, PermissionError) as e:
                    log_message(self.app.log_section.log_area, f'Cannot create output folder in {dir_path}: {str(e)}', 'ERROR', self.app.current_theme)
                    tk.messagebox.showerror('Permission Error', f'Cannot create output folder in the selected directory.\nPlease choose a directory where you have write permissions.')

        except Exception as e:
            log_message(self.app.log_section.log_area, f'Error selecting output directory: {str(e)}', 'ERROR', self.app.current_theme)

    def get_ref_dirs(self):
        """Get reference driver directories"""
        return [d.strip() for d in self.ref_driver_text.get('1.0', 'end-1c').splitlines() if d.strip()]

    def get_dis_dirs(self):
        """Get distorted driver directories"""
        return [d.strip() for d in self.dis_driver_text.get('1.0', 'end-1c').splitlines() if d.strip()]

    def get_app_path(self):
        """Get application path"""
        return self.app_entry.get().strip()

    def get_output_path(self):
        """Get output directory path"""
        return self.output_entry.get().strip()

    def validate(self):
        """Validate input fields"""
        ref_dirs = self.get_ref_dirs()
        dis_dirs = self.get_dis_dirs()
        app_path = self.get_app_path()
        output_path = self.get_output_path()

        if not ref_dirs:
            log_message(self.app.log_section.log_area, 'At least one reference driver directory is required', 'ERROR', self.app.current_theme)
            self.app.status_bar.set_status('Error: Reference driver missing')
            self.ref_driver_text.focus()
            tk.messagebox.showerror('Input Error', 'Please specify at least one reference driver directory')
            return False

        if not dis_dirs:
            log_message(self.app.log_section.log_area, 'At least one distorted driver directory is required', 'ERROR', self.app.current_theme)
            self.app.status_bar.set_status('Error: Distorted driver missing')
            self.dis_driver_text.focus()
            tk.messagebox.showerror('Input Error', 'Please specify at least one distorted driver directory')
            return False

        if not app_path:
            log_message(self.app.log_section.log_area, 'Application path is required', 'ERROR', self.app.current_theme)
            self.app.status_bar.set_status('Error: Application path missing')
            self.app_entry.focus()
            tk.messagebox.showerror('Input Error', 'Please specify the application executable path')
            return False

        elif not os.path.exists(app_path):
            log_message(self.app.log_section.log_area, f'Application path does not exist: {app_path}', 'ERROR', self.app.current_theme)
            self.app.status_bar.set_status('Error: Application not found')
            self.app_entry.focus()
            tk.messagebox.showerror('Input Error', 'The specified application executable does not exist')
            return False

        elif not os.access(app_path, os.X_OK):
            log_message(self.app.log_section.log_area, f'Application is not executable: {app_path}', 'ERROR', self.app.current_theme)
            self.app.status_bar.set_status('Error: Application not executable')
            self.app_entry.focus()
            tk.messagebox.showerror('Input Error', 'The specified application is not executable')
            return False

        if not output_path:
            log_message(self.app.log_section.log_area, 'Output directory is required', 'ERROR', self.app.current_theme)
            self.app.status_bar.set_status('Error: Output directory missing')
            self.output_entry.focus()
            tk.messagebox.showerror('Input Error', 'Please specify the output directory')
            return False

        elif not os.path.exists(output_path):
            log_message(self.app.log_section.log_area, f'Output directory does not exist: {output_path}', 'ERROR', self.app.current_theme)
            self.app.status_bar.set_status('Error: Output directory not found')
            self.output_entry.focus()
            tk.messagebox.showerror('Input Error', 'The specified output directory does not exist')
            return False

        elif not os.access(output_path, os.W_OK):
            log_message(self.app.log_section.log_area, f'Output directory is not writable: {output_path}', 'ERROR', self.app.current_theme)
            self.app.status_bar.set_status('Error: Output directory not writable')
            self.output_entry.focus()
            tk.messagebox.showerror('Input Error', 'The specified output directory is not writable')
            return False

        return True

    def reset(self):
        """Reset input fields"""
        self.ref_driver_text.configure(state='normal')
        self.ref_driver_text.delete('1.0', 'end')
        self.ref_driver_text.configure(state='normal')

        self.dis_driver_text.configure(state='normal')
        self.dis_driver_text.delete('1.0', 'end')
        self.dis_driver_text.configure(state='normal')

        self.app_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)

    def update_theme(self, theme):
        """Update theme colors"""
        # Update text widgets
        if hasattr(self, 'ref_driver_text'):
            configure_text_widget_theme(self.ref_driver_text, theme)
            configure_scrollbar_colors(self.ref_driver_text.vbar, theme)
            # Update horizontal scrollbar if it exists
            if hasattr(self.ref_driver_text, 'hbar') and self.ref_driver_text.hbar:
                configure_scrollbar_colors(self.ref_driver_text.hbar, theme)

        if hasattr(self, 'dis_driver_text'):
            configure_text_widget_theme(self.dis_driver_text, theme)
            configure_scrollbar_colors(self.dis_driver_text.vbar, theme)
            # Update horizontal scrollbar if it exists
            if hasattr(self.dis_driver_text, 'hbar') and self.dis_driver_text.hbar:
                configure_scrollbar_colors(self.dis_driver_text.hbar, theme)
