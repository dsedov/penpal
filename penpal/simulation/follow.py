from PIL import Image
import numpy as np
import random

class FollowEdge:
    def __init__(self, canvas, image_path, angle_range=30, step_size=5, dpi=300, after_time=0, before_time=1000000000):
        self.canvas = canvas
        self.image_path = image_path
        self.angle_range = angle_range
        self.step_size = step_size
        self.image = Image.open(image_path).convert('L')
        self.dpi = dpi
        self.after_time = after_time
        self.before_time = before_time
        print(f"Resizing image to {self._mm_to_px(canvas.canvas_size_mm[0])}x{self._mm_to_px(canvas.canvas_size_mm[1])}")
        self.image = self.image.resize((self._mm_to_px(canvas.canvas_size_mm[0]), self._mm_to_px(canvas.canvas_size_mm[1])))
        print(f"Image size: {self.image.size}")
        print("Creating image array")
        self.img_array = np.array(self.image)
        print("Image array created")

    def _px_to_mm(self, px):
        return px * 25.4 / self.dpi
    def _mm_to_px(self, mm):
        return round(mm * self.dpi / 25.4) 
    
    def apply(self, point, time_step, all_points = []): 
        if time_step < self.after_time or time_step > self.before_time:
            return point

        current_x = self._mm_to_px(point["x"])
        current_y = self._mm_to_px(point["y"])

        best_score = float('-inf')
        best_angle = 0
        
        for angle in np.linspace(-self.angle_range, self.angle_range, 21):
            rad = np.radians(angle)
            next_x = int(current_x + self.step_size * np.cos(rad))
            next_y = int(current_y + self.step_size * np.sin(rad))
            
            if next_y < 0 or next_y >= self.image.height:
                continue
                
            line_y = np.linspace(0, self.image.height-1, self.image.height)
            above_mask = line_y < next_y
            below_mask = line_y >= next_y
            
            if 0 <= next_x < self.image.width and np.any(above_mask) and np.any(below_mask):
                column = self.img_array[:, next_x]
                above_score = np.mean(column[above_mask]) if np.sum(above_mask) > 0 else 0
                below_score = np.mean(column[below_mask]) if np.sum(below_mask) > 0 else 0
                score = below_score - above_score
                
                if score > best_score:
                    best_score = score
                    best_angle = angle
        
        rad = np.radians(best_angle)
        current_x = int(current_x + self.step_size * np.cos(rad))
        current_y = int(current_y + self.step_size * np.sin(rad))

        current_x = self._px_to_mm(current_x)
        current_y = self._px_to_mm(current_y)

        point["impulse"] = (current_x - point["x"], current_y - point["y"])

        return point