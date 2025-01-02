class MinImpulseConstraint:
    def __init__(self, canvas):
        self.canvas = canvas

    def apply(self, point):
        if point["impulse"][0] < point["impulse"][1]:
            point["impulse"] = (point["impulse"][0] , 0.0)
        else:
            point["impulse"] = (0.0, point["impulse"][1])
        return point    
    
class MaxImpulseConstraint:
    def __init__(self, canvas):
        self.canvas = canvas

    def apply(self, point):
        if point["impulse"][0] > point["impulse"][1]:
            point["impulse"] = (point["impulse"][0] , 0.0)
        else:
            point["impulse"] = (0.0, point["impulse"][1])
        return point    