import pygame as pg
from dataclasses import dataclass


class ClickableSurface:
    def __init__(self, width: int, height: int):
        raise NotImplementedError()

    def update(self) -> pg.Surface:
        raise NotImplementedError()

    def on_click(self, x: int, y: int, button: int):
        raise NotImplementedError()

    def resize(self, new_width: int, new_height: int):
        raise NotImplementedError()

    def get_size(self) -> tuple[int, int]:
        raise NotImplementedError()


@dataclass
class Child:
    surface: ClickableSurface
    x: int
    y: int


def click_children(children, x, y, button) -> bool:
    for child in children:
        size = child.surface.get_size()
        rect = pg.Rect(child.x, child.y, size[0], size[1])
        if rect.collidepoint(x, y):
            child.surface.on_click(x - child.x, y - child.y, button)
            return True
    return False
