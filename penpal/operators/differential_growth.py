import math
import random
class DifferentialGrowth:
    def __init__(
        self, 
        canvas, 
        split_distance=2.0, 
        repulsion_radius=20.0, 
        repulsion_strength=0.2, 
        attraction_strength=0.02, 
        alignment_strength=0.5, 
        damping=0.1,  
        relax_iterations=5,
        group=None
    ):
        self.canvas = canvas
        self.split_distance = split_distance
        self.repulsion_radius = repulsion_radius
        self.repulsion_strength = repulsion_strength
        self.attraction_strength = attraction_strength
        self.alignment_strength = alignment_strength
        
        self.damping = damping
        self.relax_iterations = relax_iterations

        self.group = group
        self.excluded_ops = []
        
        # Exclude ops that aren't in the group, if group is given
        if self.group is not None:
            for op in self.canvas.draw_stack:
                if op not in self.group.ops:
                    self.excluded_ops.append(op)

    def _group_by_pid(self):
        """Group elements by their pid."""
        groups = {}
        if self.group:
            ops_to_process = self.group.ops
        else:
            ops_to_process = self.canvas.draw_stack

        for op in ops_to_process:
            # If lines don't have a "pid" at all, nothing gets grouped
            if "pid" in op:
                pid = op["pid"]
                if pid not in groups:
                    groups[pid] = []
                groups[pid].append(op)
        return groups

    def _extract_nodes(self, lines):
        """Convert line segments to list of unique nodes with forced closure"""
        nodes = []
        seen_points = {}
        
        def get_point_key(x, y):
            return (round(x, 6), round(y, 6))
        
        # First pass - collect all points
        for line in lines:
            p1 = get_point_key(line["x1"], line["y1"])
            p2 = get_point_key(line["x2"], line["y2"])
            
            if p1 not in seen_points:
                idx = len(nodes)
                nodes.append({"pos": [line["x1"], line["y1"]], "fixed": False})
                seen_points[p1] = idx
                
            if p2 not in seen_points:
                idx = len(nodes)
                nodes.append({"pos": [line["x2"], line["y2"]], "fixed": False})
                seen_points[p2] = idx
        
        # Force closure - make last point exactly match first point
        if nodes:
            # Make a new node that's exactly at the start position
            nodes.append({"pos": nodes[0]["pos"].copy(), "fixed": False})
            
        return nodes

    def _create_edges(self, nodes, close_threshold=1e-3):
        """
        Modified to ensure proper handling of closed curves
        """
        edges = []
        ncount = len(nodes)
        if ncount < 2:
            return edges
            
        # Build edges following the curve order
        for i in range(ncount - 1):
            edges.append([i, (i + 1)])
        
        # If it's a closed curve (like our circle), add the closing edge
        first_pos = nodes[0]["pos"]
        last_pos = nodes[-1]["pos"]
        dx = last_pos[0] - first_pos[0]
        dy = last_pos[1] - first_pos[1]
        if dx*dx + dy*dy < close_threshold:
            edges.append([ncount - 1, 0])
        
        return edges

    def _split_long_edges(self, nodes, edges):
        """Split edges that exceed split_distance with debug output"""
        new_edges = []
        new_nodes = nodes[:]
        
        # Debug: Check current edge lengths
        for edge in edges:
            n1, n2 = edge
            p1 = nodes[n1]["pos"]
            p2 = nodes[n2]["pos"]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.hypot(dx, dy)
            # Debug print if any edge is longer than split distance
            if dist > self.split_distance:
                print(f"Found edge to split: length {dist:.2f} > split_distance {self.split_distance}")

        for edge in edges:
            n1, n2 = edge
            p1 = new_nodes[n1]["pos"]
            p2 = new_nodes[n2]["pos"]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.hypot(dx, dy)
            
            if dist > self.split_distance:
                # Create new node at midpoint
                mx = 0.5 * (p1[0] + p2[0])
                my = 0.5 * (p1[1] + p2[1])
                new_index = len(new_nodes)
                new_nodes.append({"pos": [mx, my], "fixed": False})
                new_edges.append([n1, new_index])
                new_edges.append([new_index, n2])
                print(f"Split edge into two segments: {dist:.2f} -> {dist/2:.2f}")
            else:
                new_edges.append(edge)
        
        return new_nodes, new_edges

    def _apply_forces(self, nodes, edges):
        """Growth with explicit distortion regions"""
        movements = [[0.0, 0.0] for _ in nodes]
        n = len(nodes)
        
        # Get circle center
        center_x = sum(n["pos"][0] for n in nodes) / n
        center_y = sum(n["pos"][1] for n in nodes) / n
        
        # Pick a section of the circle to distort (30-degree arc)
        distortion_center = random.random() * 2 * math.pi
        distortion_width = math.pi / 6  # 30 degrees
        
        for i in range(n):
            x, y = nodes[i]["pos"]
            # Calculate angle from center
            angle = math.atan2(y - center_y, x - center_x)
            
            # Check if point is in distortion region
            angle_diff = abs((angle - distortion_center + math.pi) % (2 * math.pi) - math.pi)
            if angle_diff < distortion_width:
                # Calculate outward and tangential forces
                dist = math.hypot(x - center_x, y - center_y)
                
                # Strong outward force
                outward_x = (x - center_x) / dist * self.repulsion_strength * 2.0
                outward_y = (y - center_y) / dist * self.repulsion_strength * 2.0
                
                # Tangential force (perpendicular to radius)
                tangent_x = -outward_y
                tangent_y = outward_x
                
                # Combine forces with falloff based on distance from distortion center
                falloff = 1.0 - (angle_diff / distortion_width)
                movements[i][0] += (outward_x + tangent_x * 0.5) * falloff
                movements[i][1] += (outward_y + tangent_y * 0.5) * falloff

        # Maintain connections
        for (i1, i2) in edges:
            x1, y1 = nodes[i1]["pos"]
            x2, y2 = nodes[i2]["pos"]
            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            if dist > self.split_distance:
                force = (dist - self.split_distance) * self.attraction_strength
                movements[i1][0] += dx * force / dist
                movements[i1][1] += dy * force / dist
                movements[i2][0] -= dx * force / dist
                movements[i2][1] -= dy * force / dist

        # Apply movements
        for i in range(n):
            if not nodes[i]["fixed"]:
                nodes[i]["pos"][0] += movements[i][0] * self.damping
                nodes[i]["pos"][1] += movements[i][1] * self.damping

        return nodes

    def _relax(self, nodes, edges):
        """Run multiple force passes."""
        for _ in range(self.relax_iterations):
            nodes = self._apply_forces(nodes, edges)
        return nodes

    def _nodes_to_lines(self, nodes, original_lines):
        """Convert node positions back to line segments with proper closure"""
        new_lines = []
        if not original_lines or not nodes:
            return new_lines
        
        line_template = original_lines[0].copy()
        
        # Create lines between consecutive points
        for i in range(len(nodes) - 1):  # Note: -1 because we added an extra closing node
            line = line_template.copy()
            line.update({
                "x1": nodes[i]["pos"][0],
                "y1": nodes[i]["pos"][1],
                "x2": nodes[i + 1]["pos"][0],
                "y2": nodes[i + 1]["pos"][1],
            })
            new_lines.append(line)
        
        return new_lines

    def apply(self):
        """Main differential growth step."""
        print(f"Before growth - number of lines: {len(self.canvas.draw_stack)}")
        pid_groups = self._group_by_pid()
        
        # Debug the pid groups
        print(f"Number of pid groups: {len(pid_groups)}")
        for pid, lines in pid_groups.items():
            print(f"Group {pid}: {len(lines)} lines")

        all_new_lines = []
        if not pid_groups:
            pid_groups = { None: self.canvas.draw_stack }

        for pid, lines in pid_groups.items():
            nodes = self._extract_nodes(lines)
            edges = self._create_edges(nodes, close_threshold=1e-3)
            nodes = self._relax(nodes, edges)
            nodes, edges = self._split_long_edges(nodes, edges)
            new_lines = self._nodes_to_lines(nodes, lines)
            all_new_lines.extend(new_lines)

        # Debug the result
        print(f"After growth - number of lines: {len(all_new_lines)}")
        
        self.canvas.draw_stack = self.excluded_ops + all_new_lines
