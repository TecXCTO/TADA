"""

Updated Application Orchestrator (main.py)This updated version imports your cleanup and export scripts, runs the noise cleaning filters, triggers on-screen warning signs if any system registers a fault, and builds your finished CSV table.
"""


import os
import yaml
import json
import numpy as np
import pandas as pd

from src.cad_parser import CADParser
from src.telemetry_annotator import TelemetryAnnotator
from src.thermal_vision import ThermalVisionAnnotator
from src.blueprint_parser import BlueprintParser
from src.kinematic_tracker import KinematicTracker

# New architectural pipeline additions
from src.data_cleaner import DataCleaner
from src.exporter import CSVExporter

class UniversalPipelineManager:
    def __init__(self):
        self.output_dir = "./data/unified_labels"
        self.raw_dir = "./data/raw_ingest"
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open("config/threshold_rules.yaml", "r") as f:
            self.rules = yaml.safe_load(f)
            
        self.cad_parser = CADParser(self.rules)
        self.telemetry_parser = TelemetryAnnotator(self.rules)
        self.thermal_parser = ThermalVisionAnnotator(self.rules)
        self.blueprint_parser = BlueprintParser(self.rules)
        self.kinematic_parser = KinematicTracker(self.rules)

    def trigger_anomaly_alert(self, asset_name, label):
        """
        Active monitoring notification module that automatically flags 
        hazardous operational engineering failures instantly to the console terminal.
        """
        alert_triggers = ["mechanical_anomaly_vibration_spike", "critical_thermal_hotspot_detected", "kinematic_jitter_anomaly"]
        if label in alert_triggers:
            print(f"\n🚨 [CRITICAL ANOMALY ALERT] Asset: {asset_name} evaluated as: [{label.upper()}]")
            print("   ⚠️ Action Required: Inspect physical hardware system limitations immediately.\n")

    def execute(self, manifest):
        master_manifest = {}
        
        for asset_name, relative_path in manifest.items():
            if not os.path.exists(relative_path):
                print(f"⚠️ Data mismatch - Not Found: {relative_path}")
                continue
                
            ext = os.path.splitext(relative_path)[-1].lower()
            print(f"🔄 Processing: {asset_name} ({ext})...")
            
            try:
                if ext in ['.stl', '.obj', '.ply']:
                    annotation = self.cad_parser.annotate(relative_path)
                    
                elif ext in ['.csv'] and 'kinematic' in asset_name.lower():
                    # Step 1: Filter raw kinematics sensor path tracking lines
                    df = pd.read_csv(relative_path)
                    for col in df.select_dtypes(include=[np.number]).columns:
                        df[col] = DataCleaner.filter_sensor_noise(df[col].to_numpy())
                    # Temporarily cache filtered data file array link
                    temp_filtered_path = relative_path + ".filtered.csv"
                    df.to_csv(temp_filtered_path, index=False)
                    
                    annotation = self.kinematic_parser.annotate(temp_filtered_path)
                    if os.path.exists(temp_filtered_path):
                        os.remove(temp_filtered_path)
                        
                elif ext in ['.csv']:
                    # Step 1: Clean telemetry accelerometer noise peaks
                    df = pd.read_csv(relative_path)
                    for col in df.select_dtypes(include=[np.number]).columns:
                        df[col] = DataCleaner.filter_sensor_noise(df[col].to_numpy())
                    temp_filtered_path = relative_path + ".filtered.csv"
                    df.to_csv(temp_filtered_path, index=False)
                    
                    annotation = self.telemetry_parser.annotate(temp_filtered_path)
                    if os.path.exists(temp_filtered_path):
                        os.remove(temp_filtered_path)
                        
                elif ext in ['.png', '.jpg', '.jpeg', '.tiff'] and 'thermal' in asset_name.lower():
                    # Step 1: Smooth image pixel distributions via Gaussian filters
                    cleaned_img = DataCleaner.clean_thermal_image(relative_path)
                    temp_img_path = relative_path + ".cleaned.jpg"
                    import cv2
                    cv2.imwrite(temp_img_path, cleaned_img)
                    
                    annotation = self.thermal_parser.annotate(temp_img_path)
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                        
                elif ext in ['.pdf', '.png', '.jpg', '.jpeg', '.dxf']:
                    annotation = self.blueprint_parser.annotate(relative_path)
                else:
                    continue
                
                # Active Notification Guard Check
                self.trigger_anomaly_alert(asset_name, annotation.get("assigned_label"))
                
                master_manifest[asset_name] = annotation
                
                with open(os.path.join(self.output_dir, f"{asset_name}_annotation.json"), "w") as f:
                    json.dump(annotation, f, indent=4)
                    
            except Exception as e:
                print(f"❌ Automation pipeline bypassed file {asset_name}: {str(e)}")

        # Output the master dataset JSON registry ledger
        with open(os.path.join(self.output_dir, "master_five_modality_manifest.json"), "w") as f:
            json.dump(master_manifest, f, indent=4)
            
        # Compile dynamic flat tabular CSV database output file completely hands-free
        CSVExporter.convert_manifest_to_csv(master_manifest, self.output_dir)
        print("🏆 All mechanical engineering domains successfully auto-annotated.")

if __name__ == "__main__":
    for folder in ["cad_geometry", "sensor_telemetry", "thermal_vision", "technical_blueprints", "robotics"]:
        os.makedirs(f"./data/raw_ingest/{folder}", exist_ok=True)
        
    my_assets = {
        "pump_housing_mesh": "./data/raw_ingest/cad_geometry/pump.stl",
        "turbine_bearing_vibration": "./data/raw_ingest/sensor_telemetry/bearing.csv",
        "motor_thermal_matrix": "./data/raw_ingest/thermal_vision/motor_thermal.jpg",
        "assembly_blueprint_sheet": "./data/raw_ingest/technical_blueprints/layout.pdf",
        "robotic_arm_kinematic_trajectory": "./data/raw_ingest/robotics/kinematic_path.csv"
    }
    
    manager = UniversalPipelineManager()
    manager.execute(my_assets)
                                                                           
