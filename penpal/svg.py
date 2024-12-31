from svgpathtools import svg2paths, Line, CubicBezier, Path, Arc
import math
class SVG:
    def __init__(self, filename):
        self.filename = filename
        self.paths, self.attributes = svg2paths(filename)
        with open(filename, 'r') as f:
            svg_content = f.read()
        self.class_colors = self.parse_css_classes(svg_content)

    def draw(self, canvas, x, y, scale=1.0, flip_x=False, flip_y=False):
        """
        Draws each segment in self.paths to the given canvas, applying
        translation (x, y), optional scaling, and optional flipping of X and Y.
        """
        
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
        
        for path, attr in zip(self.paths, self.attributes):

            # Get the stroke color from attributes
            stroke_color = None
            if 'style' in attr:
                # Sometimes color is in the style attribute like "stroke:#000000"
                style_dict = dict(item.split(":") for item in attr['style'].split(";"))
                if 'stroke' in style_dict:
                    stroke_color = style_dict['stroke']
            elif 'stroke' in attr:
                # Sometimes color is directly in the stroke attribute
                stroke_color = attr['stroke']
            elif 'class' in attr:
                class_name = attr['class'].strip()
                if class_name in self.class_colors:
                    stroke_color = self.class_colors[class_name]

            for segment in path:
                if isinstance(segment, Line):
                    print("line")
                    # Original points
                    sx, sy = segment.start.real, segment.start.imag
                    ex, ey = segment.end.real, segment.end.imag
                    
                    # Transform them
                    sx_t, sy_t = transform_point(sx, sy, x, y, scale, flip_x, flip_y)
                    ex_t, ey_t = transform_point(ex, ey, x, y, scale, flip_x, flip_y)
                    
                    # Draw
                    canvas.line(sx_t, sy_t, ex_t, ey_t, color=stroke_color)
                
                elif isinstance(segment, CubicBezier):
                    print("cubic bezier")
                    # Original points
                    sx,  sy  = segment.start.real,    segment.start.imag
                    c1x, c1y = segment.control1.real, segment.control1.imag
                    c2x, c2y = segment.control2.real, segment.control2.imag
                    ex,  ey  = segment.end.real,      segment.end.imag
                    
                    # Transform them
                    sx_t,  sy_t  = transform_point(sx,  sy,  x, y, scale, flip_x, flip_y)
                    c1x_t, c1y_t = transform_point(c1x, c1y, x, y, scale, flip_x, flip_y)
                    c2x_t, c2y_t = transform_point(c2x, c2y, x, y, scale, flip_x, flip_y)
                    ex_t,  ey_t  = transform_point(ex,  ey,  x, y, scale, flip_x, flip_y)
                    
                    # Draw
                    canvas.cubic_bezier(
                        sx_t,  sy_t,
                        c1x_t, c1y_t,
                        c2x_t, c2y_t,
                        ex_t,  ey_t,
                        color=stroke_color
                    )

                elif isinstance(segment, Arc):
                    print("arc")
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
                        px_t, py_t = transform_point(px, py, x, y, scale, flip_x, flip_y)
                        arc_points.append((px_t, py_t))

                    # Now connect consecutive points with lines
                    for i in range(len(arc_points) - 1):
                        sx_t, sy_t = arc_points[i]
                        ex_t, ey_t = arc_points[i + 1]
                        canvas.line(sx_t, sy_t, ex_t, ey_t, color=stroke_color)

                elif isinstance(segment, Path):
                    print("path")
                    # Example: If Path is line-like, transform similarly
                    sx, sy = segment.start.real, segment.start.imag
                    ex, ey = segment.end.real, segment.end.imag
                    
                    sx_t, sy_t = transform_point(sx, sy, x, y, scale, flip_x, flip_y)
                    ex_t, ey_t = transform_point(ex, ey, x, y, scale, flip_x, flip_y)
                    
                    canvas.line(sx_t, sy_t, ex_t, ey_t, color=stroke_color)
                
                else:
                    print(f"unknown segment: {type(segment)}")

    def save(self, canvas):
        pass

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