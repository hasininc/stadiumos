import logging
from typing import Dict, Tuple, Set

logger = logging.getLogger("cv-edge")

class LineCrossingTracker:
    def __init__(self, line_y_ratio: float = 0.5, frame_height: int = 480):
        self.counting_line_y = int(frame_height * line_y_ratio)
        
        # Maps track_id -> last known Y coordinate
        self.track_history: Dict[int, int] = {}
        
        # Track IDs that have already crossed the line to avoid double-counting
        self.crossed_ids: Set[int] = set()
        
        self.entry_count = 0
        self.exit_count = 0
        
    def update(self, boxes: list) -> Tuple[int, int, int]:
        """
        Processes bounding boxes with tracking IDs.
        Returns:
            Tuple: (current_headcount, total_entries, total_exits)
        """
        current_headcount = len(boxes)
        active_ids = set()
        
        for box in boxes:
            # YOLO boxes are formatted as: xyxy, id, confidence, class
            # We can extract boxes coords and track ID
            coords = box.xyxy[0].tolist() # [x1, y1, x2, y2]
            
            if box.id is None:
                continue
                
            track_id = int(box.id[0].item())
            active_ids.add(track_id)
            
            # Calculate centroid Y coordinate
            cy = int((coords[1] + coords[3]) / 2)
            
            # If we have history for this ID, check for line crossing
            if track_id in self.track_history:
                prev_y = self.track_history[track_id]
                
                # Check for crossing
                if track_id not in self.crossed_ids:
                    # Crossed from top to bottom (Entry / Exit depending on orientation)
                    if prev_y < self.counting_line_y <= cy:
                        self.exit_count += 1
                        self.crossed_ids.add(track_id)
                        logger.info(f"Person ID {track_id} crossed line: EXIT. Total Exits: {self.exit_count}")
                    # Crossed from bottom to top
                    elif prev_y > self.counting_line_y >= cy:
                        self.entry_count += 1
                        self.crossed_ids.add(track_id)
                        logger.info(f"Person ID {track_id} crossed line: ENTRY. Total Entries: {self.entry_count}")
                        
            # Update history position
            self.track_history[track_id] = cy
            
        # Clean up stale track histories to avoid memory leaks
        stale_ids = set(self.track_history.keys()) - active_ids
        for stale_id in stale_ids:
            self.track_history.pop(stale_id, None)
            
        # Limit the crossed_ids cache size
        if len(self.crossed_ids) > 1000:
            # Remove oldest items (approximate)
            self.crossed_ids = set(list(self.crossed_ids)[200:])
            
        return current_headcount, self.entry_count, self.exit_count
