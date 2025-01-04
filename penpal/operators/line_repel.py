class LineRepel:
    def __init__(self, canvas, strength=1.0, radius=10.0, iterations=10, group=None):
        self.canvas = canvas
        self.strength = strength
        self.radius = radius
        self.iterations = iterations
        self.group = group
        self.excluded_ops = []
        self.cell_size = radius * 2
        
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

    def _get_cell_coords(self, x, y):
        return (int(x / self.cell_size), int(y / self.cell_size))

    def _get_line_cells(self, x1, y1, x2, y2):
        start_cell = self._get_cell_coords(x1, y1)
        end_cell = self._get_cell_coords(x2, y2)
        
        cells = set()
        cells.add(start_cell)
        cells.add(end_cell)
        
        dx = end_cell[0] - start_cell[0]
        dy = end_cell[1] - start_cell[1]
        steps = max(abs(dx), abs(dy))
        
        if steps > 0:
            x_inc = dx / steps
            y_inc = dy / steps
            x = start_cell[0]
            y = start_cell[1]
            
            for _ in range(steps):
                x += x_inc
                y += y_inc
                cells.add((int(x), int(y)))
        
        return cells

    def _build_spatial_grid(self, lines_by_pid):
        grid = {}
        pid_to_cells = {}
        
        for pid, lines in lines_by_pid.items():
            pid_to_cells[pid] = set()
            for line in lines:
                cells = self._get_line_cells(line["x1"], line["y1"], line["x2"], line["y2"])
                for cell in cells:
                    if cell not in grid:
                        grid[cell] = {}
                    if pid not in grid[cell]:
                        grid[cell][pid] = []
                    grid[cell][pid].append(line)
                    pid_to_cells[pid].add(cell)
        
        return grid, pid_to_cells

    def _line_point_distance(self, px, py, x1, y1, x2, y2):
        line_vec = (x2 - x1, y2 - y1)
        point_vec = (px - x1, py - y1)
        line_len_sq = line_vec[0]**2 + line_vec[1]**2
        
        if line_len_sq == 0:
            return ((px - x1)**2 + (py - y1)**2)**0.5, (x1, y1)
            
        t = max(0, min(1, (point_vec[0]*line_vec[0] + point_vec[1]*line_vec[1]) / line_len_sq))
        
        closest_x = x1 + t * line_vec[0]
        closest_y = y1 + t * line_vec[1]
        
        dist = ((px - closest_x)**2 + (py - closest_y)**2)**0.5
        return dist, (closest_x, closest_y)

    def _calculate_repulsion(self, lines_by_pid):
        movements = {pid: [] for pid in lines_by_pid.keys()}
        grid, pid_to_cells = self._build_spatial_grid(lines_by_pid)
        
        for pid1, lines1 in lines_by_pid.items():
            cells_to_check = pid_to_cells[pid1]
            
            for cell in cells_to_check:
                if cell not in grid:
                    continue
                    
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        neighbor_cell = (cell[0] + dx, cell[1] + dy)
                        if neighbor_cell not in grid:
                            continue
                            
                        for pid2, lines2 in grid[neighbor_cell].items():
                            if pid1 >= pid2:
                                continue
                                
                            for line1 in grid[cell][pid1]:
                                for line2 in lines2:
                                    dist1, p1 = self._line_point_distance(
                                        line2["x1"], line2["y1"],
                                        line1["x1"], line1["y1"],
                                        line1["x2"], line1["y2"]
                                    )
                                    dist2, p2 = self._line_point_distance(
                                        line2["x2"], line2["y2"],
                                        line1["x1"], line1["y1"],
                                        line1["x2"], line1["y2"]
                                    )
                                    
                                    if min(dist1, dist2) < self.radius:
                                        force = (self.radius - min(dist1, dist2)) / self.radius * self.strength
                                        if dist1 < dist2:
                                            dx = line2["x1"] - p1[0]
                                            dy = line2["y1"] - p1[1]
                                        else:
                                            dx = line2["x2"] - p2[0]
                                            dy = line2["y2"] - p2[1]
                                            
                                        length = (dx * dx + dy * dy) ** 0.5
                                        if length > 0:
                                            dx = dx / length * force
                                            dy = dy / length * force
                                            movements[pid1].append((dx, dy))
                                            movements[pid2].append((-dx, -dy))
        
        return movements

    def apply(self):
        lines_by_pid = self._group_lines_by_pid()
        
        for _ in range(self.iterations):
            movements = self._calculate_repulsion(lines_by_pid)
            
            # Apply average movement to each pid group as a whole
            for pid, moves in movements.items():
                if not moves:
                    continue
                
                # Calculate average movement for this pid group
                avg_dx = sum(dx for dx, dy in moves) / len(moves)
                avg_dy = sum(dy for dx, dy in moves) / len(moves)
                
                # Apply the same movement to all lines in the group
                for line in lines_by_pid[pid]:
                    line["x1"] += avg_dx
                    line["y1"] += avg_dy
                    line["x2"] += avg_dx
                    line["y2"] += avg_dy
        
        # Update canvas
        self.canvas.draw_stack = self.excluded_ops + [op for op in self.canvas.draw_stack if op["type"] != "line"] + [
            line for lines in lines_by_pid.values() for line in lines
        ]