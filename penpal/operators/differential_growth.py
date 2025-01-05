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
        """Split edges that exceed split_distance, but more conservatively"""
        new_edges = []
        new_nodes = nodes[:]
        
        # Find the average edge length to use as a reference
        total_length = 0
        for edge in edges:
            n1, n2 = edge
            p1 = nodes[n1]["pos"]
            p2 = nodes[n2]["pos"]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            total_length += math.hypot(dx, dy)
        avg_length = total_length / len(edges)
        
        # Only split if edge is significantly longer than average
        split_threshold = max(self.split_distance, 1.5 * avg_length)
        
        for edge in edges:
            n1, n2 = edge
            p1 = new_nodes[n1]["pos"]
            p2 = new_nodes[n2]["pos"]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.hypot(dx, dy)
            
            if dist > split_threshold:
                # Create new node at midpoint
                mx = 0.5 * (p1[0] + p2[0])
                my = 0.5 * (p1[1] + p2[1])
                new_index = len(new_nodes)
                new_nodes.append({"pos": [mx, my], "fixed": False})
                new_edges.append([n1, new_index])
                new_edges.append([new_index, n2])
            else:
                new_edges.append(edge)
        
        return new_nodes, new_edges

    def _apply_forces(self, nodes, edges):
        """Growth with controlled spread"""
        movements = [[0.0, 0.0] for _ in nodes]
        n = len(nodes)
        
        # Get circle center
        center_x = sum(n["pos"][0] for n in nodes) / n
        center_y = sum(n["pos"][1] for n in nodes) / n
        
        # Calculate current average segment length
        total_length = 0
        for (i1, i2) in edges:
            x1, y1 = nodes[i1]["pos"]
            x2, y2 = nodes[i2]["pos"]
            dx = x2 - x1
            dy = y2 - y1
            total_length += math.hypot(dx, dy)
        avg_length = total_length / len(edges) if edges else 1.0
        
        # Calculate growth probabilities based on neighbors
        growth_active = [False] * n
        
        # Start with one random active point if none exist
        if not any(growth_active):
            start_idx = random.randint(0, n-1)
            growth_active[start_idx] = True
        
        # Spread activation to neighbors with probability
        for i in range(n):
            if growth_active[i]:
                prev_i = (i - 1) % n
                next_i = (i + 1) % n
                if random.random() < 0.3:  # 30% chance to spread
                    growth_active[prev_i] = True
                if random.random() < 0.3:
                    growth_active[next_i] = True

        # 1. Repulsion forces with growth control
        rr_sq = self.repulsion_radius ** 2
        for i in range(n):
            if not growth_active[i]:
                continue
                
            x1, y1 = nodes[i]["pos"]
            # Outward force from center
            dx = x1 - center_x
            dy = y1 - center_y
            dist = math.hypot(dx, dy)
            if dist > 1e-8:
                force = self.repulsion_strength
                movements[i][0] += (dx / dist) * force
                movements[i][1] += (dy / dist) * force
                
            # Local repulsion
            for j in range(n):
                if i != j:
                    x2, y2 = nodes[j]["pos"]
                    dx = x2 - x1
                    dy = y2 - y1
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < rr_sq and dist_sq > 1e-8:
                        dist = math.sqrt(dist_sq)
                        force = self.repulsion_strength * (self.repulsion_radius - dist) / dist
                        fx = (dx / dist) * force
                        fy = (dy / dist) * force
                        movements[i][0] -= fx
                        movements[i][1] -= fy
                        movements[j][0] += fx
                        movements[j][1] += fy

        # 2. Attraction forces (maintain connections)
        for (i1, i2) in edges:
            x1, y1 = nodes[i1]["pos"]
            x2, y2 = nodes[i2]["pos"]
            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            if dist > 1e-8:
                # Stronger attraction for active regions
                strength = self.attraction_strength
                if growth_active[i1] or growth_active[i2]:
                    strength *= 0.5  # Reduce attraction in growing regions
                
                force = strength * (dist / avg_length)
                fx = (dx / dist) * force
                fy = (dy / dist) * force
                movements[i1][0] += fx
                movements[i1][1] += fy
                movements[i2][0] -= fx
                movements[i2][1] -= fy

        # 3. Alignment forces (smooth curve)
        for i in range(n):
            prev_i = (i - 1) % n
            next_i = (i + 1) % n
            
            x_prev = nodes[prev_i]["pos"][0]
            y_prev = nodes[prev_i]["pos"][1]
            x_curr = nodes[i]["pos"][0]
            y_curr = nodes[i]["pos"][1]
            x_next = nodes[next_i]["pos"][0]
            y_next = nodes[next_i]["pos"][1]
            
            # Move towards midpoint of neighbors
            mx = (x_prev + x_next) * 0.5 - x_curr
            my = (y_prev + y_next) * 0.5 - y_curr
            
            # Reduce alignment in active regions
            strength = self.alignment_strength
            if growth_active[i]:
                strength *= 0.5
                
            movements[i][0] += mx * strength
            movements[i][1] += my * strength

        # Apply movements with bounds
        max_move = avg_length * 0.5  # Limit per-step movement
        for i in range(n):
            if not nodes[i]["fixed"]:
                dx = movements[i][0] * self.damping
                dy = movements[i][1] * self.damping
                # Clamp movement
                dist = math.hypot(dx, dy)
                if dist > max_move:
                    dx = (dx / dist) * max_move
                    dy = (dy / dist) * max_move
                nodes[i]["pos"][0] += dx
                nodes[i]["pos"][1] += dy

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
