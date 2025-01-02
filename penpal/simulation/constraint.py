import math

class IsometricConstraint:
    def __init__(self, canvas, angle_degrees=30, threshold=0.2, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.after_time = after_time
        self.before_time = before_time
        self.angle_rad = math.radians(angle_degrees)
        self.threshold = threshold  # Threshold for snapping
        
        # Pre-calculate all preferred angles in radians
        self.preferred_angles = [
            0,                    # Horizontal (0°)
            math.pi/2,           # Vertical (90°)
            self.angle_rad,      # 30°
            math.pi - self.angle_rad,    # 150°
            math.pi + self.angle_rad,    # 210°
            2*math.pi - self.angle_rad   # 330°
        ]

    def _normalize_angle(self, angle):
        """Normalize angle to be between 0 and 2π"""
        return angle % (2 * math.pi)

    def _vector_to_angle(self, x, y):
        """Convert vector to angle in radians"""
        return self._normalize_angle(math.atan2(y, x))

    def _angle_to_vector(self, angle, magnitude):
        """Convert angle back to vector with the same magnitude"""
        return (
            magnitude * math.cos(angle),
            magnitude * math.sin(angle)
        )

    def _find_closest_preferred_angle(self, current_angle):
        """Find the closest preferred angle"""
        min_diff = float('inf')
        closest_angle = 0
        
        for preferred in self.preferred_angles:
            # Calculate difference considering the circular nature of angles
            diff = abs(self._normalize_angle(current_angle - preferred))
            diff = min(diff, 2*math.pi - diff)
            
            if diff < min_diff:
                min_diff = diff
                closest_angle = preferred
        
        return closest_angle, min_diff

    def apply(self, point, time_step):
        """Apply the isometric constraint to the point's impulse"""
        if time_step < self.after_time or time_step > self.before_time:
            return point

        # Get current impulse
        x, y = point["impulse"]
        
        # If the impulse is too small, return unchanged
        magnitude = math.sqrt(x*x + y*y)
        if magnitude < 1e-6:
            return point

        # Convert current vector to angle
        current_angle = self._vector_to_angle(x, y)
        
        # Find the closest preferred angle
        closest_angle, min_diff = self._find_closest_preferred_angle(current_angle)
        
        # If the angle difference is within threshold, snap to preferred angle
        if min_diff <= self.threshold:
            new_x, new_y = self._angle_to_vector(closest_angle, magnitude)
            point["impulse"] = (new_x, new_y)
        
        return point

class MinImpulseConstraint:
    def __init__(self, canvas, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.after_time = after_time
        self.before_time = before_time


    def apply(self, point, time_step):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        if point["impulse"][0] < point["impulse"][1]:
            point["impulse"] = (point["impulse"][0] , 0.0)
        else:
            point["impulse"] = (0.0, point["impulse"][1])
        return point    
    
class MaxImpulseConstraint:
    def __init__(self, canvas, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        if point["impulse"][0] > point["impulse"][1]:
            point["impulse"] = (point["impulse"][0] , 0.0)
        else:
            point["impulse"] = (0.0, point["impulse"][1])
        return point    