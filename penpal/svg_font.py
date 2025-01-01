from penpal.svg import SVG
class SVGFont:
    def __init__(self, font_path, cell_size_mm = (7, 7), ascii_start = 32, ascii_end = 96):
        self.svg = SVG(font_path)
        self.ascii_start = ascii_start
        self.ascii_end = ascii_end
        self.cell_size_mm = cell_size_mm
    

    def draw_char(self, canvas, x, y, char, scale=1.0, flip_x=False, flip_y=False, stroke_color=None, fill_color=None):
        x_lookup_offset = (char-self.ascii_start) * self.cell_size_mm[0]
        self.svg.draw(canvas, x-x_lookup_offset*scale, y, 
                      scale=scale, flip_x=flip_x, flip_y=flip_y, 
                      min_x=x_lookup_offset, min_y=0, 
                      max_x=x_lookup_offset+7, max_y=7, 
                      override_fill_color=fill_color,
                      override_stroke_color=stroke_color)
        return x+self.cell_size_mm[0] * scale, y

    def draw(self, canvas, x, y, text, scale=1.0, flip_x=False, flip_y=False, stroke_color=None, fill_color=None):
        current_x = x
        current_y = y
        for char in text:
            
            ascii_value = ord(char)
            if ascii_value < self.ascii_start or ascii_value > self.ascii_end:
                continue

            current_x, current_y = self.draw_char(canvas, current_x, current_y, ascii_value, scale=scale, flip_x=flip_x, flip_y=flip_y, stroke_color=stroke_color, fill_color=fill_color)

