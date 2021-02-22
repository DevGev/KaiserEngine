import os
from sys import exit
import threading
import random
from audioplayer import AudioPlayer

import kaiserengine.external as external
from kaiserengine.defines import *
from kaiserengine.loader import *
from kaiserengine.debug import *

class ColliderController:
    def __init__(self):
        self.sprites = []

    def collider(self, item):
        if isinstance(item, Sprite):
            self.sprites.append(item)

    def check_collision_point(self, x, y, rect):
        if (x > rect.rec_x) and (x < rect.rec_x + rect.rec_w) and (y > rect.rec_y) and (y < rect.rec_y + rect.rec_h):
            return True
        return False
    
    def rectangle_collision(self, rect1, rect2):
        for a, b in [(rect1, rect2), (rect2, rect1)]:
            if ((self.check_collision_point(a.rec_x, a.rec_y, b)) or
                (self.check_collision_point(a.rec_x, a.rec_y + a.rec_h, b)) or
                (self.check_collision_point(a.rec_x + a.rec_w, a.rec_y, b)) or
                (self.check_collision_point(a.rec_x + a.rec_w, a.rec_y + a.rec_h, b))):
                    return True
        return False

    def check_collision(self, sx, sy, sw, sh, source=None, target=None):
        if target == None:
            for index, sprite in enumerate(self.sprites):
                if sprite.sprite_n != source:
                    rec1 = Rectangle(sx, sy, sw, sh, 0)
                    rec2 = Rectangle(sprite.sprite_x, sprite.sprite_y, sprite.sprite_w, sprite.sprite_h, 0)
                    if self.rectangle_collision(rec1, rec2):
                        return sprite.sprite_n
        else:
            for index, _sprite in enumerate(self.sprites):
                if _sprite.sprite_n == target:
                    sprite = _sprite

            rec1 = Rectangle(sx, sy, sw, sh, 0)
            rec2 = Rectangle(sprite.sprite_x, sprite.sprite_y, sprite.sprite_w, sprite.sprite_h, 0)
            if self.rectangle_collision(rec1, rec2):
                return sprite.sprite_n

        return 0

    def check(self, sprite_name, target=None):
        for index, sprite in enumerate(self.sprites):
            if sprite.sprite_n == sprite_name:
                current_sprite = sprite
        return self.check_collision(current_sprite.sprite_x, current_sprite.sprite_y, current_sprite.sprite_w, \
                                    current_sprite.sprite_h, current_sprite.sprite_n, target)

    def remove(self, sprite_name):
        for sprite in self.sprites:
            if sprite.sprite_n == sprite_name:
                self.sprites.remove(sprite)

class AudioController:
    def __init__(self):
        self.audio_volume = 1
        self.current_song = None
        self.audioplayer = None
        self.loop = True

    def sfx(self, effect, volume):
        audioplayer = AudioPlayer(effect)
        audioplayer.volume = volume
        audioplayer.play(block=True) 
        audioplayer.close()

    def play_sfx(self, effect, volume):
        sf = threading.Thread(target=self.sfx, args=(effect,volume,))
        sf.daemon = True
        sf.start()

    def set(self, song):
        force_path(song)
        if self.audioplayer:
            self.close()

        self.audioplayer = AudioPlayer(song)
        self.audioplayer.volume = self.audio_volume
        self.current_song = song

    def play(self):
        self.audioplayer.play(loop=self.loop)

    def volume(self, v):
        self.audio_volume = v

    def pause(self):
        self.audioplayer.pause()

    def unpause(self):
        self.audioplayer.resume()
    
    def close(self):
        self.audioplayer.close()

class InputController:
    def __init__(self, e):
        self.events = e

    def pressed(self, keynum):
        keys = external.keys_pressed()
        if keys[keynum] or keys[keynum]:
            return 1
        return 0

class Cooldown:
    def __init__(self, time, name):
        self.last = external.get_ticks()
        self.cooldown_n = name
        self.cooldown = time

    def status(self):
        now = external.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            return 1
        return 0

class Rectangle:
    def __init__(self, x, y, width, height, c):
        self.rec_w = width
        self.rec_h = height
        self.rec_x = x
        self.rec_y = y
        self.rec_c = c

class Circle:
    def __init__(self, x, y, radius, c):
        self.cir_r = radius
        self.cir_x = x
        self.cir_y = y
        self.cir_c = c

class Projectile:
    def __init__(self, cm, start_x, start_y, end_x, end_y, width, height, time, color):
        self.projectile_start_x = int(start_x)
        self.projectile_start_y = int(start_y)

        self.projectile_w = width
        self.projectile_h = height
        self.projectile_c = color

        self.projectile_cx = start_x
        self.projectile_cy = start_y
        self.bitmap = None

        horizontal = None
        if end_y == 0:
            horizontal = True
        if end_x == 0:
            horizontal = False 

        if horizontal == None:
            print_error("projectile cannot be diagonal")
             
        if horizontal:
            self.projectile_end_x = int(start_x + end_x)
            self.projectile_ex = start_x + height 
            self.projectile_ey = start_y
        else:
            self.projectile_end_y = int(start_y + end_y)
            self.projectile_ey = start_y + height
            self.projectile_ex = start_x

        self.projectile_hz = horizontal
        self.exists = True
        self.destroyed = False
        self.last = external.get_ticks()
        self.cooldown = time
        self.collision_manager = cm

    def hit(self, target=None):
        if self.destroyed:
            return

        if not self.projectile_hz:
            return self.collision_manager.check_collision(self.projectile_cx-int(self.projectile_w/2), \
                   self.projectile_cy, self.projectile_w, self.projectile_h, target=target)
        # Maybe works?
        if self.projectile_hz:
            return self.collision_manager.check_collision(self.projectile_cx, self.projectile_cy-int(self.projectile_w/2), \
                   self.projectile_h, self.projectile_w, target=target)
        return 0

    def bitmap_set(self, bmp):
        if isinstance(bmp, Bitmap):
            bmp.bmp_h = self.projectile_h
            bmp.bmp_w = self.projectile_w
            self.bitmap = bmp

            return 0
        self.bitmap = Bitmap(bmp, self.projectile_w, self.projectile_h, 0, 0)

    def grab_surface(self):
        return self.bitmap.grab_surface()

    def iterate(self):
        now = external.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            return 1
        return 0
    
    def grab(self):
        kill = 0
        if self.iterate() == 1:
            if self.projectile_hz:
                if self.projectile_cx < self.projectile_end_x:
                    self.projectile_cx += self.projectile_h
                    self.projectile_ex += self.projectile_h
                    if self.projectile_cx > self.projectile_end_x:
                        self.destroyed = True 
                else:
                    self.projectile_cx -= self.projectile_h
                    self.projectile_ex -= self.projectile_h
                    if self.projectile_cx < self.projectile_end_x:
                        self.destroyed = True 

            if not self.projectile_hz:
                if self.projectile_cy < self.projectile_end_y:
                    self.projectile_cy += self.projectile_h
                    self.projectile_ey += self.projectile_h
                    if self.projectile_cy > self.projectile_end_y:
                        self.destroyed = True 
                else:
                    self.projectile_cy -= self.projectile_h
                    self.projectile_ey -= self.projectile_h
                    if self.projectile_cy < self.projectile_end_y:
                        self.destroyed = True 

        return (self.projectile_cx, self.projectile_cy)

    def destroy(self):
        self.destroyed = True

class Image:
    def __init__(self, path, name):
        self.img_p = path
        self.img_n = name
        self.loaded = external.image_load(path)

    def grab(self):
        return self.loaded

class Bitmap:
    def __init__(self, bmp, width, height,  fc, bc):
        self.bitmap = bmp
        self.bmp_w = width
        self.bmp_h = height
        self.bmp_fc = fc
        self.bmp_bc = bc
        
        self.last = external.get_ticks()
        self.iteration = 0
        self.cooldown = 300
        self.surfaces = []

        if isinstance(bmp, list):
            for img in bmp:
                surf = external.surface((width, height))
                surf.fill(self.bmp_bc)
                surf.blit(img.grab(), (0, 0))
                self.surfaces.append(surf)
            return

        if isinstance(bmp, Image):
            surf = external.surface((width, height))
            surf.fill(self.bmp_bc)
            surf.blit(bmp.grab(), (0, 0))
            self.surfaces.append(surf)
            return

        if isinstance(bmp, tuple):
            surf = external.surface((width, height))
            surf.fill(bmp)
            self.surfaces.append(surf)
            return

        if self.bitmap.split(".")[1] == "ivan":
            force_path(self.bitmap)
            self.generate_animation(self.bitmap)
        else:
            force_path(self.bitmap)
            self.generate_bmp(self.bitmap)

    def rotate(self, original_r, r):
        for index, surf in enumerate(self.surfaces):
            self.surfaces[index] = external.transform_rotate_center(surf, r-original_r)

    def generate_animation(self, bmp):
        frames = load_ivan(bmp)
        for animation in frames:
            self.generate_bmp(animation)

    def generate_bmp(self, bmp):
        width = self.bmp_w
        height = self.bmp_h
        image = external.image_load(bmp) 
        surf = external.surface((width, height))
        surf.fill(self.bmp_bc)
        surf.blit(image, (0, 0))
        self.surfaces.append(surf)

    def grab_surface(self):
        now = external.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            self.iteration += 1
            if self.iteration > len(self.surfaces)-1:
                self.iteration = 0

        surf = self.surfaces[self.iteration]
        return surf

class Particles:
    def __init__(self, x, y, r, decrease, amount, color):
        self.par_x = x
        self.par_y = y
        self.par_r = r 
        self.par_a = amount
        self.par_d = decrease
        self.par_c = color

        self.particles = []
        for x in range(0, amount):
            self.generate()

    def grab(self):
        circles_draw = []
        for index, particle in enumerate(self.particles):
            self.particles[index][0][0] += self.particles[index][1][0]
            self.particles[index][0][1] += self.particles[index][1][1]
            self.particles[index][2] -= self.par_d 
            if not self.particles[index][2] <= 0:
                circles_draw.append(self.particles[index])
        return circles_draw

    def generate(self):
        self.par_vx = random.randint(0, 20) / 10 - 1 
        self.par_vy = random.randint(0, 20) / 10 - 1 
        r = self.par_r + random.randint(-2, 2)
        self.particles.append([[self.par_x, self.par_y], [self.par_vx, self.par_vy], r])

class Sprite:
    def __init__(self, cm, bmp, x, y, width, height, name):
        self.sprite_n = name
        self.sprite_h = height
        self.sprite_w = width
        self.sprite_x = x
        self.sprite_y = y

        self.sprite_ox = x
        self.sprite_oy = y
        self.collider_manager = cm

        self.bitmap = Bitmap(bmp, width, height, 0, 0)
        self.rotation = 0
        self.own_surface = None
        self.destroyed = False
        self.hidden = False
        self.ghost = False

    def move_x(self, x, direction=True):
        if isinstance(x, float):
            print_error("argument x of Sprite.move_x cannot be float")
            return -1

        for i in range(1, x+1):
            i = i/i
            if direction == True:
                self.sprite_x += i
            else:
                self.sprite_x -= i
            if self.collider_manager.check(self.sprite_n) and not self.ghost:
                if direction == True:
                    self.sprite_x -= i
                else:
                    self.sprite_x += i
                return

    def move_y(self, y, direction=True):
        if isinstance(y, float):
            print_error("argument y of Sprite.move_y cannot be float")
            return -1

        for i in range(1, y+1):
            i = i/i
            if direction == False:
                self.sprite_y += i
            else:
                self.sprite_y -= i
            if self.collider_manager.check(self.sprite_n) and not self.ghost:
                if direction == False:
                    self.sprite_y -= i
                else:
                    self.sprite_y += i
                return

    def restore_position(self):
        self.sprite_x = self.sprite_ox
        self.sprite_y = self.sprite_oy

    def bitmap_rotate(self, rotation):
        if self.own_surface:
            self.own_surface = external.transform_rotate_center(self.own_surface, self.rotation - rotation)
        else:
            self.bitmap.rotate(self.rotation, rotation)
        self.rotation = rotation

    def bitmap_timing(self, time):
        self.bitmap.cooldown = time

    def bitmap_set(self, bmp):
        self.bitmap = Bitmap(bmp, self.sprite_w, self.sprite_h, 0, 0)
        self.own_surface = None

    def mid(self, t):
        if t == 0:
            return self.sprite_x + self.sprite_w/2
        return self.sprite_y - self.sprite_h/2

    def collided(self, target=None):
        collided = 0
        self.sprite_x -= 1
        self.sprite_w += 2
        self.sprite_y -= 1
        self.sprite_h += 2
        if self.collider_manager.check(self.sprite_n, target):
            collided = 1
        self.sprite_x += 1
        self.sprite_w -= 2
        self.sprite_y += 1
        self.sprite_h -= 2
        return collided
    
    def circle(self, circle):
        if not isinstance(circle, Circle):
            print_error("invalid circle")
            return 0
        self.own_surface = external.surface((self.sprite_w, self.sprite_h))
        self.own_surface.fill((255, 0, 255))
        external.draw_circle(self.own_surface, circle.cir_c, (circle.cir_x+self.sprite_w/2, circle.cir_y+self.sprite_h/2), circle.cir_r)

    def rectangle(self, rectangle):
        if not isinstance(rectangle, Rectangle):
            print_error("invalid rectangle")
            return 0
        self.own_surface = external.surface((self.sprite_w, self.sprite_h))
        self.own_surface.fill((255, 0, 255))
        external.draw.rect(self.own_surface, rectangle.rec_c, (self.sprite_x + rectangle.rec_x, \
                              self.sprite_y + rectangle.rec_y, self.sprite_w + rectangle.rec_w, self.sprite_h + rectangle.rec_h))

    def grab_surface(self):
        if self.own_surface != None:
            return self.own_surface
        return self.bitmap.grab_surface()

    def destroy(self):
        self.destroyed = True
        self.collider_manager.remove(self.sprite_n)

class Text:
    def __init__(self, t, x, y, f, c):
        self.text_t = t
        self.text_x = x 
        self.text_y = y

        self.text_surface = None
        self.text_c = c
        self.current_font  = f
        self.generate()

    def text(self, t):
        self.text_t = t
        self.generate()

    def generate(self):
        self.text_surface = self.current_font.render(self.text_t, False, self.text_c)

    def grab_surface(self):
        return self.text_surface

class Task:
    def __init__(self, t, n):
        self.task_t = t
        self.task_n = n
        self.is_active = True 

    def run(self):
        self.task_t()

class Engine:
    def __init__(self, width, height, title, icon):
        self.screen_icon = None
        self.background_image = None
        self.background = colors.BLACK
        if icon:
            self.screen_icon = external.image_load(icon, False)

        self.screen_title = title
        self.screen_width = width
        self.screen_height = height

        self.controller = InputController(external.event())
        self.clock = external.clock()
        self.collider_manager = ColliderController()
        self.audio_controller = AudioController()
        
        self.loaded_images = []
        self.cooldowns = []
        self.render_objects = []
        self.tasks = []

        self.current_font = None
        self.is_running = True
        self.debug = False
        self.enable_fullscreen = False
        self.fullscreen_key = keys.KEY_F
        self.fullscreen_counter = self.cooldown(1000, "Fullscreen Timer")

        self.display_flags = 0 
        self.delta_time = 0
        self.fps = 160 
        self.display = external.display(self.screen_title, self.screen_width, \
                                        self.screen_height, self.screen_icon)

    def set_display_mode(self, flags):
        self.display_flags = flags
        external.set_mode((self.screen_width, self.screen_height), flags)

    def fullscreen(self, key):
        self.enable_fullscreen = True
        self.fullscreen_key = key

    def find_cooldown(self, name):
        for cooldown in self.cooldowns:
            if cooldown.cooldown_n == name:
                return cooldown

    def find_sprite(self, name):
        for sprite in self.render_objects:
            if isinstance(sprite, Sprite):
                if sprite.sprite_n == name:
                    return sprite

    def find_image(self, name):
        for image in self.loaded_images:
            if isinstance(image, list):
                if image[0].img_n == name:
                    return image
            else:
                if image.img_n == name:
                    return image 
        print_error("could not preload image: " + name)

    def cooldown(self, t, n):
        self.cooldowns.append(Cooldown(t, n))
        return self.cooldowns[len(self.cooldowns)-1]

    def load_image(self, p, n):
        force_path(p)

        if p.split(".")[1] == "ivan":
            img_load = []
            for img in load_ivan(p):
                img_load.append(Image(img, n))
            self.loaded_images.append(img_load)
            print_info("preloaded ivan file: " + str(p) +  " as '" + n + "'")
            return self.loaded_images[len(self.loaded_images)-1]

        self.loaded_images.append(Image(p, n))
        print_info("preloaded image file: " + p + " as '" + n + "'")
        return self.loaded_images[len(self.loaded_images)-1]

    def font(self, f, s):
        if ".tff" in f:
            force_path(f)
            self.current_font = external.init_font(f, s, False)
        else:
            self.current_font = external.init_font(f, s, True)

    def text(self, t, x, y, c):
        if self.current_font == None:
            print_error("no font selected")
            return 0
        text = Text(t, x, y, self.current_font, c)
        self.render_objects.append(text)
        return self.render_objects[len(self.render_objects)-1]

    def particle_effect(self, x, y, r, decrease, amount, color):
        particle = Particles(x, y, r, decrease, amount, color)
        self.render_objects.append(particle)
        return particle

    def rectangle(self, x, y, width, height, c, static=False):
        rectangle = Rectangle(x, y, width, height, c)
        if static == True:
            self.render_objects.append(rectangle)
        return rectangle

    def circle(self, x, y, radius, c, static=False):
        circle = Circle(x, y, radius, c)
        if static == True:
            self.render_objects.append(circle)
        return circle

    def sprite(self, bmp, x, y, w, h, n):
        self.render_objects.append(Sprite(self.collider_manager, bmp, x, y, w, h, n))
        self.collider_manager.collider(self.render_objects[len(self.render_objects)-1])
        return self.render_objects[len(self.render_objects)-1]

    def projectile(self, sx, sy, ex, ey, w, h, time, color):
        self.render_objects.append(Projectile(self.collider_manager, sx, sy, ex, ey, w, h, time, color))
        return self.render_objects[len(self.render_objects)-1]

    def render(self):
        if self.background_image:
            self.display.blit(self.background_image, (0, 0))
        else:
            self.display.fill(self.background)

        for index, render_object in enumerate(self.render_objects):

            if isinstance(render_object, Particles):
                circles = render_object.grab()
                if len(circles) == 0:
                    del self.render_objects[index]
                for circle in circles:
                    external.draw_circle(self.display, render_object.par_c, (circle[0][0], circle[0][1]), circle[2])

            if isinstance(render_object, Circle):
                external.draw_circle(self.display, render_object.cir_c, (render_object.cir_x, render_object.cir_y), render_object.cir_r)

            if isinstance(render_object, Rectangle):
                external.draw.rect(self.display, render_object.rec_c, (render_object.rec_x, render_object.rec_y, render_object.rec_w, render_object.rec_h))

            if isinstance(render_object, Text):
                self.display.blit(render_object.grab_surface(), (render_object.text_x, render_object.text_y))

            if isinstance(render_object, Projectile):
                if render_object.exists == True and render_object.destroyed == False:
                    if render_object.bitmap:
                        self.display.blit(render_object.grab_surface(), render_object.grab())
                    else:
                        external.draw_line(self.display, render_object.projectile_c, render_object.grab(), (render_object.projectile_ex, render_object.projectile_ey), render_object.projectile_w)
                else:
                    del self.render_objects[index]

            if isinstance(render_object, Sprite):
                if render_object.destroyed == True:
                    self.render_objects.remove(render_object)

                if render_object.hidden != True:
                    self.display.blit(render_object.grab_surface(), (render_object.sprite_x, render_object.sprite_y))

        external.display_flip()

    def task(self, t, n):
        self.tasks.append(Task(t, n))
        return self.tasks[len(self.tasks)-1]

    def task_remove(self, name):
        for index, task in enumerate(self.tasks):
            if task.task_n == name:
                del self.tasks[index]

    def set_background(self, back):
        if isinstance(back, tuple):
            self.background = back
        else:
            force_path(back)
            self.background_image = external.image_load(back)

    def events(self):
        external.event_quit()

        if self.controller.pressed(self.fullscreen_key) and self.enable_fullscreen and self.display.get_flags() & display.FULLSCREEN and self.fullscreen_counter.status():
            external.set_mode((self.screen_width, self.screen_height), None)
        elif self.controller.pressed(self.fullscreen_key) and self.enable_fullscreen and not self.display.get_flags() & display.FULLSCREEN and self.fullscreen_counter.status():
            external.set_mode((self.screen_width, self.screen_height), self.display_flags | display.FULLSCREEN)

    def run(self):
        while self.is_running:
            if self.debug == True:
                objects_in_render(self.render_objects, Sprite, Projectile, Particles)
            self.delta_time = self.clock.tick(self.fps)

            for task in self.tasks:
                if task.is_active:
                    task.run()

            self.events()
            self.render()

def init(width, height, title, icon=None):
    return Engine(width, height, title, icon)
