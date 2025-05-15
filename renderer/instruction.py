
class BladeOn:
    pass


class BladeOff:
    pass


class Line:
    def __init__(self, start, end):
        self.start = (float(start[0]), float(start[1]))
        self.end = (float(end[0]), float(end[1]))


class CubicBezier:
    def __init__(self, p0, p1, p2, p3):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

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
