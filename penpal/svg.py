from svgpathtools import svg2paths, Line, CubicBezier, Path, Arc
import math
class SVG:
    def __init__(self, filename):
        self.filename = filename
        self.paths, self.attributes = svg2paths(filename)
        with open(filename, 'r') as f:
            svg_content = f.read()
        self.class_colors = self.parse_css_classes(svg_content)

    def get_shape_bounds(path, x=0.0, y=0.0, scale=1, flip_x=False, flip_y=False):
        """Get min/max coordinates of the shape"""
        points = []
        for segment in path:
            if isinstance(segment, Line):
                start_x_t, start_y_t = SVG.transform_point(segment.start.real, segment.start.imag, x, y, scale, flip_x, flip_y)
                end_x_t, end_y_t = SVG.transform_point(segment.end.real, segment.end.imag, x, y, scale, flip_x, flip_y)
                points.append((start_x_t, start_y_t))
                points.append((end_x_t, end_y_t))
        
        xs, ys = zip(*points)
        return min(xs), max(xs), min(ys), max(ys)
    
    def transform_point(px, py, tx, ty, s=1.0, fx=False, fy=False):
        """
        Transforms the point (px, py) by optionally flipping X/Y,
        then scaling by s, then translating by (tx, ty).
        """
        # Flip
        if fx:
            px = -px
        if fy:
            py = -py
        # Scale
        px *= s
        py *= s
        # Translate
        px += tx
        py += ty
        return px, py
    def fill_shape_with_lines(path, canvas, pen_width, stroke_color="white", 
                    x=0, y=0, scale=1, flip_x=False, flip_y=False):
        """Fill shape with parallel lines"""
        # Get bounds of the shape
        min_x, max_x, min_y, max_y = SVG.get_shape_bounds(path, x, y, scale, flip_x, flip_y)
        
        # Calculate number of lines needed based on pen width
        spacing = pen_width * 0.8

        current_x = min_x
        while current_x <= max_x-0.01:
            # Check if line intersects with shape and get intersection points
            intersections = []
            for segment in path:
                if isinstance(segment, Line):
                    # Create vertical line segment
                    fill_line = Line(
                        complex(current_x, min_y - 0.1), 
                        complex(current_x, max_y + 0.1))
                    
                    transformd_line_start_x, tranformedd_line_start_y = SVG.transform_point(
                        segment.start.real, segment.start.imag, x, y, scale, flip_x, flip_y)
                    transformd_line_end_x, tranformedd_line_end_y = SVG.transform_point(
                        segment.end.real, segment.end.imag, x, y, scale, flip_x, flip_y)

                    transformed_segment = Line( 
                        complex(transformd_line_start_x, tranformedd_line_start_y), 
                        complex(transformd_line_end_x, tranformedd_line_end_y))

                    # Skip if lines are parallel
                    if abs(transformed_segment.start.real - transformed_segment.end.real) < 1e-10:
                        if abs(transformed_segment.start.real - current_x) < 1e-10:
                            intersections.extend([transformed_segment.start.imag, transformed_segment.end.imag])
                        continue
                        
                    # Find intersection
                    ints = transformed_segment.intersect(fill_line)
                    if ints:
                        # Get intersection point by evaluating the transformed segment at t1
                        if isinstance(ints, tuple):
                            t1 = ints[0]
                            intersection_point = transformed_segment.point(t1)
                            intersections.append(intersection_point.imag)
                        else:
                            for t1, _ in ints:
                                intersection_point = transformed_segment.point(t1)
                                intersections.append(intersection_point.imag)

                else:
                    print(f"unknown segment: {type(segment)}")
            
            # Sort intersections and draw line segments between pairs
            if intersections:
                intersections = sorted(set(intersections))
                for i in range(0, len(intersections)-1, 2):
                    start_y = intersections[i]
                    end_y = intersections[i+1]
                    canvas.line(current_x, start_y, current_x, end_y, color=stroke_color)
            
            current_x += spacing




    def draw(self, canvas, x, y, scale=1.0, pen_width=0.5, flip_x=False, flip_y=False, override_stroke_color=None, override_fill_color=None, min_x=None, min_y=None, max_x=None, max_y=None):
        """
        Draws each segment in self.paths to the given canvas, applying
        translation (x, y), optional scaling, and optional flipping of X and Y.
        """
        scale = scale * (1.0 / 2.834646) # from illustrator to mm
        
        
        for path, attr in zip(self.paths, self.attributes):

            if min_x is not None and min_y is not None and max_x is not None and max_y is not None:
                s_min_x, s_max_x, s_min_y, s_max_y = SVG.get_shape_bounds(path, 0, 0, 1.0/2.834646)
                if s_min_x < min_x or s_max_x > max_x or s_min_y < min_y or s_max_y > max_y:
                    continue
            
            # Get the stroke color from attributes
            stroke_color = None
            fill_color = None

            if 'style' in attr:
                style_dict = dict(
                    item.strip().split(':') 
                    for item in attr['style'].split(';') 
                    if item.strip()  # Skip empty strings
                )
                if 'stroke' in style_dict:
                    stroke_color = style_dict['stroke'].strip()
                if 'fill' in style_dict:
                    fill_color = style_dict['fill'].strip()
            if 'stroke' in attr:
                # Sometimes color is directly in the stroke attribute
                stroke_color = attr['stroke']
            if 'fill' in attr:
                fill_color = attr['fill']
            if 'class' in attr:
                class_name = attr['class'].strip()
                if class_name in self.class_colors:
                    stroke_color = self.class_colors[class_name]

            if override_stroke_color:
                stroke_color = override_stroke_color
            if override_fill_color:
                fill_color = override_fill_color
            

            if stroke_color or not fill_color:
                for segment in path:
                    if isinstance(segment, Line):
                        
                        # Original points
                        sx, sy = segment.start.real, segment.start.imag
                        ex, ey = segment.end.real,   segment.end.imag
                        
                        # Transform them
                        sx_t, sy_t = SVG.transform_point(sx, sy, x, y, scale, flip_x, flip_y)
                        ex_t, ey_t = SVG.transform_point(ex, ey, x, y, scale, flip_x, flip_y)

                        canvas.line(sx_t, sy_t, ex_t, ey_t, color=stroke_color, thickness=pen_width)
                    
                    elif isinstance(segment, CubicBezier):
                        # Original points
                        sx,  sy  = segment.start.real,    segment.start.imag
                        c1x, c1y = segment.control1.real, segment.control1.imag
                        c2x, c2y = segment.control2.real, segment.control2.imag
                        ex,  ey  = segment.end.real,      segment.end.imag
                        
                        # Transform them
                        sx_t,  sy_t  = SVG.transform_point(sx,  sy,  x, y, scale, flip_x, flip_y)
                        c1x_t, c1y_t = SVG.transform_point(c1x, c1y, x, y, scale, flip_x, flip_y)
                        c2x_t, c2y_t = SVG.transform_point(c2x, c2y, x, y, scale, flip_x, flip_y)
                        ex_t,  ey_t  = SVG.transform_point(ex,  ey,  x, y, scale, flip_x, flip_y)
                        
                        # Draw
                        canvas.cubic_bezier(
                            sx_t,  sy_t,
                            c1x_t, c1y_t,
                            c2x_t, c2y_t,
                            ex_t,  ey_t,
                            color=stroke_color,
                            thickness=pen_width
                        )

                    elif isinstance(segment, Arc):
                        # We'll approximate the arc by sampling points along its parameter [0..1].
                        # Then we draw small line segments between consecutive sample points.

                        # Choose how many segments you want for the arc approximation:
                        arc_length = segment.length()  # svgpathtools can compute arc length
        
                        # 2) Determine how many segments we need based on self.tolerance
                        if arc_length < 1e-10:
                            # Degenerate arc, treat like a point or a line
                            n_points = 1
                        else:
                            # A simple heuristic: enough segments so each sub-segment is ~tolerance
                            n_points = max(4, int(math.ceil(arc_length / (canvas.tolerance / scale))))

                        # Collect the transformed sample points
                        arc_points = []
                        for i in range(n_points + 1):
                            t = i / n_points
                            # Use Arc.point(t) to get the complex coordinate at parameter t
                            px = segment.point(t).real
                            py = segment.point(t).imag

                            # Transform (flip, scale, translate)
                            px_t, py_t = SVG.transform_point(px, py, x, y, scale, flip_x, flip_y)
                            arc_points.append((px_t, py_t))

                        # Now connect consecutive points with lines
                        for i in range(len(arc_points) - 1):
                            sx_t, sy_t = arc_points[i]
                            ex_t, ey_t = arc_points[i + 1]
                            canvas.line(sx_t, sy_t, ex_t, ey_t, color=stroke_color, thickness=pen_width)

                    elif isinstance(segment, Path):
                        print(f"path: {segment}")
                        # Example: If Path is line-like, transform similarly
                        sx, sy = segment.start.real, segment.start.imag
                        ex, ey = segment.end.real, segment.end.imag
                        
                        sx_t, sy_t = SVG.transform_point(sx, sy, x, y, scale, flip_x, flip_y)
                        ex_t, ey_t = SVG.transform_point(ex, ey, x, y, scale, flip_x, flip_y)
                        
                        canvas.line(sx_t, sy_t, ex_t, ey_t, color=stroke_color, thickness=pen_width)
                    
                    else:
                        print(f"unknown segment: {type(segment)}")
            if fill_color:
                SVG.fill_shape_with_lines(path, canvas, pen_width=pen_width, 
                         stroke_color=fill_color, x=x, y=y, scale=scale, 
                         flip_x=flip_x, flip_y=flip_y)

    def save(self, canvas, filename):
        """
        Saves the drawing operations as SVG files, creating separate files for each color.
        Converts millimeter coordinates to pixels (96 DPI) for better compatibility with SVG editors.
        
        Args:
            canvas: The canvas object containing the draw stack
            filename: Base filename to save the SVG(s)
        """
        # MM to PX conversion (96 DPI)
        MM_TO_PX = 3.7795275591

        # Group operations by color
        grouped_by_color = {}
        for op in canvas.draw_stack:
            if op["color"] not in grouped_by_color:
                grouped_by_color[op["color"]] = []
            grouped_by_color[op["color"]].append(op)
        
        # Remove extension from filename
        filename_base = ".".join(filename.split(".")[:-1])
        
        for color in grouped_by_color:
            operations = grouped_by_color[color]
            
            # Convert canvas size to pixels
            canvas_width_px = canvas.canvas_size_mm[0] * MM_TO_PX
            canvas_height_px = canvas.canvas_size_mm[1] * MM_TO_PX
            
            # Generate SVG content
            svg_lines = []
            svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
            svg_lines.append('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" ' +
                            f'width="{canvas.canvas_size_mm[0]}mm" ' +
                            f'height="{canvas.canvas_size_mm[1]}mm" ' +
                            f'viewBox="0 0 {canvas_width_px} {canvas_height_px}">')
            
            # Add style definitions
            svg_lines.append('<style type="text/css">')
            svg_lines.append('  .plotted-line { stroke-linecap: round; }')
            svg_lines.append('</style>')
            
            # Process each drawing operation
            for op in operations:
                if op["type"] == "line":
                    svg_lines.append(
                        f'  <line class="plotted-line" ' +
                        f'x1="{op["x1"] * MM_TO_PX:.2f}" ' +
                        f'y1="{op["y1"] * MM_TO_PX:.2f}" ' +
                        f'x2="{op["x2"] * MM_TO_PX:.2f}" ' +
                        f'y2="{op["y2"] * MM_TO_PX:.2f}" ' +
                        f'stroke="{color if color else "black"}" ' +
                        f'stroke-width="{op.get("thickness", 0.5) * MM_TO_PX}"/>'
                    )
                elif op["type"] == "point":
                    # For points, create a small circle
                    svg_lines.append(
                        f'  <circle ' +
                        f'cx="{op["x"] * MM_TO_PX:.2f}" ' +
                        f'cy="{op["y"] * MM_TO_PX:.2f}" ' +
                        f'r="{op.get("thickness", 0.5) * MM_TO_PX}" ' +
                        f'fill="{color if color else "black"}"/>'
                    )
                elif op["type"] == "cubic_bezier":
                    svg_lines.append(
                        f'  <path class="plotted-line" ' +
                        f'd="M {op["x1"] * MM_TO_PX:.2f},{op["y1"] * MM_TO_PX:.2f} ' +
                        f'C {op["cx1"] * MM_TO_PX:.2f},{op["cy1"] * MM_TO_PX:.2f} ' +
                        f'{op["cx2"] * MM_TO_PX:.2f},{op["cy2"] * MM_TO_PX:.2f} ' +
                        f'{op["x2"] * MM_TO_PX:.2f},{op["y2"] * MM_TO_PX:.2f}" ' +
                        f'stroke="{color if color else "black"}" ' +
                        f'fill="none" ' +
                        f'stroke-width="{op.get("thickness", 0.5) * MM_TO_PX}"/>'
                    )
            
            svg_lines.append('</svg>')
            
            # Create filename with color
            if color:
                color_str = color.replace('#', '')
                try:
                    from penpal.utils import hex_to_color_name
                    color_name = hex_to_color_name(color)
                    output_filename = f"{filename_base}_{color_str}_{color_name}.svg"
                except ImportError:
                    output_filename = f"{filename_base}_{color_str}.svg"
            else:
                output_filename = f"{filename_base}_unknown.svg"
            
            # Write the SVG file
            with open(output_filename, 'w') as f:
                f.write('\n'.join(svg_lines))

    def parse_css_classes(self, svg_content):
        """
        Parse CSS classes from SVG content to get stroke colors.
        Returns a dictionary mapping class names to stroke colors.
        """
        import re
        from xml.dom import minidom

        doc = minidom.parseString(svg_content)
        style_elements = doc.getElementsByTagName('style')
        
        class_colors = {}
        for style in style_elements:
            css_text = style.firstChild.data
            # Find class definitions
            class_matches = re.finditer(r'\.([^{]+){([^}]+)}', css_text)
            for match in class_matches:
                class_name = match.group(1).strip()
                style_block = match.group(2)
                # Find stroke color in style block
                stroke_match = re.search(r'stroke:\s*([^;]+)', style_block)
                if stroke_match:
                    class_colors[class_name] = stroke_match.group(1).strip()
        
        doc.unlink()
        return class_colors