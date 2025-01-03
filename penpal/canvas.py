import numpy as np
import random
from copy import deepcopy
from PIL import Image, ImageDraw 
class Canvas:
    def __init__(self, canvas_size_mm = (356.0, 432.0), margin = 15.0, paper_color="white", pen_color="black", respect_margin=False):
        self.canvas_size_mm = canvas_size_mm
        self.paper_color = paper_color
        self.pen_color = pen_color
        self.draw_stack = []
        self.tolerance = 0.2
        self.stored_matrix = np.identity(3) 
        self.current_matrix = np.identity(3)
        self.margin = margin
        self.respect_margin = respect_margin

        self.plotter_buffer = Image.new("L", (self._mm_to_pixels(canvas_size_mm[0]), self._mm_to_pixels(canvas_size_mm[1])), "black")
        self.plotter_buffer_thickness = 2.0
        self.plotter_buffer_draw = ImageDraw.Draw(self.plotter_buffer)

    @property
    def plottable_size(self):
        return (self.canvas_size_mm[0] - self.margin*2, self.canvas_size_mm[1] - self.margin*2)
    
    @property
    def top_left(self):
        return (self.margin, self.margin)
    
    @property
    def bottom_right(self):
        return (self.canvas_size_mm[0] - self.margin, self.canvas_size_mm[1] - self.margin)
    
    def clone(self):
        clone = Canvas(self.canvas_size_mm, self.margin, self.paper_color, self.pen_color, self.respect_margin)
        clone.draw_stack = deepcopy(self.draw_stack)
        clone.stored_matrix = deepcopy(self.stored_matrix)
        clone.current_matrix = deepcopy(self.current_matrix)
        return clone
    
    def crop(self):
        temp_stack = []
        for op in self.draw_stack:
            if op["type"] == "line":    
                if op["x1"] > self.margin and op["x1"] < self.canvas_size_mm[0] - self.margin and op["y1"] > self.margin and op["y1"] < self.canvas_size_mm[1] - self.margin:
                    if op["x2"] > self.margin and op["x2"] < self.canvas_size_mm[0] - self.margin and op["y2"] > self.margin and op["y2"] < self.canvas_size_mm[1] - self.margin:
                        temp_stack.append(op)
            elif op["type"] == "point":
                if op["x"] > self.margin and op["x"] < self.canvas_size_mm[0] - self.margin and op["y"] > self.margin and op["y"] < self.canvas_size_mm[1] - self.margin:
                    temp_stack.append(op)
        self.draw_stack = temp_stack

    def translate(self, x, y):
        self.current_matrix = np.dot(self.current_matrix, np.array([[1, 0, x], [0, 1, y], [0, 0, 1]]))

    def scale(self, x, y=None):
        if y is None:
            y = x
        self.current_matrix = np.dot(self.current_matrix, np.array([[x, 0, 0], [0, y, 0], [0, 0, 1]]))

    def rotate(self, angle):
        self.current_matrix = np.dot(self.current_matrix, np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]]))

    def push(self):
        self.stored_matrix = self.current_matrix
    def pop(self):
        self.current_matrix = self.stored_matrix

    def line(self, x1, y1, x2, y2, color=None, thickness=0.5, pid=None):
        self._line(x1, y1, x2, y2, color, thickness, pid)
    
    def point(self, x, y, color=None, thickness=0.5, pid=None):
        self._point(x, y, color, thickness, pid)
    
    def clear(self, type="all", chance=1.0):
        if type == "all":
            self.draw_stack = [op for op in self.draw_stack if random.random() < chance]
        elif type == "points":
            self.draw_stack = [op for op in self.draw_stack if op["type"] != "point" or random.random() < chance]
        elif type == "lines":
            self.draw_stack = [op for op in self.draw_stack if op["type"] != "line" or random.random() < chance]

    def merge_with(self, other):
        self.draw_stack.extend(other.draw_stack)

    def cubic_bezier(self, x1, y1, x2, y2, x3, y3, x4, y4, color=None, thickness=1.0):
        """
        Approximates the cubic Bézier curve (x1,y1)-(x2,y2)-(x3,y3)-(x4,y4)
        with line segments to within self.tolerance, and draws them using
        self.line(...).
        """

        import math

        def is_flat_enough(p1, p2, p3, p4, tolerance):
            """
            Checks if the control polygon p1->p2->p3->p4 is 'flat enough'
            by measuring the distance of p2 and p3 from the line p1->p4.
            """
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, p3, p4
            
            # Vector from p1 to p4
            dx = x4 - x1
            dy = y4 - y1
            seg_len = math.hypot(dx, dy)
            
            # Degenerate case: p1 == p4
            if seg_len < 1e-14:
                return True
            
            def dist_point_to_line(px, py):
                # Distance via the cross-product method
                return abs(dx*(py - y1) - dy*(px - x1)) / seg_len
            
            # Distances for p2, p3
            d2 = dist_point_to_line(x2, y2)
            d3 = dist_point_to_line(x3, y3)
            
            return (d2 <= tolerance) and (d3 <= tolerance)

        def subdivide_cubic_bezier(p1, p2, p3, p4):
            """
            Subdivide a cubic Bézier at t=0.5 using De Casteljau's algorithm.
            Returns (left_p1, left_p2, left_p3, left_p4), (right_p1, right_p2, right_p3, right_p4)
            """
            (x1, y1) = p1
            (x2, y2) = p2
            (x3, y3) = p3
            (x4, y4) = p4
            
            # First-level midpoints
            x12 = 0.5 * (x1 + x2)
            y12 = 0.5 * (y1 + y2)
            x23 = 0.5 * (x2 + x3)
            y23 = 0.5 * (y2 + y3)
            x34 = 0.5 * (x3 + x4)
            y34 = 0.5 * (y3 + y4)
            
            # Second-level midpoints
            x123 = 0.5 * (x12 + x23)
            y123 = 0.5 * (y12 + y23)
            x234 = 0.5 * (x23 + x34)
            y234 = 0.5 * (y23 + y34)
            
            # Third-level midpoint
            x1234 = 0.5 * (x123 + x234)
            y1234 = 0.5 * (y123 + y234)
            
            left  = ((x1, y1), (x12, y12), (x123, y123), (x1234, y1234))
            right = ((x1234, y1234), (x234, y234), (x34, y34), (x4, y4))
            return left, right

        def approximate_cubic_bezier(p1, p2, p3, p4, tolerance):
            """
            Recursively approximates the Bézier curve defined by control points
            p1, p2, p3, p4 to within 'tolerance'. Returns a list of points.
            """
            if is_flat_enough(p1, p2, p3, p4, tolerance):
                # Flat enough: just [start, end]
                return [p1, p4]
            else:
                # Subdivide and recurse
                left, right = subdivide_cubic_bezier(p1, p2, p3, p4)
                left_points  = approximate_cubic_bezier(*left,  tolerance)
                right_points = approximate_cubic_bezier(*right, tolerance)
                # Combine, removing the duplicate midpoint
                return left_points[:-1] + right_points
        
        # 1) Get all the approximation points
        p1 = (x1, y1)
        p2 = (x2, y2)
        p3 = (x3, y3)
        p4 = (x4, y4)
        points = approximate_cubic_bezier(p1, p2, p3, p4, self.tolerance / 30.0)

        # 2) Draw line segments between consecutive points
        for i in range(len(points) - 1):
            start = points[i]
            end   = points[i + 1]
            self._line(start[0], start[1], end[0], end[1], color, thickness)

    def box(self,
            x, y,
            w, h,
            color=None,
            thickness=1.0,
            filled=False,
            outline=True,
            fill_density=1.0,
            fill_direction='horizontal',
            align_fill_to_edges=False):

        # --- Draw the outline ---
        if outline:
            self._line(x,     y,     x + w, y,     color, thickness)  # top edge
            self._line(x + w, y,     x + w, y + h, color, thickness)  # right edge
            self._line(x + w, y + h, x,     y + h, color, thickness)  # bottom edge
            self._line(x,     y + h, x,     y,     color, thickness)  # left edge

        # --- If not filled, we are done ---
        if not filled:
            return

        # Calculate step size
        basic_step = abs(thickness / fill_density)
        
        if fill_direction.lower() == 'horizontal':
            if align_fill_to_edges:
                # Calculate number of zigzag sections needed
                num_steps = max(1, int(h / basic_step))
                # Adjust step size to exactly fit height
                step = h / num_steps
            else:
                step = basic_step

            # Start position
            curr_x = x
            curr_y = y
            going_right = True

            # Draw continuous zigzag
            while curr_y < y + h:
                next_y = min(curr_y + step, y + h)
                if going_right:
                    self._line(curr_x, curr_y, x + w, curr_y, color, thickness)
                    if curr_y < y + h - step/2:  # Draw connecting line if not at last step
                        self._line(x + w, curr_y, x + w, next_y, color, thickness)
                    curr_x = x + w
                else:
                    self._line(curr_x, curr_y, x, curr_y, color, thickness)
                    if curr_y < y + h - step/2:  # Draw connecting line if not at last step
                        self._line(x, curr_y, x, next_y, color, thickness)
                    curr_x = x
                
                curr_y = next_y
                going_right = not going_right

            # Add final line if needed (when we ended on a connecting line)
            if abs(curr_y - y - h) < step/2:
                self._line(x if not going_right else x + w, y + h, x + w if not going_right else x, y + h, color, thickness)

        elif fill_direction.lower() == 'vertical':
            if align_fill_to_edges:
                # Calculate number of zigzag sections needed
                num_steps = max(1, int(w / basic_step))
                # Adjust step size to exactly fit width
                step = w / num_steps
            else:
                step = basic_step

            # Start position
            curr_x = x
            curr_y = y
            going_down = True

            # Draw continuous zigzag
            while curr_x < x + w:
                next_x = min(curr_x + step, x + w)
                if going_down:
                    self._line(curr_x, curr_y, curr_x, y + h, color, thickness)
                    if curr_x < x + w - step/2:  # Draw connecting line if not at last step
                        self._line(curr_x, y + h, next_x, y + h, color, thickness)
                    curr_y = y + h
                else:
                    self._line(curr_x, curr_y, curr_x, y, color, thickness)
                    if curr_x < x + w - step/2:  # Draw connecting line if not at last step
                        self._line(curr_x, y, next_x, y, color, thickness)
                    curr_y = y
                
                curr_x = next_x
                going_down = not going_down

            # Add final line if needed (when we ended on a connecting line)
            if abs(curr_x - x - w) < step/2:
                self._line(x + w, y if not going_down else y + h, x + w, y + h if not going_down else y, color, thickness)


    def check_collision(self, x, y, radius=1):
        x, y, _ = self.current_matrix @ np.array([x, y, 1])
        px = self._mm_to_pixels(x)
        py = self._mm_to_pixels(y)
        
        pr = self._mm_to_pixels(radius)
        if px < 0 + pr or px >= self.plotter_buffer.width - pr or py < 0 + pr or py >= self.plotter_buffer.height - pr  :
            return False
        for cx in range(px-pr, px+pr):
            for cy in range(py-pr, py+pr):
                if self.plotter_buffer.getpixel((cx, cy)) == 255:
                    return True
        return False

    def _point(self, x, y, color=None, thickness=0.5, pid=None):
        x, y, _ = self.current_matrix @ np.array([x, y, 1])
        if self.respect_margin:
            if x < self.margin or x > self.canvas_size_mm[0] - self.margin or y < self.margin or y > self.canvas_size_mm[1] - self.margin:
                return

        self.draw_stack.append({
            "type": "point",
            "x": x,
            "y": y,
            "color": color,
            "thickness": thickness,
            "pid": pid
        })

        point_px = (self._mm_to_pixels(x), self._mm_to_pixels(y))
        thickness_px = self._mm_to_pixels(self.plotter_buffer_thickness)
        self.plotter_buffer_draw.ellipse([point_px[0]-thickness_px/2, point_px[1]-thickness_px/2, point_px[0]+thickness_px/2, point_px[1]+thickness_px/2], fill="white")

    def _line(self, x1, y1, x2, y2, color=None, thickness=0.5, pid=None):
        x1, y1, _ = self.current_matrix @ np.array([x1, y1, 1])
        x2, y2, _ = self.current_matrix @ np.array([x2, y2, 1])

        if self.respect_margin:
            if x1 < self.margin or x1 > self.canvas_size_mm[0] - self.margin or y1 < self.margin or y1 > self.canvas_size_mm[1] - self.margin:
                return
            if x2 < self.margin or x2 > self.canvas_size_mm[0] - self.margin or y2 < self.margin or y2 > self.canvas_size_mm[1] - self.margin:
                return

        self.draw_stack.append({
            "type": "line",
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": color,
            "thickness": thickness,
            "pid": pid
        })

        start_point_px = (self._mm_to_pixels(x1), self._mm_to_pixels(y1))
        end_point_px = (self._mm_to_pixels(x2), self._mm_to_pixels(y2))
        thickness_px = self._mm_to_pixels(self.plotter_buffer_thickness)
        self.plotter_buffer_draw.line([start_point_px, end_point_px], fill="white", width=thickness_px)

    def _mm_to_pixels(self, mm):
        return round(mm * 300 / 25.4)  