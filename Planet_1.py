import pygame
from pygame.locals import *
import sys
import time
import math
import pyganim

pygame.init()


#--------Variable Declarations--------------#

MAX_X = 800
MAX_Y = 640
  
# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
mainClock = pygame.time.Clock()
BGCOLOR = (100, 50, 50)

Surface = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption('Planet Vortex')

#-------------------------------------------#



def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

class Planet(pygame.sprite.Sprite):
    def __init__(self, x, y, r, rotation):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.r = r
        self.rotangle = rotation
    def draw(self, Surface):
        pygame.draw.circle(Surface, BLACK, (self.x,self.y), self.r, 10)
    
#---Initialize objects---#
earth = Planet(400,320, 180,0)
    
while True:
    Surface.fill(BGCOLOR)
    for event in pygame.event.get():
        print event
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    earth.draw(Surface)
    pygame.draw.circle(Surface, BLACK, (100,200), 50, 10)
    
    pygame.display.update()
