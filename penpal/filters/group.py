class Group:
    def __init__(self, canvas):
        self.canvas = canvas
        self.ops = []

    def where(self, rule):
        for op in self.canvas.draw_stack:
            if rule(op):
                self.ops.append(op)
        return self

    def expand_pids(self):
        ids = []
        for op in self.ops:
            ids.append(op["pid"])
        pid_set = set(ids)
        self.ops = [op for op in self.canvas.draw_stack if op["pid"] in pid_set]
        return self

    def remove_pids(self, pids):
        self.ops = [op for op in self.ops if op["pid"] not in pids]
        return self

    def all_pids(self):
        pids = []
        for op in self.ops:
            pids.append(op["pid"])
        return list(set(pids))

