# Pygame should not be used in the future
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
pygame.init()


# Resource loading and misc

def image_load(image):
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

def event_quit():
    for event in pygame.event.get():              
        if event.type == pygame.QUIT:        
            pygame.quit()                    
            exit()


# Draw functions  

def draw_line(surface, color, start_pos, end_pos, width):
    pygame.draw.line(surface, color, start_pos, end_pos, width) 

def draw_circle(surface, color, center, radius):
    pygame.draw.circle(surface, color, center, radius) 

def draw_rect(surface, color, rect):
    pygame.draw.rect(surface, color, rect)

def surface(size):
    return pygame.Surface(size)

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

def display_update():
    pygame.display.update()
