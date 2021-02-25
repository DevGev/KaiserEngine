# Pygame should not be used in the future
import pygame
from kaiserengine.defines import *
pygame.init()


# Resource loading and misc

def rectangle_collision(rect1, rect2):
    r1 = pygame.Rect(rect1.rec_x, rect1.rec_y, rect1.rec_w, rect1.rec_h)
    r2 = pygame.Rect(rect2.rec_x, rect2.rec_y, rect2.rec_w, rect2.rec_h)
    return r1.colliderect(r2)


def transform_rotate_center(surface, angle):
    orig_rect = surface.get_rect()
    rot_surface = pygame.transform.rotate(surface, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_surface.get_rect().center
    rot_surface = rot_surface.subsurface(rot_rect).copy()
    return rot_surface


def transform_rotate(surface, angle):
    return pygame.transform.rotate(surface, angle)


def image_load(image, convert=True):
    if convert:
        return pygame.image.load(image).convert_alpha()
    return pygame.image.load(image)


def get_ticks():
    return pygame.time.get_ticks()


# Event and input functions

def clock():
    return pygame.time.Clock()


def event():
    return pygame.event


def keys_pressed():
    return pygame.key.get_pressed()


def mouse_press():
    return pygame.mouse.get_pressed()


def mouse_pos():
    x, y = pygame.mouse.get_pos()
    return (x, y)


def event_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# Draw functions


def draw_line(surface, color, start_pos, end_pos, width):
    pygame.draw.line(surface, color, start_pos, end_pos, width)


def draw_circle(surface, color, center, radius):
    center = (int(center[0]), int(center[1]))
    pygame.draw.circle(surface, color, center, int(radius))


def draw_rect(surface, color, rect):
    pygame.draw.rect(surface, color, rect)


def surface(size, colorkey=True):
    surf = pygame.Surface(size)
    if colorkey:
        surf.set_colorkey(colors.TRANSPARENT)
    return surf


def init_font(font, size, system_font=True):
    pygame.font.init()
    if system_font:
        return pygame.font.SysFont(font, size)
    return pygame.font.Font(font, size)


# Display functions

def display(title, width, height, icon=None):
    pygame.display.set_caption(title)
    if icon:
        pygame.display.set_icon(icon)
    return pygame.display.set_mode((width, height), 0, 32)


def set_mode(size, flags):
    if flags:
        pygame.display.set_mode(size, flags)
    else:
        pygame.display.set_mode(size)


def display_flip():
    pygame.display.flip()


def display_update():
    pygame.display.update()
