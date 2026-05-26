"""
Modality 1 Engine
(src/cad_parser.py)

Processes 3D CAD files (.stl, .obj, .ply) to compute mass and volumetric properties.
"""
import trimesh

class CADParser:
    def __init__(self, rules):
        self.rules = rules

    def annotate(self, file_path):
        mesh = trimesh.load(file_path)
        volume = float(mesh.volume)
        extents = sorted([float(x) for x in mesh.extents])
        aspect_ratio = extents[-1] / extents if extents > 0 else 1
        
        label = "custom_machined_component"
        if aspect_ratio > self.rules["shaft"]["min_aspect_ratio"]:
            label = "transmission_shaft_axis"
        elif (extents / float(mesh.area)) < self.rules["plate"]["max_thickness_to_area_ratio"]:
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
      
