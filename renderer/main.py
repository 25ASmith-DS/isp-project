import pygame as pg
import elements


pg.init()
screen = pg.display.set_mode((1280, 720))
font = pg.font.SysFont(None, 32)


class InstructionBuilderModel:
    def __init__(self):
        self.instructions = []
        self.selected = -1

    def receive(self, message):
        print(f"Received {message} message")


class Root(elements.ClickableSurface):
    def __init__(self, size, model):
        self.surface = None
        self.bg = (40, 40, 40)  # #282828

        button_size = (300, 75)
        button_fg = (235, 219, 178)
        button_bg = (80, 73, 69)
        button_child = (lambda text, message: elements.Child(
            EventEmitterButton(
                button_size,
                button_bg, button_fg,
                text, message, model),
            (0, 0)))

        self.children = [
                button_child("Pop instruction", "pop_instruction"),
                button_child("Line", "add_line"),
                button_child("Curve", "add_curve"),
                button_child("Blade off", "blade_off"),
                button_child("Blade on", "blade_on"),
                ]

        self.resize(size)

    def on_click(self, pos, button):
        if elements.click_children(self.children, pos, button):
            return

    def resize(self, new_size):
        new_width, new_height = new_size
        self.surface = pg.Surface((new_width, new_height))

        border_padding = 40
        button_padding = 10
        button_y = border_padding - button_padding

        for child in self.children:
            if isinstance(child.surface, EventEmitterButton):
                button_y += button_padding
                w, h = child.get_size()
                child.x = new_width - w - border_padding
                child.y = button_y
                child.blit_on(self.surface)
                button_y += h

    def get_size(self):
        return self.surface.get_size()

    def update(self):
        self.surface.fill(self.bg)
        for child in self.children:
            child.blit_on(self.surface)

        return self.surface


class EventEmitterButton(elements.ClickableSurface):
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
        if button == 1:
            print(f"Emitted {self.message} message")
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
            root.on_click(mouse_pos, ev.button)

    screen.blit(root.update(), (0, 0))
    pg.display.update()
