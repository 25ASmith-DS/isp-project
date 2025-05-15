

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
