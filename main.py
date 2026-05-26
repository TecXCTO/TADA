# Single command-line trigger to parse all data

# Application entry point to execute bulk pipelines
"""
Master Framework Pipeline Pipeline Runner (main.py)The system orchestrator. It imports your modular scripts, handles rule routing, and builds the database completely hands-free.
"""
import os
import yaml
import json

from src.cad_parser import CADParser
from src.telemetry_annotator import TelemetryAnnotator
from src.thermal_vision import ThermalVisionAnnotator
from src.blueprint_parser import BlueprintParser
from src.kinematic_tracker import KinematicTracker

class UniversalPipelineManager:
    def __init__(self):
        # Establish structural pipeline directories
        self.output_dir = "./data/unified_labels"
        self.raw_dir = "./data/raw_ingest"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load configuration thresholds safely
        with open("config/threshold_rules.yaml", "r") as f:
            self.rules = yaml.safe_load(f)
            
        # Initialize engineering sub-systems
        self.cad_parser = CADParser(self.rules)
        self.telemetry_parser = TelemetryAnnotator(self.rules)
        self.thermal_parser = ThermalVisionAnnotator(self.rules)
        self.blueprint_parser = BlueprintParser(self.rules)
        self.kinematic_parser = KinematicTracker(self.rules)

    def execute(self, manifest):
        master_manifest = {}
        
        for asset_name, relative_path in manifest.items():
            if not os.path.exists(relative_path):
                print(f"⚠️ Data mismatch - Not Found: {relative_path}")
                continue
                
            ext = os.path.splitext(relative_path)[-1].lower()
            print(f"🔄 Processing: {asset_name} ({ext})...")
            
            if ext in ['.stl', '.obj', '.ply']:
                annotation = self.cad_parser.annotate(relative_path)
            elif ext in ['.csv'] and 'kinematic' in asset_name.lower():
                annotation = self.kinematic_parser.annotate(relative_path)
            elif ext in ['.csv']:
                annotation = self.telemetry_parser.annotate(relative_path)
            elif ext in ['.png', '.jpg', '.jpeg', '.tiff'] and 'thermal' in asset_name.lower():
                annotation = self.thermal_parser.annotate(relative_path)
            elif ext in ['.pdf', '.png', '.jpg', '.jpeg', '.dxf']:
                annotation = self.blueprint_parser.annotate(relative_path)
            else:
                continue
                
            master_manifest[asset_name] = annotation
            
            # Export individual label file matching data source name
            with open(os.path.join(self.output_dir, f"{asset_name}_annotation.json"), "w") as f:
                json.dump(annotation, f, indent=4)

        # Output the master dataset training manifest ledger
        with open(os.path.join(self.output_dir, "master_five_modality_manifest.json"), "w") as f:
            json.dump(master_manifest, f, indent=4)
        print("🏆 All mechanical engineering domains successfully auto-annotated.")

if __name__ == "__main__":
    # Create production directory tree template instantly
    for folder in ["cad_geometry", "sensor_telemetry", "thermal_vision", "technical_blueprints", "robotics"]:
        os.makedirs(f"./data/raw_ingest/{folder}", exist_ok=True)
        
    # Input Dataset Manifest Registry
    my_assets = {
        "pump_housing_mesh": "./data/raw_ingest/cad_geometry/pump.stl",
        "turbine_bearing_vibration": "./data/raw_ingest/sensor_telemetry/bearing.csv",
        "motor_thermal_matrix": "./data/raw_ingest/thermal_vision/motor_thermal.jpg",
        "assembly_blueprint_sheet": "./data/raw_ingest/technical_blueprints/layout.pdf",
        "robotic_arm_kinematic_trajectory": "./data/raw_ingest/robotics/kinematic_path.csv"
    }
    
    manager = UniversalPipelineManager()
    manager.execute(my_assets)
                      
