import pygame
import numpy
import cv2

pygame.init()
screen = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()

def get_outline(image, color=(0,0,0), threshold=127):
    mask = pygame.mask.from_surface(image,threshold)
    outline_image = pygame.Surface(image.get_size()).convert_alpha()
    outline_image.fill((0,0,0,0))
    for point in mask.outline():
        outline_image.set_at(point,color)
    return outline_image

image = pygame.image.load('object.png')
rect = image.get_rect()
outline = get_outline(image, color=(0, 0, 255), threshold=100)
outline_rect = outline.get_rect()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False          

    screen.fill((0, 0, 0))
    screen.blit(image, rect)
    screen.blit(outline, outline_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
exit()