import pygame
import json


class Duration:
    def __init__(self, obj: dict):
        self.secs = obj['secs']
        self.nanos = obj['nanos']


class SimState:
    def __init__(self, obj):
        self.robot_x = obj['robot_x']
        self.robot_y = obj['robot_y']
        self.robot_theta = obj['robot_theta']
        self.debug = obj['debug']


class SimOutput:
    def __init__(self, obj: dict):
        self.steps = [SimState(state) for state in obj['steps']]
        self.delta_time = Duration(obj['delta_time'])


path = "tests/basic_goto.sim"
with open(path, 'r') as file:
    s = file.read()
simulation_output = SimOutput(json.loads(s))

if __name__ == "__main__":
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    WORLD_WIDTH = 800
    WORLD_HEIGHT = 600

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    camera = pygame.Rect(0.0, 0.0, SCREEN_WIDTH, SCREEN_HEIGHT)
    camera_surface = pygame.Surface(camera.size)

    aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    world_surface = pygame.image.load("noise.png")

    clock = pygame.time.Clock()

    quit = False
    frame = 0
    while not quit:
        delta_time = clock.get_time() / 1000.0
        if delta_time > 1:
            print("too much lag! skipping frame")
            continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True

        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_a]:
            camera.x -= camera.width * 0.5 * delta_time
        if pressed[pygame.K_d]:
            camera.x += camera.width * 0.5 * delta_time
        if pressed[pygame.K_w]:
            camera.y -= camera.width * 0.5 * delta_time
        if pressed[pygame.K_s]:
            camera.y += camera.width * 0.5 * delta_time
        if pressed[pygame.K_e]:
            old_center = camera.center
            camera.width *= 2 ** delta_time
            camera.height = camera.width / aspect_ratio
            camera.center = old_center
        if pressed[pygame.K_q]:
            old_center = camera.center
            camera.width *= 0.5 ** delta_time
            camera.height = camera.width / aspect_ratio
            camera.center = old_center

        if camera.width < 100:
            old_center = camera.center
            camera.width = 100
            camera.height = camera.width / aspect_ratio
            camera.center = old_center

        if camera.width != camera_surface.get_width():
            camera_surface = pygame.Surface(camera.size)

        camera_surface.blit(world_surface, (-camera.x, -camera.y))
        c = pygame.transform.scale(camera_surface, screen.get_size())
        screen.blit(c, (0, 0))

        pygame.display.update()

        clock.tick(60)
