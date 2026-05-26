# New Modality Engine Addition: Visual Graphs Logger (src/visualizer.py)This script automatically saves visual diagnostic plots. It overlays the raw noisy sensor waveforms with the cleaned low-pass signals, allowing you to instantly inspect your automation pipeline's accuracy.

import os
import matplotlib
matplotlib.use('Agg') # Enforces non-interactive file writing generation background profile
import matplotlib.pyplot as plt

class DiagnosticVisualizer:
    @staticmethod
    def save_signal_comparison(raw_signal, clean_signal, asset_name, output_directory):
        """
        Generates and saves dual-trace timeline charts contrasting raw telemetry noise
        against the system's low-pass filtered mathematical output curves.
        """
        os.makedirs(output_directory, exist_ok=True)
        plt.figure(figsize=(10, 4))
        
        plt.plot(raw_signal, label="Raw Sensor Stream (Noisy)", color="orange", alpha=0.6, linewidth=1)
        plt.plot(clean_signal, label="Processed Data (Low-Pass Filtered)", color="darkblue", linewidth=1.5)
        
        plt.title(f"Signal Optimization Diagnostic Ledger: {asset_name}")
        plt.xlabel("Sample Timeline Indices (t)")
        plt.ylabel("Telemetry Amplitude Vector (g)")
        plt.legend(loc="upper right")
        plt.grid(True, linestyle="--", alpha=0.5)
        
        output_path = os.path.join(output_directory, f"{asset_name}_diagnostic_plot.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
