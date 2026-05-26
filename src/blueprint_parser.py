# Extracts bounding vectors from 2D engineering sheets

"""
Modality 4 Engine (src/blueprint_parser.py)Extracts engineering data from vector drawings (.pdf) or applies edge maps to images (.png/.jpg).
"""
import os
import cv2
import numpy as np
import pypdf

class BlueprintParser:
    def __init__(self, rules):
        self.rules = rules

    def annotate(self, file_path):
        ext = os.path.splitext(file_path)[-1].lower()
        metadata_found = []
        label = "standard_engineering_blueprint"

        if ext == '.pdf':
            try:
                with open(file_path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    text = "".join([page.extract_text() for page in reader.pages])
                    for keyword in ["GD&T", "TOLERANCE", "SCALE", "MATERIAL"]:
                        if keyword.lower() in text.lower():
                            metadata_found.append(keyword)
                label = "vector_metadata_complete_drawing" if len(metadata_found) > 0 else "unstructured_pdf_drawing"
            except Exception as e:
                metadata_found = [f"Parsing error: {str(e)}"]
        else:
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                edges = cv2.Canny(img, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                metadata_found.append(f"raster_edge_density_{round(edge_density, 4)}")
                label = "high_density_geometric_drawing" if edge_density > 0.05 else "low_density_schematic"

        return {
            "modality": "4_2D_Technical_Blueprints",
            "assigned_label": label,
            "metrics": {
                "file_type_format": ext,
                "extracted_notations": metadata_found
            }
        }
      
