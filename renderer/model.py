import message
from instruction import Line, CubicBezier, BladeOn, BladeOff


class InstructionBuilderModel:
    def __init__(self):
        self.instructions = []

    def receive(self, m):
        end = self.end_point()

        def add(p0, p1):
            return (p0[0] + p1[0], p0[1] + p1[1])

        if isinstance(m, message.PopInstruction):
            if len(self.instructions) > 0:
                self.instructions.pop()

        if isinstance(m, message.AddLine):
            dx = -0.5 if end[0] > 0 else 0.5
            dy = -0.5 if end[1] > 0 else 0.5
            self.instructions.append(Line(end, add(end, (dx, dy))))

        if isinstance(m, message.AddCurve):
            dx = -0.25 if end[0] > 0 else 0.25
            dy = -0.25 if end[1] > 0 else 0.25
            self.instructions.append(CubicBezier(end,
                                                 add(end, (dx, dy)),
                                                 add(end, (dx * 2, -dy)),
                                                 add(end, (dx * 4, 0))))

        if isinstance(m, message.BladeOn):
            self.instructions.append(BladeOn())

        if isinstance(m, message.BladeOff):
            self.instructions.append(BladeOff())

        if isinstance(m, message.UpdatePoint):
            length = len(self.instructions)
            if length < 1:
                return
            selected = self.instructions[length - 1]
            if isinstance(selected, Line):
                if m.index == 0:
                    selected.start = m.pos
                if m.index == 1:
                    selected.end = m.pos
            if isinstance(selected, CubicBezier):
                if m.index == 0:
                    selected.p0 = m.pos
                if m.index == 1:
                    selected.p1 = m.pos
                if m.index == 2:
                    selected.p2 = m.pos
                if m.index == 3:
                    selected.p3 = m.pos

        print([type(i) for i in self.instructions])

    def end_point(self) -> tuple[int, int]:
        i = len(self.instructions) - 1
        while i >= 0:
            inst = self.instructions[i]
            if isinstance(inst, Line):
                return inst.end
            if isinstance(inst, CubicBezier):
                return inst.p3
            i -= 1
        return (0, 0)
