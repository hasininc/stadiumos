import logging
from typing import Dict, Any

logger = logging.getLogger("cv-edge")

class ZoneDensityEstimator:
    def __init__(self, frame_width: int = 640, frame_height: int = 480):
        self.width = frame_width
        self.height = frame_height
        
        # Define 4 quadrants as default monitoring zones
        # Zone coordinates: [x_min, y_min, x_max, y_max]
        mid_x = frame_width // 2
        mid_y = frame_height // 2
        
        self.zones = {
            'A': (0, 0, mid_x, mid_y, 12.0),       # Zone A, area 12 sqm
            'B': (mid_x, 0, frame_width, mid_y, 12.0), # Zone B, area 12 sqm
            'C': (0, mid_y, mid_x, frame_height, 15.0), # Zone C, area 15 sqm
            'D': (mid_x, mid_y, frame_width, frame_height, 15.0) # Zone D, area 15 sqm
        }
        
    def estimate_density(self, boxes: list) -> Dict[str, Any]:
        """
        Calculates occupancy and density rates per virtual zone.
        """
        zone_counts = {z: 0 for z in self.zones}
        
        for box in boxes:
            coords = box.xyxy[0].tolist() # [x1, y1, x2, y2]
            cx = (coords[0] + coords[2]) / 2
            cy = (coords[1] + coords[3]) / 2
            
            # Match centroid into zone boundaries
            for zone_id, (x_min, y_min, x_max, y_max, _) in self.zones.items():
                if x_min <= cx < x_max and y_min <= cy < y_max:
                    zone_counts[zone_id] += 1
                    break
                    
        zone_metrics = {}
        max_density = 0.0
        
        for zone_id, count in zone_counts.items():
            _, _, _, _, area_sqm = self.zones[zone_id]
            people_per_sqm = count / area_sqm
            max_density = max(max_density, people_per_sqm)
            
            # Map occupancy rate assuming 4 persons/sqm is 100% capacity limit
            occupancy_pct = min(100.0, (people_per_sqm / 4.0) * 100.0)
            
            zone_metrics[f"zone_{zone_id}_count"] = count
            zone_metrics[f"zone_{zone_id}_density"] = round(people_per_sqm, 2)
            zone_metrics[f"zone_{zone_id}_occupancy"] = round(occupancy_pct, 1)

        # Calculate overall parameters
        total_people = len(boxes)
        overall_density = total_people / sum(z[4] for z in self.zones.values())
        congestion_score = min(100.0, (overall_density / 3.0) * 100.0)
        
        if congestion_score < 30:
            risk_level = "LOW"
        elif congestion_score < 60:
            risk_level = "MEDIUM"
        elif congestion_score < 85:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
            
        return {
            'people_count': total_people,
            'crowd_density': round(overall_density * 100, 1), # scaled for display percent
            'congestion_score': round(congestion_score, 1),
            'risk_level': risk_level,
            'zone_details': zone_metrics
        }
