import math
from copy import deepcopy
import tqdm
class Merge:
    def __init__(self, margin = 0.0):
        self.margin = margin
    def distance_point_to_point(x1, y1, x2, y2):
        """Calculate distance between two points."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def distance_point_to_line(px, py, x1, y1, x2, y2):
        """Calculate minimum distance from a point to a line segment."""
        # Vector from line start to point
        A = px - x1
        B = py - y1
        # Vector from line start to line end
        C = x2 - x1
        D = y2 - y1
        
        # Length of line segment squared
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        # If line has zero length, return distance to start point
        if len_sq == 0:
            return Merge.distance_point_to_point(px, py, x1, y1)
        
        # Calculate projection parameter
        param = dot / len_sq
        
        if param < 0:
            # Point is beyond start of line segment
            return Merge.distance_point_to_point(px, py, x1, y1)
        elif param > 1:
            # Point is beyond end of line segment
            return Merge.distance_point_to_point(px, py, x2, y2)
        
        # Project point onto line segment
        proj_x = x1 + param * C
        proj_y = y1 + param * D
        return Merge.distance_point_to_point(px, py, proj_x, proj_y)
    
    def lines_intersect(x1, y1, x2, y2, x3, y3, x4, y4, margin):
        """Check if two line segments intersect or come within margin distance."""
        # Check if any endpoint of one line is too close to the other line
        if (Merge.distance_point_to_line(x1, y1, x3, y3, x4, y4) <= margin or
            Merge.distance_point_to_line(x2, y2, x3, y3, x4, y4) <= margin or
            Merge.distance_point_to_line(x3, y3, x1, y1, x2, y2) <= margin or
            Merge.distance_point_to_line(x4, y4, x1, y1, x2, y2) <= margin):
            return True
            
        # Check actual intersection
        denominator = ((x4 - x3) * (y1 - y2) - (x1 - x2) * (y4 - y3))
        if denominator == 0:
            return False
        
        ua = ((y3 - y4) * (x1 - x3) + (x4 - x3) * (y1 - y3)) / denominator
        ub = ((y1 - y2) * (x1 - x3) + (x2 - x1) * (y1 - y3)) / denominator
        
        return (0 <= ua <= 1) and (0 <= ub <= 1)
    
    def _has_space_for_point(self, canvas, px, py):
        """Check if there's enough space around a point."""
        for op in canvas.draw_stack:
            if op["type"] == "point":
                if Merge.distance_point_to_point(px, py, op["x"], op["y"]) <= self.margin:
                    return False
            elif op["type"] == "line":
                if Merge.distance_point_to_line(px, py, op["x1"], op["y1"], 
                                       op["x2"], op["y2"]) <= self.margin:
                    return False
        return True
    def _split_line(self, x1, y1, x2, y2, step=1.0):
        """Split a line into smaller segments."""
        segments = []
        length = Merge.distance_point_to_point(x1, y1, x2, y2)
        if length < step:
            return [(x1, y1, x2, y2)]
            
        num_segments = math.ceil(length / step)
        dx = (x2 - x1) / num_segments
        dy = (y2 - y1) / num_segments
        
        for i in range(num_segments):
            start_x = x1 + i * dx
            start_y = y1 + i * dy
            end_x = x1 + (i + 1) * dx
            end_y = y1 + (i + 1) * dy
            if i == num_segments - 1:
                end_x, end_y = x2, y2  # Ensure last segment ends exactly at end point
            segments.append((start_x, start_y, end_x, end_y))
            
        return segments
    
    def _has_space_for_line_segment(self, canvas, x1, y1, x2, y2):
        """Check if there's enough space around a line segment."""
        for op in canvas.draw_stack:
            if op["type"] == "point":
                if Merge.distance_point_to_line(op["x"], op["y"], x1, y1, x2, y2) <= self.margin:
                    return False
            elif op["type"] == "line":
                if Merge.lines_intersect(x1, y1, x2, y2, 
                                op["x1"], op["y1"], 
                                op["x2"], op["y2"], 
                                self.margin):
                    return False
        return True
    
    
    def apply(self, canvas_1, canvas_2):
        new_canvas = canvas_1.clone()
        
        if self.margin <= 0.0:
            # Simple merge without margin checking
            new_canvas.draw_stack.extend(deepcopy(canvas_2.draw_stack))
            return new_canvas
            
        for op in tqdm.tqdm(canvas_2.draw_stack):
            if op["type"] == "point":
                if self._has_space_for_point(new_canvas, op["x"], op["y"]):
                    new_canvas.draw_stack.append(deepcopy(op))
                    
            elif op["type"] == "line":
                # Split the line into smaller segments
                segments = self._split_line(op["x1"], op["y1"], 
                                         op["x2"], op["y2"], 
                                         step=self.margin)
                
                # Track segments that can be added
                valid_segments = []
                current_segment = []
                
                for seg_x1, seg_y1, seg_x2, seg_y2 in segments:
                    if self._has_space_for_line_segment(new_canvas, 
                                                      seg_x1, seg_y1, 
                                                      seg_x2, seg_y2):
                        if not current_segment:
                            current_segment = [seg_x1, seg_y1]
                        current_segment[2:] = [seg_x2, seg_y2]
                    else:
                        if current_segment and len(current_segment) == 4:
                            valid_segments.append(tuple(current_segment))
                        current_segment = []
                
                # Add last valid segment if exists
                if current_segment and len(current_segment) == 4:
                    valid_segments.append(tuple(current_segment))
                
                # Create new line operations for valid segments
                for seg_x1, seg_y1, seg_x2, seg_y2 in valid_segments:
                    new_op = deepcopy(op)
                    new_op.update({
                        "x1": seg_x1,
                        "y1": seg_y1,
                        "x2": seg_x2,
                        "y2": seg_y2
                    })
                    new_canvas.draw_stack.append(new_op)
                    
        return new_canvas
