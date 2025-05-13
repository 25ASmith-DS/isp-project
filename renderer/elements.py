import pygame as pg


class ClickableSurface:
    def __init__(self, size: tuple[int, int]):
        raise NotImplementedError()

    def update(self) -> pg.Surface:
        raise NotImplementedError()

    def on_click(self, pos: tuple[int, int], button: int):
        raise NotImplementedError()

    def resize(self, new_size: tuple[int, int]):
        raise NotImplementedError()

    def get_size(self) -> tuple[int, int]:
        raise NotImplementedError()

    def get_width(self):
        return self.get_size()[0]

    def get_height(self):
        return self.get_size()[1]


class Child:
    def __init__(self, surface, pos):
        self.surface = surface
        self.x, self.y = pos

    def blit_on(self, target_surface: pg.Surface):
        target_surface.blit(self.surface.update(), (self.x, self.y))

    def get_pos(self) -> tuple[int, int]:
        return (self.x, self.y)

    def set_pos(self, pos: tuple[int, int]):
        self.x += pos[0]
        self.y += pos[1]

    def collide_point(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        cx, cy = self.get_pos()
        w, h = self.surface.get_size()
        return (cx <= x <= cx + w) and (cy <= y <= cy + h)

    def point_on_child(self, pos: tuple[int, int]):
        (x, y) = pos
        return (x - self.x, y - self.y)

    def update(self) -> pg.Surface:
        return self.surface.update()

    def on_click(self, pos: tuple[int, int], button: int):
        self.surface.on_click(pos, button)

    def resize(self, new_width: int, new_height: int):
        self.surface.resize(new_width, new_height)

    def get_size(self) -> tuple[int, int]:
        return self.surface.get_size()

    def get_width(self):
        return self.surface.get_width()

    def get_height(self):
        return self.surface.get_height()


def click_children(children, pos, button) -> bool:
    x, y = pos
    for child in children:
        if child.collide_point(pos):
            child.surface.on_click((x - child.x, y - child.y), button)
            return True
    return False
