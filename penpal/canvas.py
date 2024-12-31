import numpy as np
class Canvas:
    def __init__(self, canvas_size_mm = (356.0, 432.0), paper_color="white", pen_color="black"):
        self.canvas_size_mm = canvas_size_mm
        self.paper_color = paper_color
        self.pen_color = pen_color
        self.draw_stack = []
        self.tolerance = 0.2

    def line(self, x1, y1, x2, y2, color=None, thickness=0.5):
        self.draw_stack.append({
            "type": "line",
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": color,
            "thickness": thickness
        })

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
            self.line(start[0], start[1], end[0], end[1], color, thickness)


    def box2(self, x, y, w, h, color=None, thickness=1.0, filled=False, fill_direction='horizontal'):
        # Draw the box outline
        self.line(x, y, x + w, y, color, thickness)
        self.line(x + w, y, x + w, y + h, color, thickness)
        self.line(x + w, y + h, x, y + h, color, thickness)
        self.line(x, y + h, x, y, color, thickness)
        
        if filled:
            step = thickness
            
            if fill_direction == 'horizontal':
                # Horizontal fill with snake pattern
                going_right = True
                for i in np.arange(step, h, step):
                    if going_right:
                        self.line(x, y + i, x + w, y + i, color, thickness)
                        # Small vertical line to connect to next horizontal line
                        if i + step < h:
                            self.line(x + w, y + i, x + w, y + i + step, color, thickness)
                    else:
                        self.line(x + w, y + i, x, y + i, color, thickness)
                        # Small vertical line to connect to next horizontal line
                        if i + step < h:
                            self.line(x, y + i, x, y + i + step, color, thickness)
                    going_right = not going_right
                    
            elif fill_direction == 'vertical':
                # Vertical fill with snake pattern
                going_up = True
                for i in np.arange(step, w, step):
                    if going_up:
                        self.line(x + i, y, x + i, y + h, color, thickness)
                        # Small horizontal line to connect to next vertical line
                        if i + step < w:
                            self.line(x + i, y, x + i + step, y, color, thickness)
                    else:
                        self.line(x + i, y + h, x + i, y, color, thickness)
                        # Small horizontal line to connect to next vertical line
                        if i + step < w:
                            self.line(x + i, y + h, x + i + step, y + h, color, thickness)
                    going_up = not going_up
    def box(self,
            x, y,
            w, h,
            color=None,
            thickness=1.0,
            filled=False,
            fill_direction='horizontal'):
        """
        Draws a box from (x, y) with width=w and height=h.
        If filled, draws zig-zag fill lines so the pen does not lift.
        
        :param x: Top-left x coordinate
        :param y: Top-left y coordinate
        :param w: Box width
        :param h: Box height
        :param color: Drawing color
        :param thickness: Line thickness
        :param filled: Whether or not to fill the box
        :param fill_direction: 'horizontal' or 'vertical' for fill direction
        """

        # --- Draw the outline ---
        self.line(x,     y,     x + w, y,     color, thickness)  # top edge
        self.line(x + w, y,     x + w, y + h, color, thickness)  # right edge
        self.line(x + w, y + h, x,     y + h, color, thickness)  # bottom edge
        self.line(x,     y + h, x,     y,     color, thickness)  # left edge

        # --- If not filled, we are done ---
        if not filled:
            return

        # You can tweak 'step' to control spacing between fill lines
        step = thickness  

        if fill_direction.lower() == 'horizontal':
            """
            We will:
            1. Start at (x, y).
            2. Go right across to (x+w, y).
            3. Go up a 'step' to (x+w, y+step).
            4. Go left across to (x, y+step).
            5. Go up a 'step' to (x, y+2*step).
            6. Repeat until we reach the top.
            """

            # Current "pen" position
            px = x
            py = y

            # We'll alternate direction each row
            direction_left_to_right = True

            # Continue until the next horizontal line would be above the box
            while py + step <= y + h:
                if direction_left_to_right:
                    # Draw a horizontal line to the right
                    self.line(px, py, x + w, py, color, thickness)
                    # Move pen up one step on the right side
                    self.line(x + w, py, x + w, py + step, color, thickness)
                    # Update pen position
                    px, py = x + w, py + step
                else:
                    # Draw a horizontal line to the left
                    self.line(px, py, x, py, color, thickness)
                    # Move pen up one step on the left side
                    self.line(x, py, x, py + step, color, thickness)
                    # Update pen position
                    px, py = x, py + step

                direction_left_to_right = not direction_left_to_right

            # Final horizontal stroke if there's a partial row left
            if py <= y + h:
                if direction_left_to_right:
                    # Last partial line to the right
                    self.line(px, py, x + w, py, color, thickness)
                else:
                    # Last partial line to the left
                    self.line(px, py, x, py, color, thickness)

        elif fill_direction.lower() == 'vertical':
            """
            We will:
            1. Start at (x, y).
            2. Go down to (x, y+h).
            3. Go right 'step' to (x+step, y+h).
            4. Go up to (x+step, y).
            5. Go right 'step' to (x+2*step, y).
            6. Repeat until we reach the right side.
            """

            # Current "pen" position
            px = x
            py = y

            # We'll alternate direction each column
            direction_top_to_bottom = True

            # Continue until the next vertical line would be outside the box’s width
            while px + step <= x + w:
                if direction_top_to_bottom:
                    # Draw a vertical line down
                    self.line(px, py, px, y + h, color, thickness)
                    # Move pen right one step at the bottom
                    self.line(px, y + h, px + step, y + h, color, thickness)
                    # Update pen position
                    px, py = px + step, y + h
                else:
                    # Draw a vertical line up
                    self.line(px, py, px, y, color, thickness)
                    # Move pen right one step at the top
                    self.line(px, y, px + step, y, color, thickness)
                    # Update pen position
                    px, py = px + step, y

                direction_top_to_bottom = not direction_top_to_bottom

            # Final vertical stroke if there's a partial column left
            if px <= x + w:
                if direction_top_to_bottom:
                    # Last partial line going down
                    self.line(px, py, px, y + h, color, thickness)
                else:
                    # Last partial line going up
                    self.line(px, py, px, y, color, thickness)

