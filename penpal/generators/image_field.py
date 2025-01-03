from PIL import Image

class ImageField:
    def __init__(self, canvas, image, dpi=300):
        self.canvas = canvas
        if isinstance(image, str):
            self.image = Image.open(image)
        else:
            self.image = image

        self.is_inversed = False
        self.dpi = dpi
        self.canvas_size_px = (self._mm_to_pixels(self.canvas.canvas_size_mm[0]), self._mm_to_pixels(self.canvas.canvas_size_mm[1]))
        self.generate()
        self.threshold_min_value = 0.0
        self.threshold_max_value = 1.0
        self.gamma_value = 1.0

    def _mm_to_pixels(self, mm):
        return int(mm * self.dpi / 25.4)

    def _pixels_to_mm(self, px):
        return int(px * 25.4 / self.dpi)

    def inversed(self):
        self.is_inversed = not self.is_inversed
        return self

    def gamma(self, value):
        self.gamma_value = value
        return self

    def generate(self):
        
        self.field = Image.new("L", self.canvas_size_px, self.canvas.paper_color)    
        # resize self.image to self.canvas_size_px
        self.image = self.image.resize(self.canvas_size_px)
        # paste self.image onto self.field
        self.field.paste(self.image, (0, 0))

    def threshold(self, min_value, max_value):
        self.threshold_min_value = min_value
        self.threshold_max_value = max_value

    def get_vector(self, x_mm, y_mm, radius=0.5):
        x = self._mm_to_pixels(x_mm)
        y = self._mm_to_pixels(y_mm)

        tx = x
        ty = y

        r_px = int(radius * self.dpi / 25.4)
        base_value = self._get_float(x, y)
        for i in range(-r_px, r_px):
            for j in range(-r_px, r_px):
                value = self._get_float(x + i, y + j)
                if value > base_value:
                    tx = x + i
                    ty = y + j
                    base_value = value

        tx_mm = self._pixels_to_mm(tx)
        ty_mm = self._pixels_to_mm(ty)
        if self.is_inversed:
            return (tx_mm - x_mm, ty_mm - y_mm)
        else:
            return (x_mm - tx_mm, y_mm - ty_mm)

    def _get_float(self, x, y):
        if x < 0 or y < 0 or x >= self.canvas_size_px[0] or y >= self.canvas_size_px[1]:
            return 0.0
        value = self.field.getpixel((x, y))
        if value / 255.0 < self.threshold_min_value:
            return 0.0
        if value / 255.0 > self.threshold_max_value:
            return 1.0
        return (self.field.getpixel((x, y)) / 255.0) ** self.gamma_value
    
    def get_float(self, x_mm, y_mm):
        x = self._mm_to_pixels(x_mm)
        y = self._mm_to_pixels(y_mm)
        if self.is_inversed:
            return 1.0 - self._get_float(x, y)
        else:   
            return self._get_float(x, y)

