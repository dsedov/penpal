class Rule:
    def __init__(self, canvas, rule, strength=1.0, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.rule = rule
        self.strength = strength
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step, all_points=[]):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        self.rule(point, time_step, all_points, self)
        return point

    ## Rules
    def rule_to_return_to_original_y(point, time_step, all_points, rule):
        # Store original y position on first step
        if time_step == 0:
            point["original_y"] = point["y"]
        else:
            # Calculate how close we are to the right edge as a percentage (0 to 1)
            canvas_width = rule.canvas.right - rule.canvas.left
            distance_from_right = max(0, canvas_width - (point["x"] - rule.canvas.left))
            right_edge_influence = 1.0 - (distance_from_right / canvas_width)
            
            # Only start pulling when we're in the right half of the canvas
            if right_edge_influence > 0.5:
                # Calculate the deviation from original y position
                y_deviation = point["original_y"] - point["y"]
                
                # Scale the strength based on how close to the right edge we are
                # Use a quadratic curve for smoother transition
                scaled_strength = rule.strength * ((right_edge_influence - 0.5) * 2) ** 2
                
                # Apply a force towards the original y position
                correction_force = y_deviation * scaled_strength
                
                # Update the impulse
                point["impulse"] = (
                    point["impulse"][0],
                    point["impulse"][1] + correction_force
                )