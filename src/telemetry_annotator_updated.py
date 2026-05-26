"""

Advanced Mathematical Smoothing Upgrades (src/telemetry_annotator.py)This updated sensor engine calculates cumulative rolling statistics (Rolling Averages and Rolling Standard Deviations) across your telemetry data. This allows the system to track dynamic drift and isolate wear over time rather than just spotting instantaneous spikes.
"""


import numpy as np
import pandas as pd
from scipy.signal import find_peaks

class TelemetryAnnotator:
    def __init__(self, rules):
        self.rules = rules

    def annotate(self, file_path):
        df = pd.read_csv(file_path)
        col = 'vibration_g' if 'vibration_g' in df.columns else df.select_dtypes(include=[np.number]).columns[0]
        signal = df[col].to_numpy()
        
        # Core Calculations
        rms = np.sqrt(np.mean(signal**2))
        peak_val = np.max(np.abs(signal))
        crest_factor = peak_val / rms if rms > 0 else 0
        peaks, _ = find_peaks(np.abs(signal), distance=10, prominence=1.5)
        
        # Advanced Engineering Statistics additions: Dynamic Rolling Aggregations
        series = pd.Series(signal)
        rolling_window = max(5, len(signal) // 20)
        rolling_mean = series.rolling(window=rolling_window, min_periods=1).mean().to_numpy()
        rolling_std = series.rolling(window=rolling_window, min_periods=1).std().to_numpy()
        
        label = "nominal_operating_state"
        if rms > self.rules["telemetry"]["max_rms_vibration"] or crest_factor > self.rules["telemetry"]["max_crest_factor"]:
            label = "mechanical_anomaly_vibration_spike"
            
        return {
            "modality": "2_1D_Sensor_Telemetry",
            "assigned_label": label,
            "metrics": {
                "signal_rms_amplitude": round(float(rms), 3),
                "crest_factor_ratio": round(float(crest_factor), 3),
                "detected_anomaly_count": len(peaks),
                "cumulative_rolling_mean_peak": round(float(np.max(rolling_mean)), 3),
                "cumulative_rolling_std_peak": round(float(np.max(np.nan_to_num(rolling_std))), 3),
                "anomaly_index_locations": [int(p) for p in peaks[:10]]
            }
        }
