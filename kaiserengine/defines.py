import pygame
import os
import sys

class sides:
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3

class display:
    FULLSCREEN = pygame.FULLSCREEN
    DOUBLEBUF = pygame.DOUBLEBUF
    HWSURFACE = pygame.HWSURFACE
    OPENGL = pygame.OPENGL
    RESIZABLE = pygame.RESIZABLE
    NOFRAME = pygame.NOFRAME

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
    KEY_F  = pygame.K_f
    KEY_ESC = pygame.K_ESCAPE
    KEY_SPACE = pygame.K_SPACE
