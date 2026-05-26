"""
Upgraded Database Flattening Engine (src/exporter.py)This updated utility parses your hierarchical segmentation datasets, tracks variable-length arrays (like multiple hole diameters or sub-part listings), and automatically compiles them into an clean, row-by-row .csv database format.
"""

import os
import pandas as pd

class CSVExporter:
    @staticmethod
    def convert_manifest_to_csv(master_manifest, output_directory):
        """
        Flattens highly nested multi-modal engineering JSON files into a 
        standard tabular CSV. Automatically unpacks part segmentations.
        """
        flattened_rows = []
        
        for asset_name, details in master_manifest.items():
            if "error" in details or "modality" not in details:
                continue
                
            modality = details.get("modality")
            
            # Specific optimization logic block for 3D CAD files
            if modality == "1_3D_CAD_Geometry":
                segments = details.get("assembly_segmentation_labels", [])
                snapshot_str = "|".join(details.get("generated_snapshot_paths", []))
                
                # Create a row entry for each internal segmented component found in the file
                for part in segments:
                    sub_f = part.get("sub_features", {})
                    
                    row_entry = {
                        "Asset_Identifier": asset_name,
                        "Engineering_Modality": modality,
                        "Global_File_Classification": details.get("file_classification_label"),
                        "Total_Assembly_Volume_mm3": details.get("global_metrics", {}).get("total_assembly_volume_mm3"),
                        "Generated_2D_Snapshot_Image_Paths": snapshot_str,
                        
                        # Sub-Component Segments Meta Details
                        "Segment_ID": part.get("sub_part_index_id"),
                        "Assigned_Component_Label": part.get("assigned_segment_label"),
                        "Component_Volume_mm3": part.get("mass_properties", {}).get("part_volume_mm3"),
                        "Component_Surface_Area_mm2": part.get("mass_properties", {}).get("part_surface_area_mm2"),
                        
                        # Deep Hole & Thread Features
                        "Detected_Holes_Count": sub_f.get("detected_holes_count", 0),
                        "Extracted_Hole_Diameters_List": "|".join(map(str, sub_f.get("hole_diameters_mm", []))),
                        "Hole_Centers_Coordinates_XYZ": "|".join(map(str, sub_f.get("hole_centers_xyz", []))),
                        "Is_Internal_Threaded_Boolean": sub_f.get("contains_internal_threads", False)
                    }
                    flattened_rows.append(row_entry)
            else:
                # Fallback handler logic maps alternative modalities (Sensors, Thermal, Blueprints) cleanly
                row_entry = {
                    "Asset_Identifier": asset_name,
                    "Engineering_Modality": modality,
                    "Global_File_Classification": details.get("assigned_label", "N/A"),
                    "Total_Assembly_Volume_mm3": "N/A",
                    "Generated_2D_Snapshot_Image_Paths": "N/A",
                    "Segment_ID": 0,
                    "Assigned_Component_Label": details.get("assigned_label", "N/A"),
                    "Component_Volume_mm3": details.get("metrics", {}).get("signal_rms_amplitude", "N/A"),
                    "Component_Surface_Area_mm2": "N/A",
                    "Detected_Holes_Count": details.get("metrics", {}).get("detected_hotspot_count", 0),
                    "Extracted_Hole_Diameters_List": "N/A",
                    "Hole_Centers_Coordinates_XYZ": "N/A",
                    "Is_Internal_Threaded_Boolean": "N/A"
                }
                flattened_rows.append(row_entry)
                
        if flattened_rows:
            df = pd.DataFrame(flattened_rows)
            csv_path = os.path.join(output_directory, "flattened_engineering_dataset.csv")
            df.to_csv(csv_path, index=False)
            print(f"\n📊 Tabular CSV database updated successfully: {csv_path}")
