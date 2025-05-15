import pygame as pg
from elements import click_children, raise_children, \
                     move_children, Child, ClickableSurface
from instruction import Line, BladeOff, BladeOn, CubicBezier
import message


def distance_squared(p0, p1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    return (dx * dx + dy * dy)


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
            self.instructions.append(Line(end, add(end, (0.5, 0.5))))

        if isinstance(m, message.AddCurve):
            self.instructions.append(CubicBezier(end,
                                                 add(end, (0.5, 0.5)),
                                                 add(end, (1.0, 0.5)),
                                                 add(end, (2.0, 0.0))))

        if isinstance(m, message.BladeOn):
            self.instructions.append(BladeOn)

        if isinstance(m, message.BladeOff):
            self.instructions.append(BladeOff)

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

        else:
            print(f"Received message \"{m}\"")

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


class Root(ClickableSurface):
    def __init__(self, size, model):
        self.surface = None
        self.bg = (40, 40, 40)       # #282828

        button_size = (300, 75)
        button_fg = (235, 219, 178)  # #EBDBB2
        button_bg = (80, 73, 69)     # #504945
        button_child = (lambda text, message: Child(
            EventEmitterButton(
                button_size,
                button_bg, button_fg,
                text, message, model),
            (0, 0)))

        self.top_right_buttons: list[Child] = [
                button_child("Pop instruction", message.PopInstruction()),
                button_child("Line", message.AddLine()),
                button_child("Curve", message.AddCurve()),
                button_child("Blade off", message.BladeOff()),
                button_child("Blade on", message.BladeOn()),
                ]

        self.editor_frame = Child(EditorFrame((0, 0), model), (0, 0))

        self.children = []
        self.children += self.top_right_buttons
        self.children += [self.editor_frame]

        self.resize(size)

    def on_click(self, pos, button):
        click_children(self.children, pos, button)

    def on_raise(self, pos, button):
        raise_children(self.children, pos, button)

    def on_move(self, pos: tuple[int, int]):
        move_children(self.children, pos)

    def resize(self, new_size):
        new_width, new_height = new_size
        self.surface = pg.Surface((new_width, new_height))

        border_padding = 40
        button_padding = 10
        button_y = border_padding - button_padding
        max_button_width = max([b.get_width() for b in self.top_right_buttons])

        editor_frame_padding = 40

        for child in self.children:
            if child in self.top_right_buttons:
                button_y += button_padding
                w, h = child.get_size()
                child.x = new_width - w - border_padding
                child.y = button_y
                button_y += h
            if child is self.editor_frame:
                frame_size = (new_width
                              - border_padding * 2
                              - max_button_width
                              - editor_frame_padding,
                              new_height
                              - border_padding * 2)
                child.resize(frame_size)
                child.x = child.y = border_padding

    def get_size(self):
        return self.surface.get_size()

    def update(self):
        self.surface.fill(self.bg)
        for child in self.children:
            child.blit_on(self.surface)

        return self.surface


class EventEmitterButton(ClickableSurface):
    def __init__(self, size, bg, fg, text, message, recv):
        self.surface = None
        self.bg = bg
        self.fg = fg
        self.message = message
        self.recv = recv

        self.text = text
        self.text_surface = font.render(self.text, True, self.fg)
        self.resize(size)

    def on_click(self, pos, button):
        pass

    def on_raise(self, pos, button):
        if button == 1:
            self.recv.receive(self.message)

    def on_move(self, pos: tuple[int, int]):
        pass

    def resize(self, new_size):
        new_width, new_height = new_size
        self.surface = pg.Surface((new_width, new_height))
        self.surface.fill(self.bg)
        sw, sh = self.surface.get_size()
        tw, th = self.text_surface.get_size()
        blit_x = (sw - tw) / 2
        blit_y = (sh - th) / 2
        self.surface.blit(self.text_surface, (blit_x, blit_y))

    def get_size(self):
        return self.surface.get_size()

    def update(self):
        return self.surface


class EditorFrame(ClickableSurface):
    def __init__(self, size: tuple[int, int], model: InstructionBuilderModel):
        self.surface = None
        self.model = model

        self.bg = (80, 73, 69)                       # #504945
        self.line_color_unselected = (251, 73, 52)   # #FB4934
        self.line_color_selected = (184, 167, 38)    # #B8BB26

        self.world_width = self.world_height = 0
        self.world_scale = 0

        self.line_width = 0
        self.point_radius = 0

        self.dragging = -1

        self.resize(size)

    def update(self) -> pg.Surface:
        self.surface.fill(self.bg)

        instructions = self.model.instructions
        length = len(instructions)

        bezier_steps = 10

        for i in range(length - 1):
            instruction = instructions[i]
            if isinstance(instruction, Line):
                pg.draw.line(self.surface,
                             self.line_color_unselected,
                             self.screencoords(instruction.end),
                             self.screencoords(instruction.start),
                             self.line_width)
                pg.draw.circle(self.surface,
                               self.line_color_unselected,
                               self.screencoords(instruction.start),
                               self.point_radius)
            if isinstance(instruction, CubicBezier):
                ts = [i / bezier_steps for i in range(bezier_steps + 1)]
                ps = [instruction.point_on(t) for t in ts]
                sps = [self.screencoords(p) for p in ps]
                for i in range(bezier_steps):
                    pg.draw.line(self.surface,
                                 self.line_color_unselected,
                                 sps[i], sps[i + 1],
                                 width=self.line_width)

        if length > 0:
            selected = instructions[length - 1]
            if isinstance(selected, Line):
                pg.draw.line(self.surface,
                             self.line_color_selected,
                             self.screencoords(selected.end),
                             self.screencoords(selected.start),
                             self.line_width)
                pg.draw.circle(self.surface,
                               self.line_color_selected,
                               self.screencoords(selected.end),
                               self.point_radius)
            if isinstance(selected, CubicBezier):
                ts = [i / bezier_steps for i in range(bezier_steps + 1)]
                ps = [selected.point_on(t) for t in ts]
                sps = [self.screencoords(p) for p in ps]
                for i in range(bezier_steps):
                    pg.draw.line(self.surface,
                                 self.line_color_selected,
                                 sps[i], sps[i + 1],
                                 width=self.line_width)
                pg.draw.line(self.surface,
                             self.line_color_selected,
                             self.screencoords(selected.p0),
                             self.screencoords(selected.p1),
                             width=round(self.line_width/2))
                pg.draw.line(self.surface,
                             self.line_color_selected,
                             self.screencoords(selected.p2),
                             self.screencoords(selected.p3),
                             width=round(self.line_width/2))
                for p in [selected.p1, selected.p2, selected.p3]:
                    pg.draw.circle(self.surface,
                                   self.line_color_selected,
                                   self.screencoords(p),
                                   self.point_radius)

        return self.surface

    def on_click(self, pos: tuple[int, int], button: int):
        instructions = self.model.instructions
        length = len(instructions)
        if length < 1:
            return

        selected = instructions[length - 1]
        if isinstance(selected, Line):
            dist = distance_squared(pos, self.screencoords(selected.end))
            if dist < self.point_radius ** 2:
                self.dragging = 1
        if isinstance(selected, CubicBezier):
            ps = [selected.p1, selected.p2, selected.p3]
            for i in range(3):
                dist = distance_squared(pos, self.screencoords(ps[i]))
                if dist < self.point_radius ** 2:
                    self.dragging = i + 1

    def on_raise(self, pos: tuple[int, int], button: int):
        self.dragging = -1

    def on_move(self, pos: tuple[int, int]):
        if self.dragging != -1:
            msg = message.UpdatePoint(self.dragging,
                                      self.worldcoords(pos))
            self.model.receive(msg)

    def resize(self, new_size: tuple[int, int]):
        self.world_width, self.world_height = new_size
        self.world_scale = 100

        self.line_width = round(self.world_scale * (1/18))
        self.point_radius = round(self.world_scale * (1/10))

        self.surface = pg.Surface(new_size)

    def get_size(self) -> tuple[int, int]:
        return self.surface.get_size()

    def screencoords(self, x, y=None):
        if isinstance(x, tuple) and y is None:
            return self.screencoords(x[0], x[1])
        return (x * self.world_scale + self.world_width / 2,
                -y * self.world_scale + self.world_height / 2)

    def worldcoords(self, x, y=None):
        if isinstance(x, tuple) and y is None:
            return self.worldcoords(x[0], x[1])
        return ((x - self.world_width / 2) / self.world_scale,
                (y - self.world_height / 2) / -self.world_scale)


if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((1280, 720))
    font = pg.font.SysFont(None, 32)

    screen_size = (screen.get_width(), screen.get_height())
    root = Root(screen_size, InstructionBuilderModel())

    done = False
    while not done:
        mouse_pos = pg.mouse.get_pos()
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                done = True
            if ev.type == pg.WINDOWRESIZED:
                root.resize((ev.x, ev.y))
            if ev.type == pg.MOUSEBUTTONUP:
                root.on_raise(mouse_pos, ev.button)
            if ev.type == pg.MOUSEBUTTONDOWN:
                root.on_click(mouse_pos, ev.button)
            if ev.type == pg.MOUSEMOTION:
                root.on_move(mouse_pos)

        screen.blit(root.update(), (0, 0))
        pg.display.update()
