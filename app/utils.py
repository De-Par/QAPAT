import os
import time
import random
from datetime import datetime
import tkinter as tk


def configure_scrollbar_colors(scrollbar, theme):
    """Configure scrollbar colors to match theme"""
    scrollbar.configure(
        background=theme['scrollbar_bg'],
        troughcolor=theme['scrollbar_bg'],
        activebackground=theme['scrollbar_active']
    )


def configure_text_widget_theme(text_widget, theme):
    """Configure text widget colors to match theme"""
    text_widget.configure(
        bg=theme['text_widget_bg'],
        fg=theme['text_widget_fg'],
        insertbackground=theme['text_widget_fg'],
        selectbackground=theme['text_widget_selection'],
        highlightcolor=theme['text_widget_highlight'],
        highlightbackground=theme['border']
    )


def log_message(log_area, message, level='INFO', theme=None):
    """Append message to log area with color coding"""
    log_area.configure(state='normal')

    # Get current timestamp
    timestamp = datetime.now().strftime('%H:%M:%S')

    # Get color based on level and theme
    if level == 'INFO':
        tag = 'info'
        prefix = '[INFO]'
        color = theme['info_color'] if theme else "#0072C6"

    elif level == 'WARNING':
        tag = 'warning'
        prefix = '[WARN]'
        color = theme['warning_color'] if theme else "#D67F00"

    elif level == 'ERROR':
        tag = 'error'
        prefix = '[ERROR]'
        color = theme['error_color'] if theme else "#C00000"

    else:
        tag = 'debug'
        prefix = '[DEBUG]'
        color = "#555555"

    # Configure tag
    log_area.tag_configure(tag, foreground=color)

    # Insert message
    log_area.insert(tk.END, f"{timestamp} {prefix} ", tag)
    log_area.insert(tk.END, f"{message}\n")

    log_area.configure(state='disabled')
    log_area.see(tk.END)  # Auto-scroll to bottom


def _queue_log_message(log_queue, message, level, theme):
    """Helper function to queue log messages"""
    log_queue.put({'message': message, 'level': level, 'theme': theme})


def run_analysis(
        log_queue, status_var, ref_dirs, dis_dirs, app_path, output_path,
        options, delay_time, bench_time, theme, enable_buttons_callback
):
    """Simulate the analysis process with driver directories and application"""
    try:
        # Apply delay time if specified
        if delay_time > 0:
            _queue_log_message(log_queue, f"Waiting {delay_time} seconds before starting analysis...", 'INFO', theme)
            time.sleep(delay_time)
        
        # Simulate processing steps
        _queue_log_message(log_queue, 'Initializing driver directories...', 'INFO', theme)
        time.sleep(0.5)

        # Verify driver directories
        for path in ref_dirs:
            if not os.path.exists(path):
                _queue_log_message(log_queue, f"Reference driver directory not found: {path}", 'ERROR', theme)
            else:
                _queue_log_message(log_queue, f"Using reference driver: {path}", 'INFO', theme)

        for path in dis_dirs:
            if not os.path.exists(path):
                _queue_log_message(log_queue, f"Distorted driver directory not found: {path}", 'ERROR', theme)
            else:
                _queue_log_message(log_queue, f"Using distorted driver: {path}", 'INFO', theme)

        # Verify application
        if not os.path.exists(app_path):
            _queue_log_message(log_queue, f"Application not found: {app_path}", 'ERROR', theme)
            return

        elif not os.access(app_path, os.X_OK):
            # On macOS, check if file is executable by checking permissions
            if hasattr(os, 'stat') and hasattr(os.stat(app_path), 'st_mode'):
                import stat
                if not (os.stat(app_path).st_mode & stat.S_IXUSR):
                    _queue_log_message(log_queue, f"Application not executable: {app_path}", 'ERROR', theme)
                    return
            else:
                _queue_log_message(log_queue, f"Application not executable: {app_path}", 'ERROR', theme)
                return

        _queue_log_message(log_queue, f"Launching application: {os.path.basename(app_path)}", 'INFO', theme)
        time.sleep(1)

        # Verify output directory
        if not os.path.exists(output_path):
            _queue_log_message(log_queue, f"Output directory not found: {output_path}", 'ERROR', theme)
            return

        elif not os.access(output_path, os.W_OK):
            _queue_log_message(log_queue, f"Output directory not writable: {output_path}", 'ERROR', theme)
            return

        else:
            _queue_log_message(log_queue, f"Using output directory: {output_path}", 'INFO', theme)

        # Create results directory
        results_dir = os.path.join(output_path, 'results')
        try:
            os.makedirs(results_dir, exist_ok=True)
            _queue_log_message(log_queue, f"Results directory ready: {results_dir}", 'INFO', theme)

        except Exception as e:
            _queue_log_message(log_queue, f"Cannot create results directory: {str(e)}", 'ERROR', theme)
            return

        # Simulate analysis steps
        _queue_log_message(log_queue, 'Loading reference drivers...', 'INFO', theme)
        time.sleep(1)

        _queue_log_message(log_queue, 'Loading distorted drivers...', 'INFO', theme)
        time.sleep(1)

        _queue_log_message(log_queue, 'Calculating quality metrics...', 'INFO', theme)
        for i in range(1, 6):
            time.sleep(0.5)
            _queue_log_message(log_queue, f"Metric {i}/5 calculated", 'INFO', theme)

        # Apply bench time if specified
        if bench_time > 0:
            _queue_log_message(log_queue, f"Running benchmark for {bench_time} seconds...", 'INFO', theme)
            time.sleep(bench_time)
            _queue_log_message(log_queue, 'Benchmark completed', 'INFO', theme)

        # Process selected options
        if 'report' in options:
            _queue_log_message(log_queue, 'Generating report...', 'INFO', theme)
            time.sleep(1.5)
            _queue_log_message(log_queue, 'Report generated successfully', 'INFO', theme)

        if 'plot' in options:
            _queue_log_message(log_queue, 'Creating visualizations...', 'INFO', theme)
            time.sleep(1.2)
            _queue_log_message(log_queue, 'Visualizations created', 'INFO', theme)
            # Generate sample plot...

        if 'merge' in options:
            _queue_log_message(log_queue, 'Merging results...', 'INFO', theme)
            time.sleep(0.8)
            _queue_log_message(log_queue, 'Results merged', 'INFO', theme)

        if 'export' in options:
            _queue_log_message(log_queue, 'Exporting to CSV...', 'INFO', theme)
            time.sleep(1.0)
            _queue_log_message(log_queue, 'Export completed', 'INFO', theme)

        # Generate random quality score
        score = round(random.uniform(0.75, 0.99), 3)
        _queue_log_message(log_queue, f"Analysis complete! Quality score: {score}", 'INFO', theme)
        status_var.set(f"Analysis complete - Quality: {score}")

    except Exception as e:
        _queue_log_message(log_queue, f"Processing error: {str(e)}", 'ERROR', theme)
        status_var.set('Error during processing')

    finally:
        # Re-enable buttons
        enable_buttons_callback()
