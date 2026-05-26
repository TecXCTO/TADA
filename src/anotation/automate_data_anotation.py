import os
import json
import trimesh

# Configuration: Define your raw data input directory and where to save output labels
CAD_DATA_DIR = "./raw_cad_models"
ANNOTATION_OUTPUT_DIR = "./labeled_output"
os.makedirs(ANNOTATION_OUTPUT_DIR, exist_ok=True)

def auto_generate_engineering_name(volume, surface_area, bounding_box_dims):
    """
    Automated Rule-Engine: Looks at physical properties of the CAD model
    and automatically assigns a standard engineering name taxonomy.
    """
    length, width, height = bounding_box_dims
    
    # Rule 1: Long, slender cylinders are automatically labeled as Shafts/Pins
    if length > (width * 3) or length > (height * 3):
        return "structural_shaft"
    
    # Rule 2: Highly flat parts with large surface areas are Plates
    if height < 5.0 and (volume / surface_area) < 2.0:
        return "mounting_plate"
    
    # Rule 3: Small parts with balanced volume/surface ratio are fastners/brackets
    if volume < 5000.0:
        return "fastener_component"
        
    # Default fallback label if no rule is met
    return "generic_machined_part"

def process_cad_dataset():
    print("🚀 Starting automated CAD data annotation pipeline...")
    
    # Loop through all 3D CAD files in your directory
    for file_name in os.listdir(CAD_DATA_DIR):
        if file_name.endswith(('.stl', '.obj', '.ply')):
            file_path = os.path.join(CAD_DATA_DIR, file_name)
            
            try:
                # 1. Load the raw 3D mesh file automatically
                mesh = trimesh.load(file_path)
                
                # 2. Extract geometric features natively from the CAD structure
                volume = float(mesh.volume)
                surface_area = float(mesh.area)
                bounding_box_dims = [float(x) for x in mesh.extents] # [Length, Width, Height]
                center_of_mass = [float(x) for x in mesh.center_mass]
                
                # 3. Apply the automated rule engine to determine the engineering classification name
                assigned_label = auto_generate_engineering_name(volume, surface_area, bounding_box_dims)
                
                # 4. Construct the standard AI data notation dictionary
                annotation_data = {
                    "source_file": file_name,
                    "automated_annotations": {
                        "engineering_class_name": assigned_label,
                        "metadata_properties": {
                            "calculated_volume_mm3": round(volume, 2),
                            "surface_area_mm2": round(surface_area, 2),
                            "bounding_box_lwh": [round(d, 2) for d in bounding_box_dims],
                            "centroid_coordinates": [round(c, 2) for c in center_of_mass]
                        },
                        "vertex_count": len(mesh.vertices),
                        "face_count": len(mesh.faces)
                    }
                }
                
                # 5. Export out the label text file matching the CAD model file name
                output_json_name = os.path.splitext(file_name)[0] + "_annotation.json"
                output_json_path = os.path.join(ANNOTATION_OUTPUT_DIR, output_json_name)
                
                with open(output_json_path, 'w') as json_file:
                    json.dump(annotation_data, json_file, indent=4)
                    
                print(f"✅ Successfully auto-labeled: {file_name} ➡️ {assigned_label}")
                
            except Exception as e:
                print(f"❌ Failed to auto-annotate {file_name}. Error: {str(e)}")

if __name__ == "__main__":
    # Create mock folder and file for a quick verification check
    os.makedirs(CAD_DATA_DIR, exist_ok=True)
    if not os.listdir(CAD_DATA_DIR):
        print(f"ℹ️ Please drop your 3D CAD files (.stl, .obj) into the '{CAD_DATA_DIR}' folder and run again.")
    else:
        process_cad_dataset()

