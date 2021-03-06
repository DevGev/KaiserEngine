from colorama import *
from sys import exit
import os
init()

def force_path(p):
    if not os.path.exists(p):
        print_error("path " + str(p) + " does not exist")
        exit()

def clear_screen(): 
    if os.name == 'nt':
        os.system('cls') 
    else: 
        os.system('clear')

def print_info(msg):
    print(Fore.GREEN + "Info:", msg + Style.RESET_ALL)

def print_error(msg):
    print(Fore.RED + "Error:", msg + Style.RESET_ALL)
    exit()

def print_warning(msg):
    print(Fore.YELLOW + "Warning:", msg + Style.RESET_ALL)

def objects_in_render(render_objects, Sprite, Projectile, Particles):
    clear_screen()
    sprites_in_render = []
    projectiles_in_render = []
    particles_in_render = []

    for index, render_object in enumerate(render_objects):
        if isinstance(render_object, Sprite):
            sprites_in_render.append(render_object.sprite_n)
    for index, render_object in enumerate(render_objects):
        if isinstance(render_object, Projectile):
            projectiles_in_render.append(str(render_object.projectile_hz))
    for index, render_object in enumerate(render_objects):
        if isinstance(render_object, Particles):
            particles_in_render.append(str(render_object.par_a))

    print("  ╸ {Sprites}")
    for index, sprite in enumerate(sprites_in_render):
        print("  ╸\t" + str(index), sprite)
    print("\n  ╸ {Projectiles}")
    for index, projectile in enumerate(projectiles_in_render):
        print("  ╸\t" + str(index) + " Horizontal:", projectile)
    print("\n  ╸ {Particles}")
    for index, particles in enumerate(particles_in_render):
        print("  ╸\t" + str(index) + " Amount:", particles)
