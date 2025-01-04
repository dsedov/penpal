class Flatten:
    def __init__(self, canvas, axis="x", strength=1.0, group=None):
        self.canvas = canvas
        self.axis = axis
        self.group = group
        self.strength = strength
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

    def _group_by_pid(self):
        """Group elements by their pid"""
        groups = {}
        for op in self.group.ops if self.group is not None else self.canvas.draw_stack:
            if "pid" in op:
                pid = op["pid"]
                if pid not in groups:
                    groups[pid] = []
                groups[pid].append(op)
        return groups

    def apply(self):
        # Group operations by pid
        pid_groups = self._group_by_pid()
        
        # Process each pid group
        for pid, ops in pid_groups.items():
            # Find the average position in the non-flattening axis for this group
            total = 0
            count = 0
            for op in ops:
                if op["type"] == "line":
                    if self.axis == "x":
                        # If flattening towards x-axis, average y values
                        total += op["y1"] + op["y2"]
                        count += 2
                    else:
                        # If flattening towards y-axis, average x values
                        total += op["x1"] + op["x2"]
                        count += 2
                elif op["type"] == "point":
                    if self.axis == "x":
                        total += op["y"]
                    else:
                        total += op["x"]
                    count += 1
            
            if count == 0:
                continue
                
            # Calculate target position (where we want to flatten towards)
            target = total / count
            
            # Move all elements in this group towards the target
            for op in ops:
                if op["type"] == "line":
                    if self.axis == "x":
                        # Move y coordinates towards target
                        op["y1"] = op["y1"] + (target - op["y1"]) * self.strength
                        op["y2"] = op["y2"] + (target - op["y2"]) * self.strength
                    else:
                        # Move x coordinates towards target
                        op["x1"] = op["x1"] + (target - op["x1"]) * self.strength
                        op["x2"] = op["x2"] + (target - op["x2"]) * self.strength
                elif op["type"] == "point":
                    if self.axis == "x":
                        op["y"] = op["y"] + (target - op["y"]) * self.strength
                    else:
                        op["x"] = op["x"] + (target - op["x"]) * self.strength
        
        # Update canvas
        if self.group is not None:
            self.canvas.draw_stack = self.excluded_ops + [op for ops in pid_groups.values() for op in ops]