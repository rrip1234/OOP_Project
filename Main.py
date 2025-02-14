import pygame
import sys
import traceback
import SceneManager as SceneManager

WHITE = (255, 255, 255)
GRAY = (127, 127, 127)

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1440, 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cass")

FPS = 30
clock = pygame.time.Clock()

SceneManager.scene = SceneManager.MainScene()
SceneManager.screen = screen

time = 0

running = True
while running:
    screen.fill(GRAY)

    try:
        command = SceneManager.scene.update()
    except Exception as e:
        print(traceback.format_exc())
    else:
        if isinstance(command, bool):
            running = command

    pygame.display.flip()

    time += 1
    clock.tick(FPS)

pygame.quit()
sys.exit()