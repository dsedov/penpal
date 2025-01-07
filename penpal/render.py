from PIL import Image, ImageDraw 
import numpy as np
import cv2
class Render:
    def __init__(self, canvas, dpi=300):
        self.canvas = canvas
        self.dpi = dpi
        self.snapshot_images = []
        self.canvas_size_px = (self._mm_to_pixels(canvas.canvas_size_mm[0]), self._mm_to_pixels(canvas.canvas_size_mm[1]))

    def render(self, points=True):
        self.image = Image.new("RGB", self.canvas_size_px, self.canvas.paper_color)
        for op in self.canvas.draw_stack:

            if op["type"] == "line":
                start_point_px = (self._mm_to_pixels(op["x1"]), self._mm_to_pixels(op["y1"]))
                end_point_px = (self._mm_to_pixels(op["x2"]), self._mm_to_pixels(op["y2"]))
                thickness_px = self._mm_to_pixels(op["thickness"])
                draw = ImageDraw.Draw(self.image)
                color = op["color"] if op["color"] else self.canvas.pen_color
                if color == "none":
                    color = "#ffffff"
                draw.line([start_point_px, end_point_px], fill=color, width=thickness_px)

            elif op["type"] == "point" and points:
                point_px = (self._mm_to_pixels(op["x"]), self._mm_to_pixels(op["y"]))
                thickness_px = self._mm_to_pixels(op["thickness"])
                draw = ImageDraw.Draw(self.image)
                color = op["color"] if op["color"] else self.canvas.pen_color
                draw.ellipse([point_px[0]-thickness_px/2, point_px[1]-thickness_px/2, point_px[0]+thickness_px/2, point_px[1]+thickness_px/2], fill=color)

    def show(self):
        self.image.show()

    def _mm_to_pixels(self, mm):
        return round(mm * self.dpi / 25.4)    
    
    def _save_as_video(self, frames, output_path, fps=20):
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
    
    def snapshot_image(self, time_step, every = 1, save = True, folder="temp"):
        if time_step % every == 0:
            r = Render(self.canvas, dpi=150)
            r.render(points=True)
            self.snapshot_images.append(r.image)
            if save:
                r.image.save(f"{folder}/_{time_step}.png")

    def save_video(self, folder="temp", name="output", fps=20):
        if len(self.snapshot_images) > 0:
            # add reverse list to the 
            #snapshot_images.extend(reversed(snapshot_images))
            self.snapshot_images = list(reversed(self.snapshot_images)) + self.snapshot_images
            self._save_as_video(self.snapshot_images, f"{folder}/{name}.mp4", fps=fps)
            self.snapshot_images[0].save(f"{folder}/{name}.gif",
            save_all=True,           # This tells PIL to save all frames
            append_images=self.snapshot_images[1:], # This adds all other images after the first
            duration=50,             # 50ms between frames = 20fps
            loop=0                   # 0 means loop forever)
            )
