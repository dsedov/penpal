from PIL import Image, ImageDraw 

class Render:
    def __init__(self, canvas, dpi=300):
        self.canvas = canvas
        self.dpi = dpi
        self.canvas_size_px = (self._mm_to_pixels(canvas.canvas_size_mm[0]), self._mm_to_pixels(canvas.canvas_size_mm[1]))

    def render(self):
        self.image = Image.new("RGB", self.canvas_size_px, self.canvas.paper_color)
        for op in self.canvas.draw_stack:
            
            if op["type"] == "line":
                start_point_px = (self._mm_to_pixels(op["x1"]), self._mm_to_pixels(op["y1"]))
                end_point_px = (self._mm_to_pixels(op["x2"]), self._mm_to_pixels(op["y2"]))
                thickness_px = self._mm_to_pixels(op["thickness"])
                draw = ImageDraw.Draw(self.image)
                color = op["color"] if op["color"] else self.canvas.pen_color
                draw.line([start_point_px, end_point_px], fill=color, width=thickness_px)

            elif op["type"] == "point":
                point_px = (self._mm_to_pixels(op["x"]), self._mm_to_pixels(op["y"]))
                thickness_px = self._mm_to_pixels(op["thickness"])
                draw = ImageDraw.Draw(self.image)
                color = op["color"] if op["color"] else self.canvas.pen_color
                draw.ellipse([point_px[0]-thickness_px/2, point_px[1]-thickness_px/2, point_px[0]+thickness_px/2, point_px[1]+thickness_px/2], fill=color)

    def show(self):
        self.image.show()

    def _mm_to_pixels(self, mm):
        return round(mm * self.dpi / 25.4)    