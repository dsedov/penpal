class Smooth:
    def __init__(self, canvas, strength=1.0, iterations=1, contraction=0.1, group=None):
        self.canvas = canvas
        self.strength = strength
        self.iterations = iterations
        self.contraction = contraction
        self.group = group
        self.excluded_ops = []
        if self.group is not None:
            for op in self.canvas.draw_stack:
                found = False
                for opg in self.group.ops:
                    if opg == op:
                        found = True
                        break
                if not found:
                    self.excluded_ops.append(op)

    def _group_lines_by_pid(self):
        lines_by_pid = {}
        for op in self.canvas.draw_stack if self.group is None else self.group.ops:
            if op["type"] == "line":
                pid = op["pid"]
                if pid not in lines_by_pid:
                    lines_by_pid[pid] = []
                lines_by_pid[pid].append(op)
        return lines_by_pid

    def _sort_connected_lines(self, lines):
        if not lines:
            return []
            
        sorted_lines = [lines[0]]
        remaining_lines = lines[1:]
        
        while remaining_lines:
            current_end = (sorted_lines[-1]["x2"], sorted_lines[-1]["y2"])
            found = False
            
            for i, line in enumerate(remaining_lines):
                if abs(line["x1"] - current_end[0]) < 0.001 and abs(line["y1"] - current_end[1]) < 0.001:
                    sorted_lines.append(line)
                    remaining_lines.pop(i)
                    found = True
                    break
                    
            if not found:
                sorted_lines.extend(remaining_lines)
                break
                
        return sorted_lines

    def _calculate_centroid(self, points):
        if not points:
            return (0, 0)
        x_sum = sum(p[0] for p in points)
        y_sum = sum(p[1] for p in points)
        return (x_sum / len(points), y_sum / len(points))

    def _smooth_points(self, points):
        """Apply smoothing to all points"""
        centroid = self._calculate_centroid(points)
        new_points = []
        
        for i in range(len(points)):
            current = points[i]
            
            # Smoothing based on neighbors
            if 0 < i < len(points) - 1:
                # For middle points, use neighbors for smoothing
                prev = points[i-1]
                next = points[i+1]
                smooth_x = current[0] + ((prev[0] + next[0])/2 - current[0]) * self.strength
                smooth_y = current[1] + ((prev[1] + next[1])/2 - current[1]) * self.strength
            else:
                # For endpoints, only apply contraction
                smooth_x = current[0]
                smooth_y = current[1]
            
            # Add gentle contraction towards centroid
            dist_to_center = ((current[0] - centroid[0])**2 + (current[1] - centroid[1])**2)**0.5
            max_dist = max(abs(p[0] - centroid[0]) + abs(p[1] - centroid[1]) for p in points)
            if max_dist > 0:
                contraction_factor = self.contraction * (dist_to_center / max_dist)
                final_x = smooth_x + (centroid[0] - smooth_x) * contraction_factor
                final_y = smooth_y + (centroid[1] - smooth_y) * contraction_factor
            else:
                final_x = smooth_x
                final_y = smooth_y
            
            new_points.append((final_x, final_y))
            
        return new_points

    def apply(self):
        lines_by_pid = self._group_lines_by_pid()
        new_lines = []
        
        for pid, lines in lines_by_pid.items():
            sorted_lines = self._sort_connected_lines(lines)
            if len(sorted_lines) < 2:
                new_lines.extend(sorted_lines)
                continue
            
            # Extract points
            points = [(line["x1"], line["y1"]) for line in sorted_lines]
            points.append((sorted_lines[-1]["x2"], sorted_lines[-1]["y2"]))
            
            # Apply smoothing iterations
            for _ in range(self.iterations):
                points = self._smooth_points(points)
            
            # Create new line segments
            for i in range(len(points) - 1):
                new_lines.append({
                    "type": "line",
                    "x1": points[i][0],
                    "y1": points[i][1],
                    "x2": points[i + 1][0],
                    "y2": points[i + 1][1],
                    "color": sorted_lines[0]["color"],
                    "thickness": sorted_lines[0]["thickness"],
                    "pid": pid
                })
        
        # Replace old lines with smoothed ones
        self.canvas.draw_stack = self.excluded_ops + [op for op in self.canvas.draw_stack if op["type"] != "line"] + new_lines