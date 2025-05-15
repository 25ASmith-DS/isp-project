import pygame as pg
from elements import click_children, raise_children, Child, ClickableSurface
from instruction import Line, BladeOff, BladeOn, CubicBezier


class InstructionBuilderModel:
    def __init__(self):
        self.instructions = []

    def receive(self, message):
        end = self.end_point()
        print(end)
        match message:
            case "add_line":
                self.instructions.append(Line(end, tuple(c + 1 for c in end)))
            case "add_curve":
                pass
            case "blade_on":
                self.instructions.append(BladeOn)
            case "blade_off":
                self.instructions.append(BladeOff)
            case "pop_instruction":
                if len(self.instructions) > 0:
                    self.instructions.pop()
            case m:
                print(f"Received message \"{m}\"")
        print(self.instructions)

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
        self.bg = (40, 40, 40)  # #282828

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
                button_child("Pop instruction", "pop_instruction"),
                button_child("Line", "add_line"),
                button_child("Curve", "add_curve"),
                button_child("Blade off", "blade_off"),
                button_child("Blade on", "blade_on"),
                ]

        self.editor_frame = Child(EditorFrame((0, 0), model), (0, 0))

        self.children = []
        self.children += self.top_right_buttons
        self.children += [self.editor_frame]

        self.resize(size)

    def on_click(self, pos, button):
        if click_children(self.children, pos, button):
            return

    def on_raise(self, pos, button):
        if raise_children(self.children, pos, button):
            return

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

        self.bg = (80, 73, 69)  # #504945
        self.world_width = self.world_height = 0
        self.world_scale = 0

        self.resize(size)

    def update(self) -> pg.Surface:
        self.surface.fill(self.bg)
        for instruction in self.model.instructions:
            if isinstance(instruction, Line):
                line_color_unselected = (251, 73, 52)   # #FB4934
                line_color_selected = (184, 167, 38)  # #B8BB26
                inst_list = self.model.instructions
                if instruction is inst_list[len(inst_list) - 1]:
                    line_color = line_color_selected
                else:
                    line_color = line_color_unselected
                pg.draw.line(self.surface,
                             line_color,
                             self.worldcoords(instruction.end),
                             self.worldcoords(instruction.start),
                             round(self.world_scale * (1/20)))
        return self.surface

    def on_click(self, pos: tuple[int, int], button: int):
        pass

    def on_raise(self, pos: tuple[int, int], button: int):
        pass

    def resize(self, new_size: tuple[int, int]):
        self.world_width, self.world_height = new_size
        self.world_scale = 100
        self.surface = pg.Surface(new_size)

    def get_size(self) -> tuple[int, int]:
        return self.surface.get_size()

    def worldcoords(self, x, y=None):
        if isinstance(x, tuple) and y is None:
            return self.worldcoords(x[0], x[1])
        return (x * self.world_scale + self.world_width / 2,
                -y * self.world_scale + self.world_height / 2)


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

        screen.blit(root.update(), (0, 0))
        pg.display.update()
