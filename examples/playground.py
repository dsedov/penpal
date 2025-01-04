import numpy as np
from PIL import Image, ImageDraw
import random

def follow_edge(image_path, angle_range=30, step_size=5):
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)
    width, height = img.size
    
    current_x = 0
    current_y = random.randint(0, height-1)
    
    result = img.convert('RGB')
    draw = ImageDraw.Draw(result)
    
    points = [(current_x, current_y)]
    
    while current_x < width - step_size:
        best_score = float('-inf')
        best_angle = 0
        
        for angle in np.linspace(-angle_range, angle_range, 21):
            rad = np.radians(angle)
            next_x = int(current_x + step_size * np.cos(rad))
            next_y = int(current_y + step_size * np.sin(rad))
            
            if next_y < 0 or next_y >= height:
                continue
                
            line_y = np.linspace(0, height-1, height)
            above_mask = line_y < next_y
            below_mask = line_y >= next_y
            
            if next_x < width and np.any(above_mask) and np.any(below_mask):
                column = img_array[:, next_x]
                above_score = np.mean(column[above_mask]) if np.sum(above_mask) > 0 else 0
                below_score = np.mean(column[below_mask]) if np.sum(below_mask) > 0 else 0
                score = below_score - above_score
                
                if score > best_score:
                    best_score = score
                    best_angle = angle
        
        rad = np.radians(best_angle)
        current_x = int(current_x + step_size * np.cos(rad))
        current_y = int(current_y + step_size * np.sin(rad))
        points.append((current_x, current_y))
    
    draw.line(points, fill=(255, 0, 0), width=2)
    return result

# Usage
image = follow_edge('landscape.jpg', angle_range=30, step_size=5)
image.save('result.png')