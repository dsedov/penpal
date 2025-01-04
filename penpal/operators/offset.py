import math
import random
from copy import deepcopy

class Offset:
    def __init__(self, canvas, offset_distance, count=1, continuity_threshold=0.1, rule=None, group=None):
        self.canvas = canvas
        self.offset_distance = offset_distance  # Scalar offset distance
        self.count = count  # Number of parallel offsets to create
        self.threshold = continuity_threshold
        self.rule = rule
        self.group = group
    
    def _normalize_vector(self, x, y):
        """Normalize a vector to unit length."""
        length = math.sqrt(x*x + y*y)
        if length == 0:
            return 0, 0
        return x/length, y/length
    
    def _get_perpendicular(self, dx, dy):
        """Get perpendicular vector (rotated 90 degrees counterclockwise)."""
        return -dy, dx
    
    def _get_line_normal(self, x1, y1, x2, y2):
        """Get normalized perpendicular vector to line."""
        dx = x2 - x1
        dy = y2 - y1
        px, py = self._get_perpendicular(dx, dy)
        return self._normalize_vector(px, py)
    
    def _vector_angle(self, x1, y1, x2, y2):
        """Get angle between two vectors in radians."""
        dot = x1*x2 + y1*y2
        det = x1*y2 - y1*x2
        return math.atan2(det, dot)
    
    def _points_connected(self, x1, y1, x2, y2):
        """Check if two points are within threshold distance."""
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx*dx + dy*dy) <= self.threshold
    
    def _find_connected_lines(self):
        """Group connected lines together."""
        if self.group:
            lines = [op for op in self.group.ops if op["type"] == "line"]
        else:
            lines = [op for op in self.canvas.draw_stack if op["type"] == "line"]
        if not lines:
            return []
            
        groups = []
        current_group = [lines[0]]
        
        for line in lines[1:]:
            prev_line = current_group[-1]
            
            # Check if current line connects to previous line
            if self._points_connected(prev_line["x2"], prev_line["y2"], line["x1"], line["y1"]):
                # Make end point of previous line exactly match start point of current line
                line["x1"] = prev_line["x2"]
                line["y1"] = prev_line["y2"]
                current_group.append(line)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [line]
        
        if current_group:
            groups.append(current_group)
            
        return groups

    def _offset_line(self, x1, y1, x2, y2, offset_multiplier=1):
        """Offset a single line segment by the perpendicular distance."""
        nx, ny = self._get_line_normal(x1, y1, x2, y2)
        offset_x = self.offset_distance * offset_multiplier * nx
        offset_y = self.offset_distance * offset_multiplier * ny
        return (x1 + offset_x, y1 + offset_y, 
                x2 + offset_x, y2 + offset_y)

    def _handle_corner(self, prev_line, curr_line, next_line, offset_multiplier=1):
        """Handle the corner between three connected line segments."""
        # Get normals for the lines
        prev_nx, prev_ny = self._get_line_normal(prev_line["x1"], prev_line["y1"],
                                                prev_line["x2"], prev_line["y2"])
        next_nx, next_ny = self._get_line_normal(next_line["x1"], next_line["y1"],
                                                next_line["x2"], next_line["y2"])
        
        # Calculate angle between the normals
        angle = self._vector_angle(prev_nx, prev_ny, next_nx, next_ny)
        
        # If angle is very small (lines are nearly parallel), use simple offset
        if abs(angle) < 0.01:  # About 0.57 degrees
            return self._offset_line(curr_line["x1"], curr_line["y1"],
                                   curr_line["x2"], curr_line["y2"],
                                   offset_multiplier)
        
        # Calculate offset points for both lines
        prev_offset = self._offset_line(prev_line["x1"], prev_line["y1"],
                                      prev_line["x2"], prev_line["y2"],
                                      offset_multiplier)
        next_offset = self._offset_line(next_line["x1"], next_line["y1"],
                                      next_line["x2"], next_line["y2"],
                                      offset_multiplier)
        
        # Use intersection of offset lines as corner point
        # Line 1: p1 + t*(p2-p1) = Line 2: q1 + s*(q2-q1)
        p1x, p1y = prev_offset[2], prev_offset[3]  # End of prev offset line
        p2x, p2y = p1x + (prev_line["x2"] - prev_line["x1"]), p1y + (prev_line["y2"] - prev_line["y1"])
        q1x, q1y = next_offset[0], next_offset[1]  # Start of next offset line
        q2x, q2y = q1x + (next_line["x2"] - next_line["x1"]), q1y + (next_line["y2"] - next_line["y1"])
        
        # Calculate intersection
        dx1 = p2x - p1x
        dy1 = p2y - p1y
        dx2 = q2x - q1x
        dy2 = q2y - q1y
        
        denom = dx1*dy2 - dy1*dx2
        if abs(denom) < 1e-10:
            # Lines are parallel, use midpoint
            corner_x = (p1x + q1x) / 2
            corner_y = (p1y + q1y) / 2
        else:
            t = ((q1x - p1x)*dy2 - (q1y - p1y)*dx2) / denom
            corner_x = p1x + t*dx1
            corner_y = p1y + t*dy1
        
        return (prev_offset[0], prev_offset[1], corner_x, corner_y)
    
    def apply(self, chance=1.0):
        max_pid = self.canvas.max_pid()
        # Process lines by connected groups
        connected_groups = self._find_connected_lines()
        final_connected_groups = []
        for group in connected_groups:
            if random.random() > chance:
                continue
            final_connected_groups.append(group)
        connected_groups = final_connected_groups
        # Create and add offset lines for each count
        for offset_num in range(1, self.count + 1):
            # Create and add offset lines for each group
            for group in connected_groups:
                offset_lines = []
                
                # Handle single line case
                if len(group) == 1:
                    line = group[0]
                    new_line = deepcopy(line)
                    ox1, oy1, ox2, oy2 = self._offset_line(
                        line["x1"], line["y1"],
                        line["x2"], line["y2"],
                        offset_num
                    )
                    new_line.update({"x1": ox1, "y1": oy1, "x2": ox2, "y2": oy2})
                    offset_lines.append(new_line)
                    continue
                
                # Handle connected lines
                for i in range(len(group)):
                    new_line = deepcopy(group[i])
                    
                    if i == 0:
                        # First line - simple offset for start, corner handling for end
                        ox1, oy1, ox2, oy2 = self._handle_corner(
                            group[i], group[i], group[i+1], offset_num
                        )
                    elif i == len(group) - 1:
                        # Last line - use previous corner point for start, simple offset for end
                        prev_line = offset_lines[-1]
                        ox1, oy1 = prev_line["x2"], prev_line["y2"]
                        _, _, ox2, oy2 = self._offset_line(
                            group[i]["x1"], group[i]["y1"],
                            group[i]["x2"], group[i]["y2"],
                            offset_num
                        )
                    else:
                        # Middle line - use previous corner point for start, calculate new corner for end
                        prev_line = offset_lines[-1]
                        ox1, oy1 = prev_line["x2"], prev_line["y2"]
                        _, _, ox2, oy2 = self._handle_corner(
                            group[i], group[i], group[i+1], offset_num
                        )
                    
                    new_line.update({"x1": ox1, "y1": oy1, "x2": ox2, "y2": oy2})
                    offset_lines.append(new_line)
                
                # Add offset lines to the canvas
                for line in offset_lines:
                    self.canvas.line(line["x1"], line["y1"], line["x2"], line["y2"], line["color"], line["thickness"], pid=max_pid+1)
                max_pid += 1
