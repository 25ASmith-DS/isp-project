import pygame as pg
from time import time_ns as time
import json


class Duration:
    def __init__(self, obj: dict):
        self.secs = obj['secs']
        self.nanos = obj['nanos']

    def seconds(self):
        return self.secs + self.nanos / (10 ** 9)


class SimState:
    def __init__(self, obj):
        self.robot_x = obj['robot_x']
        self.robot_y = obj['robot_y']
        self.robot_theta = obj['robot_theta']
        self.debug = obj['debug']


class SimOutput:
    def __init__(self, obj: dict):
        self.states: list[SimState] = [SimState(s) for s in obj['states']]
        self.delta_time: Duration = Duration(obj['delta_time']).seconds()
        self.wheel_distance: float = obj["wheel_distance"]
        self.wheel_radius: float = obj["wheel_radius"]
        self.max_motor_speed: float = obj["max_motor_speed"]


path = "../simulation/tests/basic_goto.sim"
with open(path, 'r') as file:
    camera_text = file.read()
simulation_output = SimOutput(json.loads(camera_text))
sim_dt = simulation_output.delta_time


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WORLD_WIDTH = 800
WORLD_HEIGHT = 600
WORLD_SCALE = 20  # pixels per meter

ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

font = pg.font.Font(pg.font.get_default_font(), 18)
sprite = pg.image.load("robot.png")

camera = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
camera_surface = pg.Surface(camera.size)

world_surface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT))
camera.center = (WORLD_WIDTH / 2, WORLD_HEIGHT / 2)

clock = pg.time.Clock()

quit = False
frame = 0
start_time = time()
while not quit:

    screen.fill((0, 0, 0))
    camera_surface.fill((0, 0, 0))

    delta_time = clock.get_time() / 1000.0
    if delta_time > 1:
        print("too much lag! skipping frame")
        continue
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit = True

    elapsed = (time() - start_time) / 1_000_000_000

    state_index = round(elapsed / sim_dt)
    print(state_index)

    world_surface.fill((101, 202, 87))
    if state_index < len(simulation_output.states):
        state: SimState = simulation_output.states[state_index]
        robot = pg.transform.rotate(sprite, state.robot_theta)

        blit_x = state.robot_x * WORLD_SCALE + WORLD_WIDTH / 2
        blit_y = state.robot_y * WORLD_SCALE + WORLD_HEIGHT / 2
        world_surface.blit(robot,
                           (blit_x - robot.get_width() / 2,
                            blit_y - robot.get_height() / 2))

    pressed = pg.key.get_pressed()
    if pressed[pg.K_a]:
        camera.x -= camera.width * 0.5 * delta_time
    if pressed[pg.K_d]:
        camera.x += camera.width * 0.5 * delta_time
    if pressed[pg.K_w]:
        camera.y -= camera.width * 0.5 * delta_time
    if pressed[pg.K_s]:
        camera.y += camera.width * 0.5 * delta_time
    if pressed[pg.K_e]:
        old_center = camera.center
        camera.width *= 2 ** delta_time
        camera.height = camera.width / ASPECT_RATIO
        camera.center = old_center
    if pressed[pg.K_q]:
        old_center = camera.center
        camera.width *= 0.5 ** delta_time
        camera.height = camera.width / ASPECT_RATIO
        camera.center = old_center

    if camera.width < 100:
        old_center = camera.center
        camera.width = 100
        camera.height = camera.width / ASPECT_RATIO
        camera.center = old_center

    if camera.width != camera_surface.get_width():
        camera_surface = pg.Surface(camera.size)

    camera_surface.blit(world_surface, (-camera.x, -camera.y))
    c = pg.transform.scale(camera_surface, screen.get_size())

    screen.blit(c, (0, 0))
    camera_text = font.render(str(camera), True, (0, 0, 0), (255, 255, 255))
    screen.blit(camera_text, (0, 0))

    pg.display.update()

    clock.tick(60)
    frame += 1

pg.quit()
