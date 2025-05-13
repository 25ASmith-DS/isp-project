import pygame as pg
import ui


pg.init()
screen = pg.display.set_mode((800, 600))
font = pg.font.SysFont(None, 20)


class Root(ui.ClickableSurface):
    def __init__(self, width, height):
        self.surface = pg.Surface((width, height))
        self.children: list[ui.Child] = [
                ui.Child(DebugButton(200, 100), width - 300, 200)
                ]

    def on_click(self, x, y, button):
        if ui.click_children(self.children, x, y, button):
            return

    def resize(self, new_width, new_height):
        self.surface = pg.Surface((new_width, new_height))

    def get_size(self):
        return self.surface.get_size()

    def update(self):
        self.surface.fill((36, 36, 36))
        for child in self.children:
            self.surface.blit(child.surface.update(), (child.x, child.y))

        return self.surface


class DebugButton(ui.ClickableSurface):
    def __init__(self, width, height):
        self.surface = pg.Surface((width, height))
        self.text = "Debug"
        self.text_surface = font.render(self.text, True, (255, 255, 255))
        self.children = []

    def on_click(self, x, y, button):
        if button == 1:
            print(f"Debug button clicked at {x}, {y}")

    def resize(self, new_width, new_height):
        self.surface = pg.Surface((new_width, new_height))

    def get_size(self):
        return self.surface.get_size()

    def update(self):
        self.surface.fill((0, 0, 0))
        blit_x = self.surface.get_width() - self.text_surface.get_width()
        blit_y = self.surface.get_height() - self.text_surface.get_height()
        self.surface.blit(self.text_surface, (blit_x / 2, blit_y / 2))
        for child in self.children:
            self.surface.blit(child.surface.update(), (child.x, child.y))

        return self.surface


root = Root(screen.get_width(), screen.get_height())


done = False
while not done:
    mouse_x, mouse_y = pg.mouse.get_pos()
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            done = True
        if ev.type == pg.WINDOWRESIZED:
            root.resize(ev.x, ev.y)
        if ev.type == pg.MOUSEBUTTONDOWN:
            root.on_click(mouse_x, mouse_y, ev.button)
        # print(pg.event.event_name(ev.type), ev.__dict__)

    screen.blit(root.update(), (0, 0))
    pg.display.update()
