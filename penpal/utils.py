import math
import numpy as np
import cv2
def save_as_video(frames, output_path, fps=20):
    # Get dimensions from first frame
    height, width = np.array(frames[0]).shape[:2]
    
    # Create video writer object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID' for .avi
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Write each frame
    for frame in frames:
        # Convert PIL image to numpy array and from RGB to BGR
        frame_array = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        out.write(frame_array)
    
    # Release the video writer
    out.release()
class Optimizations:
    @staticmethod
    def are_points_collinear(p1, p2, p3, tolerance=0.1):
        """
        Check if three points are approximately collinear within a tolerance.
        Uses the area of the triangle formed by the three points.
        """
        # Calculate the area of the triangle formed by the three points
        area = abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - 
                   (p3[0] - p1[0]) * (p2[1] - p1[1])) / 2.0
        
        # Calculate the lengths of the sides
        len1 = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        len2 = math.sqrt((p3[0] - p2[0])**2 + (p3[1] - p2[1])**2)
        
        # Normalize area by the lengths to get a more meaningful tolerance
        if len1 * len2 > 0:
            normalized_area = area / (len1 * len2)
            return normalized_area <= tolerance
        return True

    @staticmethod
    def have_same_properties(line1, line2):
        """Check if two lines have the same visual properties."""
        return (line1["color"] == line2["color"] and 
                line1["thickness"] == line2["thickness"])

    @staticmethod
    def sort_lines(canvas):
        canvas.draw_stack.sort(key=lambda x: x["pid"])

    @staticmethod
    def merge_lines(canvas, tolerance=0.1):
        """
        Merge consecutive line segments in the canvas's draw stack that form
        approximately straight lines within the given tolerance.
        """
        if not canvas.draw_stack:
            return

        new_stack = []
        current_line = None
        
        for item in canvas.draw_stack:
            if item["type"] != "line":
                # If we were building a line, add it to new stack
                if current_line is not None:
                    new_stack.append(current_line)
                    current_line = None
                new_stack.append(item)
                continue

            if current_line is None:
                current_line = item.copy()
                continue

            # Check if the lines have the same properties
            if not Optimizations.have_same_properties(current_line, item):
                new_stack.append(current_line)
                current_line = item.copy()
                continue

            # Check if the lines are connected
            if (current_line["x2"] == item["x1"] and 
                current_line["y2"] == item["y1"]):
                
                # Check if the three points are collinear
                p1 = (current_line["x1"], current_line["y1"])
                p2 = (current_line["x2"], current_line["y2"])
                p3 = (item["x2"], item["y2"])
                
                if Optimizations.are_points_collinear(p1, p2, p3, tolerance):
                    # Merge the lines by extending the current line
                    current_line["x2"] = item["x2"]
                    current_line["y2"] = item["y2"]
                else:
                    # Lines aren't collinear enough, add current line and start new one
                    new_stack.append(current_line)
                    current_line = item.copy()
            else:
                # Lines aren't connected, add current line and start new one
                new_stack.append(current_line)
                current_line = item.copy()

        # Add the last line if there is one
        if current_line is not None:
            new_stack.append(current_line)

        # Update the canvas's draw stack
        canvas.draw_stack = new_stack




def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')

    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)

    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    """Calculate Euclidean distance between two RGB colors."""
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

def hex_to_color_name(hex_color):
    # Dictionary of common colors and their hex values
    color_map = {
        'red': '#FF0000',
        'green': '#00FF00',
        'blue': '#0000FF',
        'yellow': '#FFFF00',
        'cyan': '#00FFFF',
        'magenta': '#FF00FF',
        'white': '#FFFFFF',
        'black': '#000000',
        'gray': '#808080',
        'orange': '#FFA500',
        'purple': '#800080',
        'brown': '#A52A2A',
        'pink': '#FFC0CB',
        'lime': '#00FF00',
        'navy': '#000080',
        'teal': '#008080'
    }
    if isinstance(hex_color, type(None)):
        return 'unknown'
    # Convert input hex to RGB
    try:
        target_rgb = hex_to_rgb(hex_color)
    except ValueError:
        return 'unknown'
    
    # Find closest color
    min_distance = float('inf')
    closest_color = 'unknown'
    
    for name, hex_value in color_map.items():
        color_rgb = hex_to_rgb(hex_value)
        distance = color_distance(target_rgb, color_rgb)
        
        if distance < min_distance:
            min_distance = distance
            closest_color = name
    
    return closest_color