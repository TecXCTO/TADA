# Processes frequency bands and isolates faults
"""
Modality 2 Engine (src/telemetry_annotator.py)Processes time-series sensor logs (.csv) using statistical wave analysis to find structural faults.
"""


import numpy as np
import pandas as pd
from scipy.signal import find_peaks

class TelemetryAnnotator:
    def __init__(self, rules):
        self.rules = rules

    def annotate(self, file_path):
        df = pd.read_csv(file_path)
        col = 'vibration_g' if 'vibration_g' in df.columns else df.select_dtypes(include=[np.number]).columns
        signal = df[col].to_numpy()
        
        rms = np.sqrt(np.mean(signal**2))
        peak_val = np.max(np.abs(signal))
        crest_factor = peak_val / rms if rms > 0 else 0
        peaks, _ = find_peaks(np.abs(signal), distance=10, prominence=1.5)
        
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
                "anomaly_index_locations": [int(p) for p in peaks[:10]]
            }
        }
      
