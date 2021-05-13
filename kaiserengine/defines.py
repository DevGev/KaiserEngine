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
    KEY_0 = pygame.K_0
    KEY_1 = pygame.K_1
    KEY_2 = pygame.K_2
    KEY_3 = pygame.K_3
    KEY_4 = pygame.K_4
    KEY_5 = pygame.K_5
    KEY_6 = pygame.K_6
    KEY_7 = pygame.K_7
    KEY_8 = pygame.K_8
    KEY_9 = pygame.K_9

    KEY_W = pygame.K_w
    KEY_A = pygame.K_a
    KEY_B = pygame.K_b
    KEY_C = pygame.K_c
    KEY_Q = pygame.K_q
    KEY_E = pygame.K_e
    KEY_R = pygame.K_r
    KEY_T = pygame.K_t
    KEY_Y = pygame.K_y
    KEY_u = pygame.K_u
    KEY_S = pygame.K_s
    KEY_D = pygame.K_d
    KEY_F = pygame.K_f
    KEY_ESC = pygame.K_ESCAPE
    KEY_SPACE = pygame.K_SPACE
    KEY_RETURN = pygame.K_RETURN
