import pygame as pg
from elements import click_children, raise_children, \
                     move_children, Child, ClickableSurface
from model import InstructionBuilderModel
from editor import EditorFrame
import message


class Root(ClickableSurface):
    def __init__(self, size, model):
        self.surface = None
        self.bg = (40, 40, 40)       # #282828

        trb_size = (300, 75)
        button_fg = (235, 219, 178)  # #EBDBB2
        button_bg = (80, 73, 69)     # #504945
        font = pg.font.Font(pg.font.get_default_font(), 32)
        button_child = (lambda size, text, message: Child(
            EventEmitterButton(
                size,
                button_bg, button_fg,
                text, font, message, model),
            (0, 0)))

        self.top_right_buttons: list[Child] = [
                button_child(trb_size, "Pop instruction", message.PopInstruction()),
                button_child(trb_size, "Line", message.AddLine()),
                button_child(trb_size, "Curve", message.AddCurve()),
                button_child(trb_size, "Blade off", message.BladeOff()),
                button_child(trb_size, "Blade on", message.BladeOn()),
                ]

        brb_size = (300, 75)
        self.bottom_right_buttons: list[Child] = [
                button_child(brb_size, "Export", message.Export()),
                button_child(brb_size, "Import", message.Import())
                ]

        self.editor_frame = Child(EditorFrame((0, 0), model), (0, 0))

        self.children = []
        self.children += self.top_right_buttons
        self.children += self.bottom_right_buttons
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
        tr_button_y = border_padding - button_padding
        br_button_y = new_height - border_padding - button_padding
        max_button_width = max([b.get_width() for b in self.top_right_buttons])

        editor_frame_padding = 40

        for child in self.children:
            if child in self.top_right_buttons:
                tr_button_y += button_padding
                w, h = child.get_size()
                child.x = new_width - w - border_padding
                child.y = tr_button_y
                tr_button_y += h

            if child in self.bottom_right_buttons:
                w, h = child.get_size()
                br_button_y -= h
                child.x = new_width - w - border_padding
                child.y = br_button_y
                br_button_y -= button_padding

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
    def __init__(self, size, bg, fg, text, font, message, recv):
        self.surface = None
        self.bg = bg
        self.fg = fg
        self.message = message
        self.recv = recv
        self.font = font

        self.text = text
        self.text_surface = self.font.render(self.text, True, self.fg)
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




if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((1600, 900))

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
