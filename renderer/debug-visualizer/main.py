import pygame as pg
import json
from math import pi as PI, floor, ceil
from debug import Debug, Circle, Line


class Duration:
    def __init__(self, obj: dict):
        self.secs = obj['secs']
        self.nanos = obj['nanos']

    def seconds(self):
        return self.secs + self.nanos / (10 ** 9)


class SimState:
    def __init__(self, obj: dict):
        self.robot_x = obj['robot_x']
        self.robot_y = obj['robot_y']
        self.robot_theta = obj['robot_theta']
        self.blade_on = obj['blade_on']
        self.debug = Debug(obj['debug'])


class SimOutput:
    def __init__(self, obj: dict):
        self.states: list[SimState] = [SimState(s) for s in obj['states']]
        self.delta_time: Duration = Duration(obj['delta_time']).seconds()
        self.wheel_distance: float = obj["wheel_distance"]
        self.wheel_radius: float = obj["wheel_radius"]
        self.max_motor_speed: float = obj["max_motor_speed"]
        self.blade_radius: float = obj["max_motor_speed"]


path = "../../simulation/out.sim"
with open(path, 'r') as file:
    json_str = file.read()
sim_output = SimOutput(json.loads(json_str))
sim_dt = sim_output.delta_time
states = sim_output.states
blade_radius = sim_output.blade_radius


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT

WORLD_SCALE = SCREEN_HEIGHT / 10  # pixels per meter

WORLD_WIDTH = SCREEN_WIDTH * 5
WORLD_HEIGHT = WORLD_WIDTH


pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

font = pg.font.Font(pg.font.get_default_font(), floor(SCREEN_HEIGHT / 40))
robot_sprite = pg.image.load("robot.png")
robot_sprite_size = (sim_output.wheel_distance * WORLD_SCALE,
                     sim_output.wheel_distance * WORLD_SCALE
                     * robot_sprite.get_height() / robot_sprite.get_width())
robot_sprite = pg.transform.smoothscale(robot_sprite, robot_sprite_size)

grass_size = 2
grass_texture_path = "grass.png"
grass_texture = pg.image.load(grass_texture_path)
grass_texture = pg.transform.smoothscale(
        grass_texture, (WORLD_SCALE * grass_size, WORLD_SCALE * grass_size))

grass_surface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT))
for y in range(ceil(WORLD_HEIGHT / grass_texture.get_height())):
    for x in range(ceil(WORLD_WIDTH / grass_texture.get_width())):
        grass_surface.blit(grass_texture,
                           (x * grass_texture.get_width(),
                            y * grass_texture.get_height()))


camera = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
camera_surface = pg.Surface(camera.size)

world_surface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT))
camera.center = (WORLD_WIDTH / 2, WORLD_HEIGHT / 2)

clock = pg.time.Clock()
world_timer = 0.0
frame_by_frame = True
frame_skip = 1


def worldcoords(x, y=None):
    if isinstance(x, tuple) and y is None:
        return worldcoords(x[0], x[1])
    return (x * WORLD_SCALE + WORLD_WIDTH / 2,
            -y * WORLD_SCALE + WORLD_HEIGHT / 2)


quit = False

if __name__ != "__main__":
    quit = True

while not quit:
    screen.fill((0, 0, 0))
    camera_surface.fill((0, 0, 0))
    world_surface.blit(grass_surface, (0, 0))

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

    debug_messages = []

    if state_index < len(states):

        for i in range(state_index):
            state = states[i]
            x, y = state.robot_x, state.robot_y
            if state.blade_on:
                pg.draw.circle(world_surface,
                               (48, 49, 31),
                               worldcoords(x, y),
                               blade_radius)

        state: SimState = states[state_index]
        radians = state.robot_theta
        degrees = radians * 180 / PI
        robot = pg.transform.rotate(robot_sprite, degrees)

        blit_x, blit_y = worldcoords(state.robot_x, state.robot_y)
        world_surface.blit(robot,
                           (blit_x - robot.get_width() / 2,
                            blit_y - robot.get_height() / 2))
        debug = state.debug
        for r in debug.renderables:
            if isinstance(r, Circle):
                circle: Circle = r
                pg.draw.circle(world_surface,
                               circle.color,
                               worldcoords(circle.center),
                               circle.radius * WORLD_SCALE)
            if isinstance(r, Line):
                line: Line = r
                pg.draw.line(world_surface, line.color,
                             worldcoords(line.p1),
                             worldcoords(line.p2),
                             line.width)
        debug_messages += debug.messages
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

    fs = f"frame skip {frame_skip}" if frame_by_frame else "realtime"
    debug_messages = \
        [f"Frame {state_index}/{len(states)} ({fs})"] + debug_messages

    dec = 4
    t = str(world_timer) + "0" * dec
    debug_messages = [f"Time: {t[:t.find('.')+dec]}"] + debug_messages

    padding = 5
    y = padding
    for line in debug_messages:
        r = font.render(line, True, (0, 0, 0), (255, 255, 255))
        screen.blit(r, (padding, y))
        y += r.get_height() + padding

    pg.display.update()

    clock.tick(60)

pg.quit()
