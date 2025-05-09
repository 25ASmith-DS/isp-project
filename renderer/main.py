import pygame as pg
from math import pi as PI, floor
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
    debug_text = file.read()
simulation_output = SimOutput(json.loads(debug_text))
sim_dt = simulation_output.delta_time
states = simulation_output.states


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960

WORLD_WIDTH = 8000
WORLD_HEIGHT = 6000
WORLD_SCALE = 20  # pixels per meter

ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

font = pg.font.Font(pg.font.get_default_font(), floor(SCREEN_HEIGHT / 40))
sprite = pg.image.load("robot.png")

camera = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
camera_surface = pg.Surface(camera.size)

world_surface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT))
camera.center = (WORLD_WIDTH / 2, WORLD_HEIGHT / 2)

clock = pg.time.Clock()
world_timer = 0.0
frame_by_frame = True
frame_skip = 1


quit = False

if __name__ != "__main__":
    quit = True

while not quit:
    screen.fill((0, 0, 0))
    camera_surface.fill((0, 0, 0))

    pressed = pg.key.get_pressed()

    delta_time = clock.get_time() / 1000.0
    if not frame_by_frame:
        world_timer += delta_time

    if delta_time > 1:
        print("too much lag! skipping frame")
        continue
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                frame_by_frame = not frame_by_frame
            if event.key == pg.K_r:
                world_timer = 0.0
            if event.key == pg.K_LEFTBRACKET:
                world_timer -= sim_dt * frame_skip
            if event.key == pg.K_RIGHTBRACKET:
                world_timer += sim_dt * frame_skip
            if event.key == pg.K_MINUS:
                frame_skip = max(frame_skip - 1 - 9*pressed[pg.K_LSHIFT], 1)
            if event.key == pg.K_EQUALS:
                frame_skip = min(frame_skip + 1 + 9*pressed[pg.K_LSHIFT], 100)

    state_index = floor(world_timer / sim_dt)

    if state_index < len(states):
        world_surface.fill((101, 202, 87))
        state: SimState = states[state_index]
        radians = state.robot_theta
        degrees = radians * 180 / PI
        robot = pg.transform.rotate(sprite, degrees)

        blit_x = state.robot_x * WORLD_SCALE + WORLD_WIDTH / 2
        blit_y = -state.robot_y * WORLD_SCALE + WORLD_HEIGHT / 2
        world_surface.blit(robot,
                           (blit_x - robot.get_width() / 2,
                            blit_y - robot.get_height() / 2))
    else:
        frame_by_frame = True
        world_timer -= sim_dt

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

    debug_text = []
    fs = f"frame skip {frame_skip}" if frame_by_frame else "realtime"
    debug_text.append(f"Frame {state_index}/{len(states)} ({fs})")

    dec = 4
    t = str(world_timer) + "0" * dec
    debug_text.append(f"Time: {t[:t.find('.')+dec]}")

    debug_text += str(state.debug).splitlines()

    padding = 5
    y = padding
    for line in debug_text:
        r = font.render(line, True, (0, 0, 0), (255, 255, 255))
        screen.blit(r, (padding, y))
        y += r.get_height() + padding

    pg.display.update()

    clock.tick(60)

pg.quit()
