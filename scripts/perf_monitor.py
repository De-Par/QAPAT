"""
perf_monitor.py

A Python script to collect CPU and GPU performance metrics while replaying an
application trace with 'glretrace' from the apitrace suite.

This script:
1.  Captures an averaged 'before' snapshot of system metrics for a more
    accurate cold start comparison, with a configurable number of samples.
2.  Launches 'glretrace' to replay a specified trace file.
3.  Simultaneously monitors and collects detailed CPU, RAM, and GPU metrics,
    including FPS from the glretrace output.
4.  Automatically detects the GPU vendor (NVIDIA, AMD, Intel) to use the
    appropriate monitoring tool (`nvidia-smi`, sysfs, `intel_gpu_top`).
5.  Saves the time-series data into a structured CSV file for analysis.

Requirements:
- Python 3.6+
- psutil: `pip install psutil`
- apitrace suite (with 'glretrace' in the system's PATH).
- Vendor-specific GPU monitoring tools:
    - NVIDIA: `nvidia-smi` (comes with the driver).
    - AMD: Access to `/sys/class/drm/card*/device/` metrics.
    - Intel: `intel_gpu_top` (often in `intel-gpu-tools` package).

Usage:
    python perf_monitor.py --trace-file /path/to/your/trace.trace --output-file results.csv --interval 0.5 --cold-start-samples 10
"""

import argparse
import csv
import os
import subprocess
import threading
import time
import shutil
import re
import glob
from datetime import datetime
from collections import defaultdict

try:
    import psutil
except ImportError:
    print("Error: 'psutil' library not found. Please install it using: pip install psutil")
    exit(1)

# --- Configuration ---
# Define the headers for the output CSV file.
CSV_HEADERS = [
    "timestamp",
    "elapsed_time_s",
    "fps",
    "cpu_total_usage_percent",
    "cpu_load_avg_1m",
    "cpu_freq_current_mhz",
    "ram_usage_percent",
    "cpu_per_core_usage_percent",
    "gpu_usage_percent",
    "gpu_mem_used_mb",
    "gpu_power_draw_w",
    "gpu_temp_c"
]


class GpuMonitor:
    """A base class and factory for creating vendor-specific GPU monitors."""

    def __init__(self):
        self.vendor = "unknown"

    @staticmethod
    def detect():
        """Detects the GPU vendor and returns an appropriate monitor instance."""
        if shutil.which("nvidia-smi"):
            print("NVIDIA GPU detected.")
            return NvidiaGpuMonitor()
        if os.path.exists("/sys/module/i915"):
            if shutil.which("intel_gpu_top"):
                print("Intel GPU detected.")
                return IntelGpuMonitor()
            else:
                print("Warning: Intel GPU detected, but 'intel_gpu_top' is not installed or not in PATH.")

        if os.path.exists("/sys/class/drm/card0/device/vendor") and \
                any("amdgpu" in line for line in open("/sys/class/drm/card0/device/vendor", 'r')):
        #if os.path.exists("/sys/module/amdgpu"):
            print("AMD GPU detected. Using sysfs for monitoring.")
            return AmdGpuMonitor()

        print("Warning: Could not detect a supported GPU vendor. GPU metrics will be unavailable.")
        return GpuMonitor()

    def get_metrics(self):
        """Placeholder for getting metrics. Returns a dictionary with None values."""
        return {
            "gpu_usage_percent": None,
            "gpu_mem_used_mb": None,
            "gpu_power_draw_w": None,
            "gpu_temp_c": None
        }


class NvidiaGpuMonitor(GpuMonitor):
    """Monitors NVIDIA GPUs using the `nvidia-smi` command-line tool."""

    def __init__(self):
        super().__init__()
        self.vendor = "nvidia"
        self.command = [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,power.draw,temperature.gpu",
            "--format=csv,noheader,nounits"
        ]

    def get_metrics(self):
        try:
            result = subprocess.run(self.command, capture_output=True, text=True, check=True)
            values = [v.strip() for v in result.stdout.strip().split(',')]
            return {
                "gpu_usage_percent": float(values[0]),
                "gpu_mem_used_mb": float(values[1]),
                "gpu_power_draw_w": float(values[2]) if "N/A" not in values[2] else None,
                "gpu_temp_c": float(values[3])
            }
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError) as e:
            print(f"Error collecting NVIDIA metrics: {e}")
            return super().get_metrics()


class AmdGpuMonitor(GpuMonitor):
    """Monitors AMD GPUs by reading values directly from sysfs."""

    def __init__(self, card_index=0):
        super().__init__()
        self.vendor = "amd"
        self.card_path = f"/sys/class/drm/card{card_index}/device"
        print(f"Monitoring AMD GPU at: {self.card_path}")
        if not os.path.exists(self.card_path):
            raise FileNotFoundError(f"AMD GPU sysfs path does not exist: {self.card_path}")

    def _read_sysfs(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return f.read().strip()
        except (IOError, FileNotFoundError) as e:
            if not hasattr(self, f"_warned_{os.path.basename(file_path)}"):
                print(f"Warning: Could not read AMD sysfs file '{file_path}': {e}")
                setattr(self, f"_warned_{os.path.basename(file_path)}", True)
            return None

    def get_metrics(self):
        busy_percent = self._read_sysfs(os.path.join(self.card_path, "gpu_busy_percent"))
        vram_used = self._read_sysfs(os.path.join(self.card_path, "mem_info_vram_used"))
        mem_used_mb = (int(vram_used) / (1024 * 1024)) if vram_used else None
        power_draw = self._read_sysfs(os.path.join(self.card_path, "power1_average"))
        power_w = (int(power_draw) / 1_000_000) if power_draw else None
        temp = None
        temp_files = glob.glob(os.path.join(self.card_path, "hwmon/hwmon*/temp1_input"))
        if temp_files:
            temp = self._read_sysfs(temp_files[0])
        temp_c = (int(temp) / 1000) if temp else None

        return {
            "gpu_usage_percent": float(busy_percent) if busy_percent else None,
            "gpu_mem_used_mb": mem_used_mb,
            "gpu_power_draw_w": power_w,
            "gpu_temp_c": temp_c
        }


class IntelGpuMonitor(GpuMonitor):
    """Monitors Intel GPUs using `intel_gpu_top`."""

    def __init__(self):
        super().__init__()
        self.vendor = "intel"
        print("Warning: Intel GPU monitoring is basic.")

    def get_metrics(self):
        try:
            result = subprocess.run(
                ["intel_gpu_top", "-s", "100", "-n", "1", "-o", "-"],
                capture_output=True, text=True, check=True
            )
            usage = None
            for line in result.stdout.splitlines():
                if "Render/3D" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "Render/3D" and i + 2 < len(parts):
                            usage = float(parts[i + 2].replace('%', ''))
                            break
            return {"gpu_usage_percent": usage, "gpu_mem_used_mb": None, "gpu_power_draw_w": None, "gpu_temp_c": None}
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError) as e:
            print(f"Error collecting Intel metrics: {e}")
            return super().get_metrics()


class SystemMonitor:
    """Handles the monitoring thread and data collection."""

    def __init__(self, interval_sec):
        self.interval_sec = interval_sec
        self.is_running = False
        self._thread = None
        self.collected_data = []
        self.start_time = None
        self.gpu_monitor = GpuMonitor.detect()
        self.current_fps = 0
        self.fps_lock = threading.Lock()

    def update_fps(self, new_fps):
        """Thread-safe method to update the current FPS value."""
        with self.fps_lock:
            self.current_fps = new_fps

    def _monitor_loop(self):
        self.start_time = time.monotonic()
        while self.is_running:
            loop_start_time = time.monotonic()

            row = self.get_snapshot()
            row["elapsed_time_s"] = round(loop_start_time - self.start_time, 4)
            with self.fps_lock:
                row["fps"] = self.current_fps

            self.collected_data.append(row)

            loop_duration = time.monotonic() - loop_start_time
            sleep_time = self.interval_sec - loop_duration
            if sleep_time > 0:
                time.sleep(sleep_time)

    def get_snapshot(self):
        """Collects and returns a single snapshot of system metrics."""
        psutil.cpu_percent(interval=None)  # Prime the pump
        time.sleep(0.1)  # Short delay for a valid reading

        cpu_total = psutil.cpu_percent(interval=None)
        cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
        cpu_freq = psutil.cpu_freq()
        ram_percent = psutil.virtual_memory().percent
        load_avg = psutil.getloadavg()
        gpu_metrics = self.gpu_monitor.get_metrics()

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_total_usage_percent": cpu_total,
            "cpu_load_avg_1m": load_avg[0],
            "cpu_freq_current_mhz": cpu_freq.current if cpu_freq else None,
            "ram_usage_percent": ram_percent,
            "cpu_per_core_usage_percent": ','.join(map(str, cpu_per_core)),
            **gpu_metrics
        }

    def start(self):
        if self._thread is not None: return
        print(f"Starting system monitor with a {self.interval_sec}s interval.")
        self.is_running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.is_running: return
        print("Stopping system monitor...")
        self.is_running = False
        self._thread.join()
        print("Monitor stopped.")
        self._thread = None

    def fill_final_fps(self):
        last_valid_fps = None or self.current_fps
        # Find the last non-zero FPS value
        for row in reversed(self.collected_data):
            if row["fps"] > 0:
                last_valid_fps = row["fps"]
                break
        if last_valid_fps is not None:
            # Apply to all subsequent snapshots
            for row in self.collected_data:
                if row["fps"] == 0:
                    row["fps"] = last_valid_fps


def get_averaged_snapshot(snapshots):
    avg_snapshot = defaultdict(float)
    valid_counts = defaultdict(int)

    for snap in snapshots:
        for key, value in snap.items():
            if isinstance(value, (int, float)):
                avg_snapshot[key] += value
                valid_counts[key] += 1

    for key, total in avg_snapshot.items():
        if valid_counts[key] > 0:
            avg_snapshot[key] = total / valid_counts[key]

    return dict(avg_snapshot)


def gen_averaged_snapshot(monitor, num_samples=5, delay=0.2):
    """Collects multiple snapshots and averages the results for stability."""
    print(f"Collecting {num_samples} samples for stable baseline...")
    snapshots = []
    for i in range(num_samples):
        print(f"  ...sample {i + 1}/{num_samples}")
        snapshots.append(monitor.get_snapshot())
        time.sleep(delay)

    avg_snapshot = get_averaged_snapshot(snapshots)
    return avg_snapshot


def log_glretrace_output(stdout, monitor):
    """Reads glretrace stdout, prints it, and parses for FPS."""
    fps_pattern = re.compile(r'(\d+\.?\d*)\s*fps')
    # The `iter(stdout.readline, '')` loop reads the process output line by line
    # as it becomes available, which is crucial for real-time FPS tracking.
    for line in iter(stdout.readline, ''):
        line = line.strip()
        print(f"[glretrace] {line}")
        match = fps_pattern.search(line)
        if match:
            try:
                fps = float(match.group(1))
                monitor.update_fps(fps)
            except (ValueError, IndexError):
                pass  # Ignore parsing errors
    stdout.close()


def write_csv(data, output_file):
    """Writes the collected data to a CSV file."""
    if not data:
        print("No data collected. CSV file not created.")
        return
    print(f"Writing {len(data)} data points to '{output_file}'...")
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(data)
        print("Successfully wrote CSV file.")
    except IOError as e:
        print(f"Error writing to CSV file '{output_file}': {e}")


def print_summary(before, after):
    """Prints a summary comparing before and after metric snapshots."""
    print(f"\n{'Metric':<25} | {'Before':>10} | {'After':>10} | {'Delta':>10}")
    print("-"*65)

    for key in ["gpu_mem_used_mb", "gpu_power_draw_w", "gpu_temp_c", "ram_usage_percent", "cpu_load_avg_1m"]:
        before_val = before.get(key)
        after_val = after.get(key)

        before_str = f"{before_val:.3f}" if isinstance(before_val, (int, float)) else "N/A"
        after_str = f"{after_val:.3f}" if isinstance(after_val, (int, float)) else "N/A"

        delta_str = "N/A"
        if isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
            delta_str = f"{after_val - before_val:+.3f}"

        print(f"{key:<25} | {before_str:>10} | {after_str:>10} | {delta_str:>10}")
    print("-"*65)


def main():
    parser = argparse.ArgumentParser(description="Monitor system metrics during glretrace replay.")
    parser.add_argument("-t", "--trace-file", required=True, help="Path to the apitrace file.")
    parser.add_argument("-o", "--output-file", default="performance_metrics.csv", help="Name of the output CSV file.")
    parser.add_argument("-i", "--interval", type=float, default=0.5, help="Sampling interval in seconds.")
    parser.add_argument("--cold-start-samples", type=int, default=10, help="Number of samples to average for the 'before' cold start snapshot.")
    args = parser.parse_args()

    if not os.path.exists(args.trace_file):
        print(f"Error: Trace file not found at '{args.trace_file}'")
        exit(1)
    if not shutil.which("glretrace"):
        print("Error: 'glretrace' not found. Make sure apitrace is in your PATH.")
        exit(1)

    monitor = SystemMonitor(interval_sec=args.interval)
    before_metrics = gen_averaged_snapshot(monitor, num_samples=args.cold_start_samples, delay=args.interval)

    monitor.start()
    glretrace_command = ["glretrace", "-b", args.trace_file]
    print(f"\nExecuting command: {' '.join(glretrace_command)}")
    print("Replaying trace...")

    process = None
    fps_thread = None
    try:
            # FIX: Launch the subprocess with line buffering (bufsize=1) and text mode.
            # This prevents stdout from being buffered, ensuring FPS is read in real-time.
        process = subprocess.Popen(
            glretrace_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='ignore'
        )
        fps_thread = threading.Thread(target=log_glretrace_output, args=(process.stdout, monitor), daemon=True)
        fps_thread.start()
        process.wait()  # Wait for the subprocess to finish

        if process.returncode != 0:
            print("\n--- glretrace finished with an error ---")
        else:
            print("\n--- glretrace finished successfully ---")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Stopping...")
        if process: process.terminate()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if process: process.wait()
        if fps_thread: fps_thread.join(timeout=3)
        monitor.stop()
        monitor.fill_final_fps()
        write_csv(monitor.collected_data, args.output_file)

        after_metrics = get_averaged_snapshot(monitor.collected_data)
        print_summary(before_metrics, after_metrics)


if __name__ == "__main__":
    main()
