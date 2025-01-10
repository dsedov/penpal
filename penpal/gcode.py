import random, re
from penpal.utils import hex_to_color_name

class GCode:
    def __init__(self, canvas, draw_speed=8000, move_speed=30000):
        self.canvas = canvas
        self.state_x = 0
        self.state_y = 0
        self.state_z = 1.0
        self.precision = 0.01
        self.draw_speed = draw_speed
        self.move_speed = move_speed
        self.gcode = []
        self.verbose = True
        self.pen_up_z = 1.0
        self.pen_down_z = 0.0

        self.gcode.append("G21 ; Set units to millimeters")
        self.gcode.append("G90 ; Use absolute positioning")    
        # Move pen up
        self.gcode.append(f"G0 Z{self.pen_up_z}")

        self.multi_gcode = {}
        self._dwell()


    def generate(self):
        grouped_by_color = {}
        for op in self.canvas.draw_stack:
            if op["color"] not in grouped_by_color:
                grouped_by_color[op["color"]] = []
            grouped_by_color[op["color"]].append(op)

        self.saved_gcode_state = self.gcode.copy()
        for color in grouped_by_color:
            self.gcode = self.saved_gcode_state.copy()
            print(f"Color: {color}")

            for op in grouped_by_color[color]:
                if op["type"] == "line":
                    # flip y vertically 
                    line_start_x = op["x1"]
                    line_start_y = self.canvas.canvas_size_mm[1] - op["y1"] 
                    line_end_x = op["x2"]
                    line_end_y = self.canvas.canvas_size_mm[1] - op["y2"]

                    if self.verbose:
                        self.gcode.append(f"; Line from {line_start_x}, {line_start_y} to {line_end_x}, {line_end_y}")

                    if self._is_close_to(line_start_x, line_start_y, self.state_z):
                        self.gcode.append(f"G1 X{line_end_x:.2f} Y{line_end_y:.2f} F{self.draw_speed}")
                        self.state_x = line_end_x
                        self.state_y = line_end_y
                    else:
                        self.gcode.append(f"G0 Z{self.pen_up_z:.2f}")
                        self.state_z = self.pen_up_z
                        self._dwell()

                        self.gcode.append(f"G0 X{line_start_x:.2f} Y{line_start_y:.2f} F{self.move_speed}")
                        self.state_x = line_start_x
                        self.state_y = line_start_y

                        self.gcode.append(f"G0 Z{self.pen_down_z}")
                        self.state_z = self.pen_down_z
                        self._dwell()
                     
                        self.gcode.append(f"G1 X{line_end_x:.2f} Y{line_end_y:.2f} F{self.draw_speed}")
                        self.state_x = line_end_x
                        self.state_y = line_end_y

                if op["type"] == "point":
                    point_x = op["x"]
                    point_y = self.canvas.canvas_size_mm[1] - op["y"] 

                    if self.verbose:
                        self.gcode.append(f"; Point at {point_x}, {point_y}")

                    self.gcode.append(f"G0 Z{self.pen_up_z:.2f}")
                    self.state_z = self.pen_up_z
                    self._dwell()

                    self.gcode.append(f"G0 X{point_x:.2f} Y{point_y:.2f} F{self.move_speed}")
                    self.state_x = point_x
                    self.state_y = point_y

                    self.gcode.append(f"G0 Z{self.pen_down_z:.2f}")
                    self.state_z = self.pen_down_z
                    self._dwell()

            # Move pen up
            self.gcode.append(f"G0 Z{self.pen_up_z:.2f}")
            self._dwell(0.1)
            self.gcode.append(f"G0 X0 Y0")
            self.multi_gcode[color] = self.gcode.copy()

    def save(self, filename):   
        print(f"Saving gcode to {filename}")
        filename = ".".join(filename.split(".")[:-1])
        print(f"Filename stem: {filename}")
        for color in self.multi_gcode:
            self.gcode = self.multi_gcode[color].copy()
            # makes sure color contains only alphanumeric characters    
            color_for_filename = hex_to_color_name(color)
            # remove # from color_for_filename
            if isinstance(color, type(None)):
                color = "unknown"
            color = color.replace("#", "")

            with open(f"{filename}_{color}_{color_for_filename}.gcode", "w") as f:
                for line in self.gcode:
                    f.write(line + "\n")
                
    def _is_close_to(self, x, y, z=None):
        if z is None:
            return abs(self.state_x - x) < self.precision and abs(self.state_y - y) < self.precision
        else:
            return abs(self.state_x - x) < self.precision and abs(self.state_y - y) < self.precision and abs(self.state_z - z) < self.precision
    
    def _dwell(self, time_s = 0.05):
        self.gcode.append(f"G4 P{time_s}")            
    