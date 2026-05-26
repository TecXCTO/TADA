"""

Final Master Program Orchestrator (main.py)This complete version brings everything together. It loads your raw files, applies filters, saves visual tracking charts, checks for errors, updates your spreadsheet, and fires automated warning emails directly to your inbox.
"""


import os
import yaml
import json
import numpy as np
import pandas as pd
import smtplib
from email.mime.text import MIMEText

from src.cad_parser import CADParser
from src.telemetry_annotator import TelemetryAnnotator
from src.thermal_vision import ThermalVisionAnnotator
from src.blueprint_parser import BlueprintParser
from src.kinematic_tracker import KinematicTracker
from src.data_cleaner import DataCleaner
from src.exporter import CSVExporter

# Integration of final advanced system additions
from src.visualizer import DiagnosticVisualizer

class UniversalPipelineManager:
    def __init__(self):
        self.output_dir = "./data/unified_labels"
        self.raw_dir = "./data/raw_ingest"
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open("config/threshold_rules.yaml", "r") as f:
            self.rules = yaml.safe_load(f)
            
        with open("config/alerts.yaml", "r") as f:
            self.alert_config = yaml.safe_load(f)
            
        self.cad_parser = CADParser(self.rules)
        self.telemetry_parser = TelemetryAnnotator(self.rules)
        self.thermal_parser = ThermalVisionAnnotator(self.rules)
        self.blueprint_parser = BlueprintParser(self.rules)
        self.kinematic_parser = KinematicTracker(self.rules)

    def dispatch_email_notification(self, asset_name, label):
        """
        SMTP Dispatcher: Automatically routes secure, encrypted notification 
        alerts to human supervisors when an asset trips an anomaly limit.
        """
        cfg = self.alert_config["email_alerts"]
        if not cfg["enabled"] or cfg["sender_password"] == "YOUR_APP_PASSWORD":
            return
            
        subject = f"🚨 [CRITICAL AI ALARM] - Anomaly Evaluated for {asset_name}"
        body = f"Attention Engineering Core,\n\nThe autonomous validation pipeline has flagged a critical operational variance.\n\nAsset ID: {asset_name}\nAssigned Classification: {label.upper()}\nStatus: Action Required. Inspect structural tolerances immediately."
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = cfg["sender_email"]
        msg["To"] = cfg["recipient_email"]
        
        try:
            with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
                server.starttls()
                server.login(cfg["sender_email"], cfg["sender_password"])
                server.sendmail(cfg["sender_email"], cfg["recipient_email"], msg.as_string())
            print(f"📧 Notification alert successfully sent to: {cfg['recipient_email']}")
        except Exception as e:
            print(f"❌ Failed to dispatch SMTP communication frame: {e}")

    def trigger_anomaly_alert(self, asset_name, label):
        alert_triggers = ["mechanical_anomaly_vibration_spike", "critical_thermal_hotspot_detected", "kinematic_jitter_anomaly"]
        if label in alert_triggers:
            print(f"\n🚨 [CRITICAL ANOMALY ALERT] Asset: {asset_name} evaluated as: [{label.upper()}]")
            self.dispatch_email_notification(asset_name, label)

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
                    df = pd.read_csv(relative_path)
                    col = df.select_dtypes(include=[np.number]).columns[0]
                    raw_sig = df[col].to_numpy().copy()
                    
                    for c in df.select_dtypes(include=[np.number]).columns:
                        df[c] = DataCleaner.filter_sensor_noise(df[c].to_numpy())
                    clean_sig = df[col].to_numpy()
                    
                    # Generate Diagnostic Visualizations
                    DiagnosticVisualizer.save_signal_comparison(raw_sig, clean_sig, asset_name, self.output_dir)
                    
                    temp_filtered_path = relative_path + ".filtered.csv"
                    df.to_csv(temp_filtered_path, index=False)
                    annotation = self.kinematic_parser.annotate(temp_filtered_path)
                    if os.path.exists(temp_filtered_path): os.remove(temp_filtered_path)
                        
                elif ext in ['.csv']:
                    df = pd.read_csv(relative_path)
                    col = df.select_dtypes(include=[np.number]).columns[0]
                    raw_sig = df[col].to_numpy().copy()
                    
                    for c in df.select_dtypes(include=[np.number]).columns:
                        df[c] = DataCleaner.filter_sensor_noise(df[c].to_numpy())
                    clean_sig = df[col].to_numpy()
                    
                    # Generate Diagnostic Visualizations
                    DiagnosticVisualizer.save_signal_comparison(raw_sig, clean_sig, asset_name, self.output_dir)
                    
                    temp_filtered_path = relative_path + ".filtered.csv"
                    df.to_csv(temp_filtered_path, index=False)
                    annotation = self.telemetry_parser.annotate(temp_filtered_path)
                    if os.path.exists(temp_filtered_path): os.remove(temp_filtered_path)
                        
                elif ext in ['.png', '.jpg', '.jpeg', '.tiff'] and 'thermal' in asset_name.lower():
                    cleaned_img = DataCleaner.clean_thermal_image(relative_path)
                    temp_img_path = relative_path + ".cleaned.jpg"
                    import cv2
                    cv2.imwrite(temp_img_path, cleaned_img)
                    annotation = self.thermal_parser.annotate(temp_img_path)
                    if os.path.exists(temp_img_path): os.remove(temp_img_path)
                        
                elif ext in ['.pdf', '.png', '.jpg', '.jpeg', '.dxf']:
                    annotation = self.blueprint_parser.annotate(relative_path)
                else:
                    continue
                
                self.trigger_anomaly_alert(asset_name, annotation.get("assigned_label"))
                master_manifest[asset_name] = annotation
                
                with open(os.path.join(self.output_dir, f"{asset_name}_annotation.json"), "w") as f:
                    json.dump(annotation, f, indent=4)
                    
            except Exception as e:
                print(f"❌ Pipeline fault on file {asset_name}: {str(e)}")

        with open(os.path.join(self.output_dir, "master_five_modality_manifest.json"), "w") as f:
            json.dump(master_manifest, f, indent=4)
            
        CSVExporter.convert_manifest_to_csv(master_manifest, self.output_dir)
        print("🏆 Universal Pipeline Execution Complete.")

if __name__ == "__main__":
    manager = UniversalPipelineManager()
    
    # Input Test Manifest
    my_assets = {
        "pump_housing_mesh": "./data/raw_ingest/cad_geometry/pump.stl",
        "turbine_bearing_vibration": "./data/raw_ingest/sensor_telemetry/bearing.csv",
        "motor_thermal_matrix": "./data/raw_ingest/thermal_vision/motor_thermal.jpg",
        "assembly_blueprint_sheet": "./data/raw_ingest/technical_blueprints/layout.pdf",
        "robotic_arm_kinematic_trajectory": "./data/raw_ingest/robotics/kinematic_path.csv"
    }
    
    manager.execute(my_assets)
      
