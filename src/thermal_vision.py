"""
Modality 3 Engine (src/thermal_vision.py)Processes infrared pictures using spatial gradients to track machine overheating zones.
"""
import cv2

class ThermalVisionAnnotator:
    def __init__(self, rules):
        self.rules = rules

    def annotate(self, file_path):
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"error": "Invalid image matrix"}
            
        _, thresholded = cv2.threshold(img, self.rules["thermal"]["brightness_threshold"], 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hotspots = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w * h > self.rules["thermal"]["min_pixel_area"]:
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
