class Merge:
    def __init__(self):
        pass

    def apply(self, canvas_1, canvas_2):
        new_canvas = canvas_1.clone()
        new_canvas.merge_with(canvas_2)
        return new_canvas
