import cv2
import numpy as np
# No typing imports needed

class HeatmapGenerator:
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        # Accumulator map for temporal smoothing
        self.accum_map = np.zeros((height, width), dtype=np.float32)
        
    def generate_overlay(self, frame: np.ndarray, boxes: list) -> np.ndarray:
        """
        Generates a transparent crowd heatmap overlay blended onto the frame.
        """
        # Create a fresh frame intensity map for the current frame
        intensity_map = np.zeros((self.height, self.width), dtype=np.float32)
        
        for box in boxes:
            coords = box.xyxy[0].tolist() # [x1, y1, x2, y2]
            cx = int((coords[0] + coords[2]) / 2)
            cy = int((coords[1] + coords[3]) / 2)
            
            # Draw a circle on the intensity map centered at person's centroid
            cv2.circle(intensity_map, (cx, cy), 45, 1.0, -1)
            
        # Apply temporal smoothing (decay) to the accumulator map
        self.accum_map = cv2.addWeighted(self.accum_map, 0.85, intensity_map, 0.15, 0)
        
        # Normalize to 0-255 range
        norm_map = np.uint8(np.clip(self.accum_map * 255, 0, 255))
        
        # Apply Gaussian Blur to create smooth density fields
        blurred_map = cv2.GaussianBlur(norm_map, (15, 15), 0)
        
        # Apply OpenCV COLORMAP JET to create temperature visual ranges
        color_heatmap = cv2.applyColorMap(blurred_map, cv2.COLORMAP_JET)
        
        # Blend the heatmap overlay with the original frame (using 0.65 frame, 0.35 heatmap weight)
        blended_frame = cv2.addWeighted(frame, 0.70, color_heatmap, 0.30, 0)
        
        return blended_frame
