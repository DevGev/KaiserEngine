import pygame
import os
import sys

class colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    TRANSPARENT = (255, 0, 255)

class keys:
    KEY_W = pygame.K_w 
    KEY_A = pygame.K_a
    KEY_S = pygame.K_s
    KEY_D = pygame.K_d 
    KEY_SPACE = pygame.K_SPACE

def force_path(p):
    if not os.path.exists(p):
        print("Path:", p, "does not exist")
        sys.exit()
