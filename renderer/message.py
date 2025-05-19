

class PopInstruction:
    pass


class AddLine:
    pass


class AddCurve:
    pass


class BladeOn:
    pass


class BladeOff:
    pass


class UpdatePoint:
    def __init__(self, index, pos):
        self.index = index
        self.pos = pos


class BeginSimulation:
    def __init__(self, bezier_steps=10):
        self.bezier_steps = bezier_steps


class Export:
    pass


class Import:
    pass
