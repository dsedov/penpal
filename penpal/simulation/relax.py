import math

class Relax:
    def __init__(self, canvas, strength=0.1, radius=10.0, min_distance=2.0, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.strength = strength
        self.radius = radius
        self.min_distance = min_distance  # Minimum desired distance between points
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step, all_points=[]):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        
        # Initialize accumulated force
        force_x = 0.0
        force_y = 0.0
        
        # For each nearby point, calculate repulsion force
        for other in all_points:
            if other is point:  # Skip self
                continue
                
            dx = point["x"] - other["x"]
            dy = point["y"] - other["y"]
            distance_sq = dx * dx + dy * dy
            
            # Only consider points within radius
            if distance_sq < self.radius * self.radius and distance_sq > 0:
                distance = math.sqrt(distance_sq)
                
                # Calculate repulsion force (stronger when closer)
                # Force decreases with square of distance
                force_magnitude = self.strength * (1.0 - distance / self.radius)
                
                # If points are too close, apply stronger repulsion
                if distance < self.min_distance:
                    force_magnitude *= (self.min_distance / distance) * 2.0
                
                # Add to accumulated force, normalized by distance
                if distance > 0:  # Prevent division by zero
                    force_x += (dx / distance) * force_magnitude
                    force_y += (dy / distance) * force_magnitude
        
        # Add calculated force to current impulse
        current_impulse = point["impulse"]
        point["impulse"] = (
            current_impulse[0] + force_x,
            current_impulse[1] + force_y
        )
        
        return point

    def get_ideal_radius(self, num_points, area):
        """Calculate ideal radius based on number of points and area"""
        # Approximate ideal radius as sqrt(area / num_points)
        return math.sqrt(area / (num_points * math.pi)) * 2.5