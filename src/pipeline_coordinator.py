# Master entry engine mapping multi-modal streams

# The Five-Modality Automation Script

import os
import json
import numpy as np
import pandas as pd
import cv2
import trimesh
from scipy.signal import find_peaks
import pypdf

class FiveModalityMechanicalAnnotator:
    def __init__(self, output_dir="./data/unified_labels"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def annotate_3d_cad(self, file_path):
        """
        MODALITY 1: 3D CAD Geometry & Mesh Processing
        Extracts volumetric, aspect ratios, and bounding dimensions.
        """
        mesh = trimesh.load(file_path)
        volume = float(mesh.volume)
        extents = sorted([float(x) for x in mesh.extents])
        aspect_ratio = extents[-1] / extents[0] if extents[0] > 0 else 1
        
        label = "custom_machined_component"
        if aspect_ratio > 3.0:
            label = "transmission_shaft_axis"
        elif extents[0] < 5.0:
            label = "sheet_metal_plate"
            
        return {
            "modality": "1_3D_CAD_Geometry",
            "assigned_label": label,
            "metrics": {
                "volume_mm3": round(volume, 2),
                "surface_area_mm2": round(float(mesh.area), 2),
                "bounding_box_lwh": [round(x, 2) for x in extents],
                "vertex_count": len(mesh.vertices)
            }
        }

    def annotate_sensor_telemetry(self, file_path):
        """
        MODALITY 2: 1D Sensor Signal Logs (Vibration, Temperature, Pressure)
        Calculates Root-Mean-Square (RMS) and isolates high-frequency damage peaks.
        """
        df = pd.read_csv(file_path)
        # Fallback to the first numerical column if 'vibration_g' label is missing
        col = 'vibration_g' if 'vibration_g' in df.columns else df.select_dtypes(include=[np.number]).columns[0]
        signal = df[col].to_numpy()
        
        rms = np.sqrt(np.mean(signal**2))
        peak_val = np.max(np.abs(signal))
        crest_factor = peak_val / rms if rms > 0 else 0
        peaks, _ = find_peaks(np.abs(signal), distance=10, prominence=1.5)
        
        label = "nominal_operating_state"
        if rms > 5.0 or crest_factor > 6.0:
            label = "mechanical_anomaly_vibration_spike"
            
        return {
            "modality": "2_1D_Sensor_Telemetry",
            "assigned_label": label,
            "metrics": {
                "signal_rms_amplitude": round(float(rms), 3),
                "crest_factor_ratio": round(float(crest_factor), 3),
                "detected_anomaly_timestamps_count": len(peaks),
                "anomaly_index_locations": [int(p) for p in peaks[:10]] # Limit to first 10 points
            }
        }

    def annotate_thermal_vision(self, file_path):
        """
        MODALITY 3: 2D Thermal / Infrared Matrix Feeds
        Isolates structural pixel hotspots and extracts bounding boxes of thermal stress.
        """
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"error": "Invalid image matrix"}
            
        # Segment extreme heat regions (white/bright pixels in thermal gradients)
        _, thresholded = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hotspots = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w * h > 10:  # Noise filter threshold
                hotspots.append({"x_min": x, "y_min": y, "width": w, "height": h, "pixel_area": int(w*h)})
                
        label = "stable_thermal_gradient" if len(hotspots) == 0 else "critical_thermal_hotspot_detected"
        
        return {
            "modality": "3_2D_Thermal_Vision",
            "assigned_label": label,
            "metrics": {
                "active_hotspot_zones": len(hotspots),
                "bounding_boxes_xywh": hotspots
            }
        }

    def annotate_technical_blueprint(self, file_path):
        """
        MODALITY 4: 2D Technical Blueprints & Engineering Drawings
        Parses text structures from digital PDFs or vectors from raster blueprint images.
        """
        ext = os.path.splitext(file_path)[-1].lower()
        metadata_found = []
        label = "standard_engineering_blueprint"

        if ext == '.pdf':
            # Extraction engine for digital vector PDF title blocks
            try:
                with open(file_path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    text = "".join([page.extract_text() for page in reader.pages])
                    # Scan document text strings for high-priority engineering tolerances/notes
                    for keyword in ["GD&T", "TOLERANCE", "UNLESS OTHERWISE SPECIFIED", "SCALE", "MATERIAL"]:
                        if keyword.lower() in text.lower():
                            metadata_found.append(keyword)
                label = "vector_metadata_complete_drawing" if len(metadata_found) > 0 else "unstructured_pdf_drawing"
            except Exception as e:
                metadata_found = [f"Error parsing PDF: {str(e)}"]
        else:
            # Computer Vision extraction engine for raster drawings (.jpg, .png)
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                # Apply Canny Edge Detection to pull geometric drawing outlines and line frames
                edges = cv2.Canny(img, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                metadata_found.append(f"raster_edge_density_{round(edge_density, 4)}")
                label = "high_density_geometric_drawing" if edge_density > 0.05 else "low_density_schematic"

        return {
            "modality": "4_2D_Technical_Blueprints",
            "assigned_label": label,
            "metrics": {
                "file_type_format": ext,
                "extracted_notations_and_features": metadata_found
            }
        }

    def annotate_kinematic_robotics(self, file_path):
        """
        MODALITY 5: Kinematic Joint Streams & Trajectory Paths
        Tracks coordinates of joints or tool center points (TCP) to verify alignment paths.
        """
        df = pd.read_csv(file_path)
        # Automatically assumes columns correspond to X, Y, Z coordinates or Joint Angles
        coords = df.select_dtypes(include=[np.number]).to_numpy()
        
        # Calculate total distance traversed along the robotic path trajectory vector
        diffs = np.diff(coords, axis=0)
        distances = np.sqrt(np.sum(diffs**2, axis=1))
        total_path_length = np.sum(distances)
        
        # Calculate maximum coordinate velocity variance deviation
        max_deviation = np.max(np.std(coords, axis=0))
        
        label = "smooth_kinematic_trajectory"
        if max_deviation > 50.0: # High variance flags joint jitter or jerky movements
            label = "kinematic_jitter_anomaly"

        return {
            "modality": "5_Kinematic_Robotics",
            "assigned_label": label,
            "metrics": {
                "total_trajectory_distance_mm": round(float(total_path_length), 2),
                "joint_spatial_variance": round(float(max_deviation), 3),
                "data_points_logged": len(coords)
            }
        }

    def run_master_pipeline(self, raw_data_manifest):
        """
        Core routing controller that maps all five data modalities automatically.
        """
        master_manifest = {}
        
        for asset_name, path in raw_data_manifest.items():
            if not os.path.exists(path):
                print(f"⚠️ File skipped (Not Found): {path}")
                continue
                
            ext = os.path.splitext(path)[-1].lower()
            print(f"⚙️ Auto-processing {asset_name} ({ext})...")
            
            try:
                if ext in ['.stl', '.obj', '.ply']:
                    annotation = self.annotate_3d_cad(path)
                elif ext in ['.csv'] and 'kinematic' in asset_name.lower():
                    annotation = self.annotate_kinematic_robotics(path)
                elif ext in ['.csv']:
                    annotation = self.annotate_sensor_telemetry(path)
                elif ext in ['.png', '.jpg', '.jpeg', '.tiff'] and 'thermal' in asset_name.lower():
                    annotation = self.annotate_thermal_vision(path)
                elif ext in ['.pdf', '.png', '.jpg', '.jpeg', '.dxf']:
                    annotation = self.annotate_technical_blueprint(path)
                else:
                    print(f"❓ Unknown file mapping extension rule: {ext}")
                    continue
                    
                master_manifest[asset_name] = annotation
                
                # Write unique local pairing JSON files
                with open(os.path.join(self.output_dir, f"{asset_name}_annotation.json"), "w") as f:
                    json.dump(annotation, f, indent=4)
                print(f"   ↳ Clean Label applied: {annotation['assigned_label']}")
                
            except Exception as e:
                print(f"❌ Failed processing asset: {asset_name}. Error: {str(e)}")
                
        # Write absolute combined AI master manifest tracking file
        with open(os.path.join(self.output_dir, "master_five_modality_manifest.json"), "w") as f:
            json.dump(master_manifest, f, indent=4)
        print("\n🏆 Universal Pipeline Execution Complete. Manifest file generated.")

if __name__ == "__main__":
    annotator = FiveModalityMechanicalAnnotator()
    
    # Complete Cross-Modal Test Dictionary Input Setup
    my_engineering_dataset = {
        "cad_model_gearbox": "./data/raw_ingest/cad_geometry/gearbox.stl",
        "bearing_vibration_sensor": "./data/raw_ingest/sensor_telemetry/bearing_01.csv",


"""
"thermal_motor_image": "./data/raw_ingest/thermal_vision/motor_thermal.jpg","manufacturing_blueprint_pdf": "./data/raw_ingest/technical_blueprints/layout.pdf","robotic_arm_kinematic_log": "./data/raw_ingest/robotics/kinematic_trajectory.csv"}annotator.run_master_pipeline(my_engineering_dataset)
"""
  
