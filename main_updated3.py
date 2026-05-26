"""
Updated Application Orchestrator (main.py)This core tracking file hooks into the upgraded geometry parser, manages loop structures across your data storage arrays, and ensures your metadata outputs update smoothly.
"""
import os
import yaml
import json

from src.cad_parser import AdvancedCADParser
from src.telemetry_annotator import TelemetryAnnotator
from src.thermal_vision import ThermalVisionAnnotator
from src.blueprint_parser import BlueprintParser
from src.kinematic_tracker import KinematicTracker
from src.exporter import CSVExporter

class UnifiedPipelineManager:
    def __init__(self):
        self.output_dir = "./data/unified_labels"
        self.raw_dir = "./data/raw_ingest"
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open("config/threshold_rules.yaml", "r") as f:
            self.rules = yaml.safe_load(f)
            
        # Initialize upgraded parser engine
        self.cad_parser = AdvancedCADParser(self.rules)
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
            
            try:
                if ext in ['.stl', '.obj', '.ply']:
                    # Trigger the dual-mode segmentation, sub-feature extractor, and snapshot render engine
                    annotation = self.cad_parser.annotate_cad_data(relative_path, asset_name)
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
                
                # Export individual hierarchical JSON data notations
                with open(os.path.join(self.output_dir, f"{asset_name}_annotation.json"), "w") as f:
                    json.dump(annotation, f, indent=4)
                    
            except Exception as e:
                print(f"❌ Automation pipeline fault on file {asset_name}: {str(e)}")

        # Save primary structural master archive JSON ledger
        with open(os.path.join(self.output_dir, "master_five_modality_manifest.json"), "w") as f:
            json.dump(master_manifest, f, indent=4)
            
        # Flatten all classifications, features, and segments into a tabular CSV table
        CSVExporter.convert_manifest_to_csv(master_manifest, self.output_dir)
        print("🏆 Universal Pipeline Execution Complete.")

if __name__ == "__main__":
    # Ensure raw directory tree pathways match configuration targets
    for folder in ["cad_geometry", "sensor_telemetry", "thermal_vision", "technical_blueprints", "robotics", "cad_snapshots"]:
        os.makedirs(f"./data/raw_ingest/{folder}", exist_ok=True)
        
    my_assets = {
        "pump_housing_assembly_mesh": "./data/raw_ingest/cad_geometry/pump.stl",
        "turbine_bearing_vibration": "./data/raw_ingest/sensor_telemetry/bearing.csv",
        "motor_thermal_matrix": "./data/raw_ingest/thermal_vision/motor_thermal.jpg",
        "assembly_blueprint_sheet": "./data/raw_ingest/technical_blueprints/layout.pdf",
        "robotic_arm_kinematic_trajectory": "./data/raw_ingest/robotics/kinematic_path.csv"
    }
    
    manager = UnifiedPipelineManager()
    manager.execute(my_assets)
