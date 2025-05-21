
class BladeOn:
    pass


class BladeOff:
    pass


class Line:
    def __init__(self, start, end):
        self.start = (float(start[0]), float(start[1]))
        self.end = (float(end[0]), float(end[1]))

    def point_on(self, t):
        return ((1-t) * self.start[0] + t * self.end[0],
                (1-t) * self.start[1] + t * self.end[1])


class CubicBezier:
    def __init__(self, p0, p1, p2, p3):
        self.p0 = (float(p0[0]), float(p0[1]))
        self.p1 = (float(p1[0]), float(p1[1]))
        self.p2 = (float(p2[0]), float(p2[1]))
        self.p3 = (float(p3[0]), float(p3[1]))

    def point_on(self, t):
        p0 = self.p0
        c0 = (1-t)*(1-t)*(1-t)
        p1 = self.p1
        c1 = 3*t*(1-t)*(1-t)
        p2 = self.p2
        c2 = 3*t*t*(1-t)
        p3 = self.p3
        c3 = t*t*t

        x = c0 * p0[0] + c1 * p1[0] + c2 * p2[0] + c3 * p3[0]
        y = c0 * p0[1] + c1 * p1[1] + c2 * p2[1] + c3 * p3[1]
        return (x, y)


def to_json_value(instruction):
    if isinstance(instruction, BladeOn):
        return 'BladeOn'
    if isinstance(instruction, BladeOff):
        return 'BladeOff'
    if isinstance(instruction, Line):
        return {'Line': {'start': instruction.start, 'end': instruction.end}}
    if isinstance(instruction, CubicBezier):
        return {'CubicBezier': {
            'p0': instruction.p0,
            'p1': instruction.p1,
            'p2': instruction.p2,
            'p3': instruction.p3}}


def from_json_value(obj):
    if isinstance(obj, str):
        if obj == "BladeOn":
            return BladeOn()
        if obj == "BladeOff":
            return BladeOff()
    if isinstance(obj, dict):
        if ["Line"] == list(obj.keys()):
            return Line(obj["Line"]["start"], obj["Line"]["end"])
        if ["CubicBezier"] == list(obj.keys()):
            return CubicBezier(obj["CubicBezier"]["p0"],
                               obj["CubicBezier"]["p1"],
                               obj["CubicBezier"]["p2"],
                               obj["CubicBezier"]["p3"])
