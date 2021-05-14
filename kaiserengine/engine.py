import os
from sys import exit
import threading
import random
import requests
from audioplayer import AudioPlayer
import kaiserengine.external as external
from kaiserengine.defines import *
from kaiserengine.loader import *
from kaiserengine.debug import *

SCREEN_SIZE_W = 0
SCREEN_SIZE_H = 0

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
        return external.rectangle_collision(rect1, rect2)

    def check_collision(self, sx, sy, sw, sh, source=None, target=None):
        if target == None:
            for index, sprite in enumerate(self.sprites):
                if sprite.sprite_n != source:
                    rec1 = Rectangle(sx, sy, sw, sh, 0)
                    rec2 = Rectangle(sprite.sprite_x, sprite.sprite_y,
                                     sprite.sprite_w, sprite.sprite_h, 0)
                    if self.rectangle_collision(rec1, rec2):
                        return sprite.sprite_n
        else:
            sprite = None
            for index, _sprite in enumerate(self.sprites):
                if _sprite.sprite_n == target:
                    sprite = _sprite
            if not sprite:
                return 0

            rec1 = Rectangle(sx, sy, sw, sh, 0)
            rec2 = Rectangle(sprite.sprite_x, sprite.sprite_y,
                             sprite.sprite_w, sprite.sprite_h, 0)
            if self.rectangle_collision(rec1, rec2):
                return sprite.sprite_n

        return 0

    def check(self, sprite_name, target=None, side=None):
        for index, sprite in enumerate(self.sprites):
            if sprite.sprite_n == sprite_name:
                current_sprite = sprite

        if side == sides.BOTTOM:
            return self.check_collision(current_sprite.sprite_x+1, current_sprite.sprite_y+1, current_sprite.sprite_w-2,
                                        current_sprite.sprite_h-1, current_sprite.sprite_n, target)
        if side == sides.TOP:
            return self.check_collision(current_sprite.sprite_x+1, current_sprite.sprite_y, current_sprite.sprite_w-2,
                                        current_sprite.sprite_h-1, current_sprite.sprite_n, target)

        if side == sides.LEFT:
            return self.check_collision(current_sprite.sprite_x, current_sprite.sprite_y+1, current_sprite.sprite_w-1,
                                        current_sprite.sprite_h-2, current_sprite.sprite_n, target)

        if side == sides.RIGHT:
            return self.check_collision(current_sprite.sprite_x+1, current_sprite.sprite_y+1, current_sprite.sprite_w,
                                        current_sprite.sprite_h-2, current_sprite.sprite_n, target)

        if not side:
            return self.check_collision(current_sprite.sprite_x, current_sprite.sprite_y, current_sprite.sprite_w,
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
        sf = threading.Thread(target=self.sfx, args=(effect, volume,))
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

    def pressed(self, key):
        keys = external.keys_pressed()
        if keys[key] or keys[key]:
            return 1
        return 0

    def mouse_pressed(self, mkey):
        if mkey > 2 or mkey < 0:
            return 0
        return external.mouse_press()[mkey]

    def mouse_x(self):
        return external.mouse_pos()[0]

    def mouse_y(self):
        return external.mouse_pos()[1]


class Cooldown:
    def __init__(self, time, name):
        self.last = external.get_ticks()
        self.cooldown_n = name
        self.cooldown = time

    def reset(self):
        self.last = external.get_ticks()

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
            return self.collision_manager.check_collision(
                        self.projectile_cx-int(self.projectile_w/2),
                        self.projectile_cy, self.projectile_w, self.projectile_h, target=target
                    )
        # Maybe works?
        if self.projectile_hz:
            return self.collision_manager.check_collision(
                        self.projectile_cx, self.projectile_cy-int(self.projectile_w/2),
                        self.projectile_h, self.projectile_w, target=target
                    )
        return 0

    def bitmap_set(self, bmp):
        if isinstance(bmp, Bitmap):
            bmp.bmp_h = self.projectile_h
            bmp.bmp_w = self.projectile_w
            self.bitmap = bmp

            return 0
        self.bitmap = Bitmap(bmp, self.projectile_w, self.projectile_h, 0, 0)

    def bitmap_timing(self, time):
        self.bitmap.cooldown = time

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


class Layer:
    def __init__(self, objects, name):
        self.render_objects = objects
        self.layer_n = name
        self.layer_h = False

    def hide(self):
        self.layer_h = True

    def grab(self):
        return self.render_objects


class Image:
    def __init__(self, path, name):
        self.img_p = path
        self.img_n = name
        self.loaded = external.image_load(path)

    def grab(self):
        return self.loaded


class Bitmap:
    def __init__(self, bmp, width, height,  fc, bc):
        bmp = image_parse(bmp)
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
            self.surfaces[index] = external.transform_rotate_center(
                surf, r-original_r)

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
    def __init__(self, x, y, r, decrease, amount, color, velocity):
        self.par_x = x
        self.par_y = y
        self.par_r = r
        self.par_a = amount
        self.par_d = decrease
        self.par_c = color

        self.par_vx_max = 20
        self.par_vy_max = 20
        self.par_vx_min = 0
        self.par_vy_min = 0

        self.particles = []
        if velocity:
            self.velocity(velocity[0], velocity[1])

        for x in range(0, amount):
            self.generate()

    def velocity(self, velocity_x, velocity_y):
        self.par_vx_min = velocity_x[0]
        self.par_vx_max = velocity_x[1]
        self.par_vy_min = velocity_y[0]
        self.par_vy_max = velocity_y[1]

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
        self.par_vx = random.randint(self.par_vx_min, self.par_vx_max) / 10 - 1
        self.par_vy = random.randint(self.par_vy_min, self.par_vy_max) / 10 - 1
        r = self.par_r + random.randint(-2, 2)
        self.particles.append(
            [[self.par_x, self.par_y], [self.par_vx, self.par_vy], r])


class Sprite:
    def __init__(self, cm, bmp, x, y, width, height, name, current_layout=False):
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

        self.layout = current_layout
        self.screen_boundary = False
        self.own_surface = None
        self.destroyed = False
        self.hidden = False
        self.ghost = False

    def move_x(self, x):
        direction = True
        if x < 0:
            direction = False
            x = abs(x)

        if self.screen_boundary:
            if not self.layout:
                if self.sprite_x + x >= SCREEN_SIZE_W - self.sprite_w and direction:
                    return
                if self.sprite_x - x <= 0 and not direction:
                    return

            if self.layout:
                if self.sprite_x + x >= self.layout.layout_max_x - self.sprite_w and direction:
                    return
                if self.sprite_x - x <= self.layout.layout_min_x and not direction:
                    return

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

    def move_y(self, y):
        direction = True
        if y < 0:
            direction = False
            y = abs(y)

        if self.screen_boundary:
            if not self.layout:
                if self.sprite_y + y >= SCREEN_SIZE_H - self.sprite_h and not direction:
                    return
                if self.sprite_y - y <= 0 and direction:
                    return

            if self.layout:
                if self.sprite_y + y >= self.layout.layout_min_y - self.sprite_h and not direction:
                    return
                if self.sprite_y - y <= self.layout.layout_max_y and direction:
                    return

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
            self.own_surface = external.transform_rotate_center(
                self.own_surface, self.rotation - rotation)
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

    def collided(self, target=None, side=None):
        collided = 0
        self.sprite_x -= 1
        self.sprite_w += 2
        self.sprite_y -= 1
        self.sprite_h += 2
        collided = self.collider_manager.check(self.sprite_n, target, side)
        self.sprite_x += 1
        self.sprite_w -= 2
        self.sprite_y += 1
        self.sprite_h -= 2
        return collided

    def circle(self, circle):
        if not isinstance(circle, Circle):
            print_error("invalid circle")
        self.own_surface = external.surface((self.sprite_w, self.sprite_h))
        self.own_surface.fill((255, 0, 255))
        external.draw_circle
        (
            self.own_surface, circle.cir_c,
            (circle.cir_x + self.sprite_w/2, circle.cir_y+self.sprite_h/2),
            circle.cir_r
        )

    def rectangle(self, rectangle):
        if not isinstance(rectangle, Rectangle):
            print_error("invalid rectangle")
        self.own_surface = external.surface((self.sprite_w, self.sprite_h))
        self.own_surface.fill((255, 0, 255))
        external.draw_rect(
                self.own_surface, rectangle.rec_c, (self.sprite_x + rectangle.rec_x,
                self.sprite_y + rectangle.rec_y, self.sprite_w + rectangle.rec_w,
                self.sprite_h + rectangle.rec_h)
        )

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
        self.current_font = f
        self.generate()

    def text(self, t):
        self.text_t = t
        self.generate()

    def generate(self):
        self.text_surface = self.current_font.render(
            self.text_t, False, self.text_c)

    def grab_surface(self):
        return self.text_surface


class Task:
    def __init__(self, t, n):
        self.task_t = t
        self.task_n = n
        self.is_active = True

    def run(self):
        self.task_t()

class Camera:
    def __init__(self, min_x, max_x, min_y, max_y, width, height):
        self.camera_min_x = min_x
        self.camera_max_x = max_x
        self.camera_min_y = min_y
        self.camera_max_y = max_y
        self.camera_move_x = 0
        self.camera_move_y = 0
        self.camera_hx = 0
        self.camera_hy = 0
        self.screen_width = width
        self.screen_height = height
        self.camera_sprite = None
        self.camera_follow = False

    def follow(self, sprite):
        self.camera_sprite = sprite
        self.camera_follow = True

    def center(self, sprite):
        sprite.sprite_x = self.screen_width/2 - sprite.sprite_w/2
        sprite.sprite_y = self.screen_height/2
        sprite.sprite_ox = sprite.sprite_x
        sprite.sprite_oy = sprite.sprite_y

    def update(self):
        self.camera_follow = 0
        if not self.camera_sprite:
            return 0, 0

        if self.camera_sprite.sprite_x >= self.camera_min_x and self.camera_sprite.sprite_x <= self.camera_max_x:
            if not self.camera_hx:
                self.camera_hx = self.camera_sprite.sprite_x
            self.camera_move_x = self.camera_sprite.sprite_x - self.camera_hx
            self.camera_follow = 1

        if self.camera_sprite.sprite_y <= self.camera_min_y and self.camera_sprite.sprite_y >= self.camera_max_y:
            if not self.camera_hy:
                self.camera_hy = self.camera_sprite.sprite_y
            self.camera_move_y = self.camera_sprite.sprite_y - self.camera_hy
            self.camera_follow = 1

        if self.camera_follow == 0:
            return self.camera_move_x, self.camera_move_y

        return self.camera_move_x, self.camera_move_y

class Layout:
    def __init__(self, min_x, max_x, min_y, max_y, width, height):
        self.layout_min_x = min_x
        self.layout_max_x = max_x
        self.layout_min_y = min_y
        self.layout_max_y = max_y
        self.camera = Camera(min_x + width/2, max_x - width/2, min_y - height/2, max_y + height/2, width, height)

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
        self.layers = []
        self.render_objects = []
        self.tasks = []

        self.game_layout = None
        self.debug = False
        self.is_running = True
        self.current_font = None
        self.enable_fullscreen = False
        self.fullscreen_key = keys.KEY_F
        self.fullscreen_counter = self.cooldown(1000, "Full Screen Timer")

        self.display_flags = 0
        self.delta_time = 0
        self.fps = 160
        self.display = external.display(
            self.screen_title, self.screen_width, self.screen_height, self.screen_icon
        )

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

    def find_layer(self, name):
        for layer in self.layers:
            if layer.layer_n == name:
                return layer

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

    def layer_add(self, item, name):
        for l in self.layers:
            if l.layer_n == name:
                l.render_objects.append(item)
                if item in self.render_objects:
                    self.render_objects.remove(item)

    def layer(self, l, n):
        self.layers.append(Layer(l, n))

        for item in l:
            if item in self.render_objects:
                self.render_objects.remove(item)

        return self.layers[len(self.layers)-1]

    def cooldown(self, t, n):
        self.cooldowns.append(Cooldown(t, n))
        return self.cooldowns[len(self.cooldowns)-1]

    def load_image(self, p, n):
        p = image_parse(p)
        force_path(p)

        if p.split(".")[1] == "ivan":
            img_load = []
            for img in load_ivan(p):
                img_load.append(Image(img, n))
            self.loaded_images.append(img_load)
            print_info("preloaded ivan file: " + str(p) + " as '" + n + "'")
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

    def particle_effect(self, x, y, r, decrease, amount, color, velocity=None):
        particle = Particles(x, y, r, decrease, amount, color, velocity)
        self.render_objects.append(particle)
        return particle

    def rectangle(self, x, y, w, h, c, static=False):
        rectangle = Rectangle(x, y, w, h, c)
        if static == True:
            self.render_objects.append(rectangle)
        return rectangle

    def circle(self, x, y, radius, c, static=False):
        circle = Circle(x, y, radius, c)
        if static == True:
            self.render_objects.append(circle)
        return circle

    def sprite(self, bmp, x, y, w, h, n):
        self.render_objects.append(
            Sprite(self.collider_manager, bmp, x, y, w, h, n, self.game_layout)
        )
        self.collider_manager.collider(
            self.render_objects[len(self.render_objects)-1]
        )
        return self.render_objects[len(self.render_objects)-1]

    def projectile(self, sx, sy, ex, ey, w, h, time, color):
        self.render_objects.append(Projectile(
            self.collider_manager, sx, sy, ex, ey, w, h, time, color))
        return self.render_objects[len(self.render_objects)-1]

    def render_layer(self, layer, cam_x, cam_y):
        for index, render_object in enumerate(layer):
            if isinstance(render_object, Particles):
                circles = render_object.grab()
                if len(circles) == 0:
                    del layer[index]
                for circle in circles:
                    if circle[0][0] <= SCREEN_SIZE_W and circle[0][1] <= SCREEN_SIZE_H and circle[0][0] > 0 and circle[0][1] > 0:
                        external.draw_circle(
                            self.display, render_object.par_c, (circle[0][0], circle[0][1]), circle[2])

            if isinstance(render_object, Circle):
                external.draw_circle(self.display, render_object.cir_c, (
                    render_object.cir_x, render_object.cir_y), render_object.cir_r)

            if isinstance(render_object, Rectangle):
                external.draw_rect(self.display, render_object.rec_c, (render_object.rec_x,
                                                                       render_object.rec_y, render_object.rec_w, render_object.rec_h))

            if isinstance(render_object, Text):
                self.display.blit(render_object.grab_surface(
                ), (render_object.text_x, render_object.text_y))

            if isinstance(render_object, Projectile):
                if render_object.exists == True and render_object.destroyed == False:
                    if render_object.bitmap:
                        self.display.blit(
                            render_object.grab_surface(), render_object.grab())
                    else:
                        external.draw_line(self.display, render_object.projectile_c, render_object.grab(
                        ), (render_object.projectile_ex, render_object.projectile_ey), render_object.projectile_w)
                else:
                    del layer[index]

            if isinstance(render_object, Sprite):
                if render_object.destroyed:
                    layer.remove(render_object)

                if not render_object.hidden:
                    self.display.blit(render_object.grab_surface(
                    ), (render_object.sprite_x - cam_x, render_object.sprite_y - cam_y))

    def render(self):
        cam_x, cam_y = 0, 0
        bak_x, bak_y = 0, 0
        if self.game_layout:
            cam_x, cam_y = self.game_layout.camera.update()
            bak_x = self.game_layout.layout_min_x
            bak_y = self.game_layout.layout_max_y

        if self.background_image:
            self.display.blit(self.background_image, (bak_x - cam_x, bak_y - cam_y))
        else:
            self.display.fill(self.background)

        self.render_layer(self.render_objects, cam_x, cam_y)
        for layer in self.layers:
            if not layer.layer_h:
                self.render_layer(layer.render_objects, cam_x, cam_y)
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
            back = image_parse(back)
            force_path(back)
            self.background_image = external.image_load(back)

    def layout(self, min_x, max_x, min_y, max_y):
        self.game_layout = Layout(min_x, max_x, min_y, max_y, SCREEN_SIZE_W, SCREEN_SIZE_H)
        return self.game_layout

    def events(self):
        external.event_quit()

        if self.controller.pressed(self.fullscreen_key) and self.enable_fullscreen and self.display.get_flags() & display.FULLSCREEN and self.fullscreen_counter.status():
            external.set_mode((self.screen_width, self.screen_height), None)

        elif self.controller.pressed(self.fullscreen_key) and self.enable_fullscreen and not self.display.get_flags() & display.FULLSCREEN and self.fullscreen_counter.status():
            external.set_mode((self.screen_width, self.screen_height),
                              self.display_flags | display.FULLSCREEN)

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


def kaiser_init(width, height, title, icon=None):
    global SCREEN_SIZE_H, SCREEN_SIZE_W
    SCREEN_SIZE_H = height
    SCREEN_SIZE_W = width
    return Engine(width, height, title, icon)
