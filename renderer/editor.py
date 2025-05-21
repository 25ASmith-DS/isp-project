import pygame as pg
import message
from elements import ClickableSurface
from model import InstructionBuilderModel, blade_radius
from instruction import Line, CubicBezier, BladeOff, BladeOn
from math import ceil


def distance_squared(p0, p1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    return (dx * dx + dy * dy)


class EditorFrame(ClickableSurface):
    def __init__(self, size: tuple[int, int], model: InstructionBuilderModel):
        self.surface = None
        self.cut_surface = None
        self.nodes_surface = None
        self.text_surface = None
        self.model = model

        self.font = pg.font.Font(pg.font.get_default_font(), 32)

        self.bg = (80, 73, 69, 255)                      # #504945
        self.fg = (235, 219, 178, 255)                   # #EBDBB2
        self.line_color_blade_on = (251, 73, 52, 255)    # #FB4934
        self.line_color_blade_off = (138, 41, 20, 255)   # #8B2914
        self.line_color_selected = (184, 167, 38, 255)   # #B8BB26
        self.cut_color = (58, 72, 24, 255)               # #3A4818
        self.world_width = self.world_height = 0
        self.world_scale = 0

        self.line_width = 0
        self.point_radius = 0
        self.point_radius_selected = 0

        self.dragging = -1
        self.camera_pos = (0, 0)  # WORLD COORDINATES
        self.anchor = (0, 0)      # WORLD COORDINATES

        self.resize(size)

    def update(self) -> pg.Surface:
        self.surface.fill(self.bg)
        self.text_surface.fill((0, 0, 0, 0))
        self.cut_surface.fill((0, 0, 0, 0))
        self.nodes_surface.fill((0, 0, 0, 0))

        instructions = self.model.instructions
        length = len(instructions)

        bezier_steps = 50

        blade_on = False
        for i in range(length - 1):
            instruction = instructions[i]
            if blade_on:
                line_color = self.line_color_blade_on
            else:
                line_color = self.line_color_blade_off

            if isinstance(instruction, Line):
                if blade_on:
                    line_length = distance_squared(instruction.start,
                                                   instruction.end) ** 0.5
                    cut_steps = ceil(2 * line_length / blade_radius)
                    cut_steps = 100
                    cut_radius = blade_radius * self.world_scale
                    for i in range(cut_steps + 1):
                        t = i / cut_steps
                        pg.draw.circle(self.cut_surface,
                                       self.cut_color,
                                       self.screencoords(instruction.point_on(t)),
                                       cut_radius)

                pg.draw.line(self.nodes_surface,
                             line_color,
                             self.screencoords(instruction.end),
                             self.screencoords(instruction.start),
                             self.line_width)
                for p in [instruction.start, instruction.end]:
                    pg.draw.circle(self.nodes_surface,
                                   line_color,
                                   self.screencoords(p),
                                   self.point_radius)
            if isinstance(instruction, CubicBezier):
                if blade_on:
                    line_length = distance_squared(instruction.p0,
                                                   instruction.p3) ** 0.5
                    cut_steps = ceil(2 * line_length / blade_radius)
                    cut_steps = 100
                    cut_radius = blade_radius * self.world_scale
                    for i in range(cut_steps + 1):
                        t = i / cut_steps
                        pg.draw.circle(self.cut_surface,
                                       self.cut_color,
                                       self.screencoords(instruction.point_on(t)),
                                       cut_radius)

                ts = [i / bezier_steps for i in range(bezier_steps + 1)]
                ps = [instruction.point_on(t) for t in ts]
                sps = [self.screencoords(p) for p in ps]
                for i in range(bezier_steps):
                    pg.draw.line(self.nodes_surface,
                                 line_color,
                                 sps[i], sps[i + 1],
                                 width=self.line_width)
                pg.draw.circle(self.nodes_surface,
                               line_color,
                               self.screencoords(instruction.p3),
                               self.point_radius)
            if isinstance(instruction, BladeOn):
                blade_on = True
            if isinstance(instruction, BladeOff):
                blade_on = False

        if length > 0:
            selected = instructions[length - 1]
            if isinstance(selected, Line):
                if blade_on:
                    line_length = distance_squared(selected.start,
                                                   selected.end) ** 0.5
                    cut_steps = ceil(2 * line_length / blade_radius)
                    cut_steps = 100
                    cut_radius = blade_radius * self.world_scale
                    for i in range(cut_steps + 1):
                        t = i / cut_steps
                        pg.draw.circle(self.cut_surface,
                                       self.cut_color,
                                       self.screencoords(selected.point_on(t)),
                                       cut_radius)
                pg.draw.line(self.nodes_surface,
                             self.line_color_selected,
                             self.screencoords(selected.end),
                             self.screencoords(selected.start),
                             self.line_width)
                pg.draw.circle(self.nodes_surface,
                               self.line_color_selected,
                               self.screencoords(selected.start),
                               self.point_radius)
                pg.draw.circle(self.nodes_surface,
                               self.line_color_selected,
                               self.screencoords(selected.end),
                               self.point_radius_selected)

                d = distance_squared(selected.start, selected.end) ** 0.5
                text = self.font.render(f"Dist: {round(d, 3)}", True, self.fg)
                self.text_surface.blit(text, (0, 30))
            if isinstance(selected, CubicBezier):
                if blade_on:
                    line_length = distance_squared(selected.p0,
                                                   selected.p3) ** 0.5
                    cut_steps = ceil(2 * line_length / blade_radius)
                    cut_steps = 100
                    cut_radius = blade_radius * self.world_scale
                    for i in range(cut_steps + 1):
                        t = i / cut_steps
                        pg.draw.circle(self.cut_surface,
                                       self.cut_color,
                                       self.screencoords(selected.point_on(t)),
                                       cut_radius)

                ts = [i / bezier_steps for i in range(bezier_steps + 1)]
                ps = [selected.point_on(t) for t in ts]
                sps = [self.screencoords(p) for p in ps]
                for i in range(bezier_steps):
                    pg.draw.line(self.nodes_surface,
                                 self.line_color_selected,
                                 sps[i], sps[i + 1],
                                 width=self.line_width)
                pg.draw.line(self.nodes_surface,
                             self.line_color_selected,
                             self.screencoords(selected.p0),
                             self.screencoords(selected.p1),
                             width=round(self.line_width/2))
                pg.draw.line(self.nodes_surface,
                             self.line_color_selected,
                             self.screencoords(selected.p2),
                             self.screencoords(selected.p3),
                             width=round(self.line_width/2))
                for p in [selected.p1, selected.p2, selected.p3]:
                    pg.draw.circle(self.nodes_surface,
                                   self.line_color_selected,
                                   self.screencoords(p),
                                   self.point_radius_selected)
                d = distance_squared(selected.p0, selected.p3) ** 0.5
                text = self.font.render(f"Dist: {round(d, 3)}", True, self.fg)
                self.text_surface.blit(text, (0, 30))

            if isinstance(selected, BladeOn):
                blade_on = True
                pg.draw.circle(self.nodes_surface,
                               self.line_color_selected,
                               self.screencoords(self.model.end_point()),
                               self.point_radius_selected)
            if isinstance(selected, BladeOff):
                blade_on = False
                pg.draw.circle(self.nodes_surface,
                               self.line_color_selected,
                               self.screencoords(self.model.end_point()),
                               self.point_radius_selected)
        else:
            pg.draw.circle(self.nodes_surface,
                           self.line_color_selected,
                           self.screencoords(0, 0),
                           self.point_radius_selected)
            text = self.font.render("Origin", True, self.fg)
            self.text_surface.blit(text, self.screencoords(0.15, -0.15))

        text = self.font.render("Blade ON" if blade_on else "Blade OFF",
                                True, self.fg)
        self.text_surface.blit(text, (0, 0))

        self.surface.blit(self.cut_surface, (0, 0))
        self.surface.blit(self.nodes_surface, (0, 0))
        self.surface.blit(self.text_surface, (0, 0))
        return self.surface

    def on_click(self, pos: tuple[int, int], button: int):
        instructions = self.model.instructions
        length = len(instructions)

        if length > 0:
            selected = instructions[length - 1]
            if isinstance(selected, Line):
                dist = distance_squared(pos, self.screencoords(selected.end))
                if dist < self.point_radius ** 2:
                    self.dragging = 1
            elif isinstance(selected, CubicBezier):
                ps = [selected.p1, selected.p2, selected.p3]
                for i in range(3):
                    dist = distance_squared(pos, self.screencoords(ps[i]))
                    if dist < self.point_radius ** 2:
                        self.dragging = i + 1

        if self.dragging == -1:
            self.anchor = self.worldcoords(pos)
            self.dragging = 0  # dragging background

    def on_raise(self, pos: tuple[int, int], button: int):
        self.dragging = -1

    def on_move(self, pos: tuple[int, int]):
        if self.dragging == 0:
            # move self.camera_pos such that:
            # self.anchor == self.worldcoords(pos)
            x, y = pos
            cam_x, cam_y = self.camera_pos
            ax, ay = self.anchor
            new_cam_x = ax - ((x - self.world_width / 2) / self.world_scale)
            new_cam_y = ay - ((y - self.world_height / 2) / -self.world_scale)
            self.camera_pos = (new_cam_x, new_cam_y)
        elif self.dragging > 0:
            msg = message.UpdatePoint(self.dragging,
                                      self.worldcoords(pos))
            self.model.receive(msg)

    def resize(self, new_size: tuple[int, int]):
        self.world_width, self.world_height = new_size
        self.world_scale = 100

        self.line_width = round(self.world_scale * (1/18))
        self.point_radius = round(self.world_scale * (1/15))
        self.point_radius_selected = round(self.world_scale * (1/8))

        self.cut_surface = pg.Surface(new_size, flags=pg.SRCALPHA)
        self.nodes_surface = pg.Surface(new_size, flags=pg.SRCALPHA)
        self.text_surface = pg.Surface(new_size, flags=pg.SRCALPHA)
        self.surface = pg.Surface(new_size)

    def get_size(self) -> tuple[int, int]:
        return self.surface.get_size()

    def screencoords(self, x, y=None):
        if isinstance(x, tuple) and y is None:
            return self.screencoords(x[0], x[1])

        cam_x, cam_y = self.camera_pos
        return ((x - cam_x) * self.world_scale + self.world_width / 2,
                -(y - cam_y) * self.world_scale + self.world_height / 2)

    def worldcoords(self, x, y=None):
        if isinstance(x, tuple) and y is None:
            return self.worldcoords(x[0], x[1])

        cam_x, cam_y = self.camera_pos
        return (((x - self.world_width / 2) / self.world_scale) + cam_x,
                ((y - self.world_height / 2) / -self.world_scale) + cam_y)
