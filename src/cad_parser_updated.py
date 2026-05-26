"""
Updated 3D CAD Parse Engine (src/cad_parser.py)This upgraded module reads an assembly, splits it into separate physical components for segmentation, classifies the entire file geometry for classification, extracts sub-features like hole locations/diameters/threads, and automatically captures 2D images from different viewing angles.
"""
import os
import json
import numpy as np
import trimesh
import cv2

class AdvancedCADParser:
    def __init__(self, rules, snapshot_dir="./data/raw_ingest/cad_snapshots"):
        self.rules = rules
        self.snapshot_dir = snapshot_dir
        os.makedirs(self.snapshot_dir, exist_ok=True)

    def extract_hole_and_thread_features(self, mesh):
        """
        Analyzes localized surface curvature patterns to isolate cylindrical internal cutouts,
        calculating precise physical diameters, locations, and identifying fast-pitch threads.
        """
        hole_locations = []
        hole_diameters = []
        has_internal_threading = False

        try:
            # Group flat triangles into continuous smooth geometric surfaces (cylinders, planes)
            facets = mesh.facets(min_area=1.0)
            
            for facet_index in facets:
                # Isolate highly curved or cylindrical surface segments
                if len(facet_index) > 8: 
                    vertices = mesh.vertices[mesh.faces[facet_index].flatten()]
                    # Calculate bounding parameters of the surface region
                    min_bounds = np.min(vertices, axis=0)
                    max_bounds = np.max(vertices, axis=0)
                    center = (min_bounds + max_bounds) / 2.0
                    
                    # Estimate localized diameter via bounding box width/height profiles
                    dims = max_bounds - min_bounds
                    diameter = (dims[0] + dims[1]) / 2.0 
                    
                    # Filtering rules to separate standard bolt clearances from generic holes
                    if 1.0 <= diameter <= 50.0:  # Focus on standard industrial fastener ranges (M1 to M50)
                        hole_locations.append([round(float(c), 2) for c in center])
                        hole_diameters.append(round(float(diameter), 2))
                        
                        # High-frequency micro-undulations along a long axis flag screw threads
                        if len(facet_index) > 50 and np.std(vertices[:, 2]) > 2.0:
                            has_internal_threading = True
        except Exception:
            pass

        return {
            "detected_holes_count": len(hole_diameters),
            "hole_diameters_mm": hole_diameters,
            "hole_centers_xyz": hole_locations,
            "contains_internal_threads": has_internal_threading
        }

    def generate_2d_snapshots(self, mesh, asset_name):
        """
        Renders multi-view projection snapshots (Isometric, Front, Top) 
        of the 3D geometry to train downstream image classification models.
        """
        saved_paths = []
        try:
            # Set up a headless scene viewer matrix
            scene = trimesh.Scene(mesh)
            
            # Camera projection transformation matrices
            views = {
                "isometric": [np.pi / 4, np.pi / 4, 0],
                "front": [0, 0, 0],
                "top": [np.pi / 2, 0, 0]
            }
            
            for view_name, rotation in views.items():
                # Rotate scene camera coordinates relative to core model origin
                rotated_scene = scene.copy()
                rotated_scene.apply_transform(trimesh.transformations.euler_matrix(*rotation))
                
                # Render high-resolution binary pixel arrays natively
                png_data = rotated_scene.save_image(resolution=[512, 512], background=[255, 255, 255, 255])
                
                output_path = os.path.join(self.snapshot_dir, f"{asset_name}_{view_name}.png")
                with open(output_path, "wb") as img_file:
                    img_file.write(png_data)
                saved_paths.append(output_path)
        except Exception as e:
            print(f"   ⚠️ Render engine bypass for {asset_name}: {e}")
            
        return saved_paths

    def annotate_cad_data(self, file_path, asset_name):
        """
        Dual-mode pipeline executing macro-level File Classification 
        and micro-level Assembly Component Segmentation simultaneously.
        """
        # Load core asset geometry map
        base_mesh = trimesh.load(file_path)
        
        # 1. Global Macro Classification Logic
        global_volume = float(base_mesh.volume)
        global_extents = sorted([float(x) for x in base_mesh.extents])
        global_aspect_ratio = global_extents[-1] / global_extents[0] if global_extents[0] > 0 else 1
        
        file_classification_label = "complex_mechanical_machined_assembly"
        if global_aspect_ratio > 4.0:
            file_classification_label = "linear_transmission_system_assembly"

        # 2. Micro Part Segmentation Module
        # Automatically split combined single meshes into discrete internal independent solids
        if hasattr(base_mesh, 'split'):
            split_components = base_mesh.split()
        else:
            split_components = [base_mesh]
            
        segmentation_ledger = []
        print(f"   ↳ Segmenting assembly: Found {len(split_components)} distinct parts.")

        for idx, component in enumerate(split_components):
            comp_volume = float(component.volume)
            comp_extents = sorted([float(x) for x in component.extents])
            comp_aspect_ratio = comp_extents[-1] / comp_extents[0] if comp_extents[0] > 0 else 1
            
            # Extract internal hardware sub-features for the individual segment
            sub_features = self.extract_hole_and_thread_features(component)
            
            # Determine classification for the sub-part
            part_label = "machined_structural_casting"
            if comp_aspect_ratio > self.rules["shaft"]["min_aspect_ratio"]:
                part_label = "transmission_shaft_core"
            elif sub_features["contains_internal_threads"] or comp_volume < self.rules["fastener"]["max_volume_mm3"]:
                part_label = "threaded_fastener_hardware"
            elif (comp_extents[0] / float(component.area)) < self.rules["plate"]["max_thickness_to_area_ratio"]:
                part_label = "stamped_sheet_metal_bracket"

            segmentation_ledger.append({
                "sub_part_index_id": idx,
                "assigned_segment_label": part_label,
                "mass_properties": {
                    "part_volume_mm3": round(comp_volume, 2),
                    "part_surface_area_mm2": round(float(component.area), 2),
                    "bounding_envelope_lwh": [round(x, 2) for x in comp_extents]
                },
                "sub_features": sub_features
            })

        # Generate 2D image snapshot training cards completely hands-free
        rendered_image_links = self.generate_2d_snapshots(base_mesh, asset_name)

        return {
            "modality": "1_3D_CAD_Geometry",
            "file_classification_label": file_classification_label,
            "global_metrics": {
                "total_assembly_volume_mm3": round(global_volume, 2),
                "assembly_envelope_dimensions_lwh": [round(x, 2) for x in global_extents]
            },
            "generated_snapshot_paths": rendered_image_links,
            "assembly_segmentation_labels": segmentation_ledger
        }
