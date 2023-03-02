import os
import sys
import random

import pygame
from pygame import *
import pygame_menu
from pygame_menu import themes

pygame.init()
SIZE = W, H = 1600, 900
screen = display.set_mode(SIZE)


def terminate():
    pygame.quit()
    sys.exit()


def create_menu():
    mainmenu = pygame_menu.Menu('ИГРА', 800, 450,
                                theme=themes.THEME_DARK)
    mainmenu.add.button('Новая игра', start_game())
    mainmenu.add.button('Выход', terminate())


all_sprites = sprite.Group()
player_sprite = sprite.Group()
level_sprites = sprite.Group()
background_sprites = sprite.Group()
clock = time.Clock()
FPS = 15
GRAVITY = 5


def load_image(name, colorkey=None):
    filename = os.path.join('data', name)
    if not os.path.isfile(filename):
        print(f'Файл {filename} не найден')
        sys.exit()
    image = pygame.image.load(filename)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Camera:
    def __init__(self):
        self.back = False
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        if not obj.back:
            obj.rect.x += self.dx
            obj.rect.y += self.dy
        elif obj.lay == 2:
            obj.rect.x += self.dx // 12
            obj.rect.y += self.dy
        elif obj.lay == 3:
            obj.rect.x += self.dx // 10
            obj.rect.y += self.dy
        elif obj.lay == 4:
            obj.rect.x += self.dx // 8
            obj.rect.y += self.dy
        elif obj.lay == 5:
            obj.rect.x += self.dx // 6
            obj.rect.y += self.dy
        elif obj.lay == 6:
            obj.rect.x += self.dx // 4
            obj.rect.y += self.dy
        elif obj.lay == 7:
            obj.rect.x += self.dx // 2
            obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - W // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - H * 0.85)


class Ground(sprite.Sprite):
    def __init__(self):
        self.back = False
        super().__init__(level_sprites, all_sprites)
        self.image = load_image('ground.png')
        self.rect = self.image.get_rect()
        self.rect.bottom = H
        self.mask = mask.from_surface(self.image)


class Player(sprite.Sprite):
    def __init__(self, x, y):
        self.back = False
        super().__init__(player_sprite, all_sprites)
        self.frames = []
        self.cur_frame = 0
        self.image = None
        self.change_animation('idle', x, y)
        self.status = 'idle'
        self.vx = 0
        self.vy = 0
        self.direction = 'R'
        self.on_ground = True
        self.mask = mask.from_surface(self.image)

    def change_animation(self, animation, x, y):
        if animation == 'idle':
            self.frames = []
            self.cut_sheet(load_image('animation/Idle.png'),
                           4, 1, x, y)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame].convert_alpha()
        elif animation == 'walk':
            self.frames = []
            self.cut_sheet(load_image('animation/Walk.png'),
                           8, 1, x, y)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame].convert_alpha()
        elif animation == 'run':
            self.frames = []
            self.cut_sheet(load_image('animation/Run.png'),
                           7, 1, x, y)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame].convert_alpha()
        elif animation == 'jump':
            self.frames = []
            self.cut_sheet(load_image('animation/Jump.png'),
                           6, 1, x, y)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame].convert_alpha()
        elif animation == 'attack':
            self.frames = []
            self.cut_sheet(load_image('animation/Attack 1.png'),
                           5, 1, x, y)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame].convert_alpha()

    def cut_sheet(self, sheet, cols, rows, x, y):
        self.rect = Rect(x, y, sheet.get_width() // cols,
                         sheet.get_height() // rows)
        for j in range(rows):
            for i in range(cols):
                frame_location = self.rect.w * i, self.rect.h * j
                self.frames.append(sheet.subsurface(Rect(
                    frame_location, self.rect.size
                )))

    def idle(self):
        self.status = 'idle'
        self.change_animation('idle', self.rect.x, self.rect.y)
        self.vx = 0

    def walk(self):
        self.status = 'walk'
        self.vx = 10
        self.change_animation('walk', self.rect.x, self.rect.y)

    def run(self):
        self.status = 'run'
        self.vx = 20
        self.change_animation('run', self.rect.x, self.rect.y)

    def jump(self):
        self.status = 'jump'
        if self.on_ground:
            self.vy = -20
            self.change_animation('jump', self.rect.x, self.rect.y)

    def attack(self):
        self.status = 'attack'
        self.change_animation('attack', self.rect.x, self.rect.y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        if not pygame.sprite.collide_mask(self, ground):
            self.on_ground = False
        else:
            self.on_ground = True
        if self.direction == 'R':
            self.image = self.frames[self.cur_frame]
        elif self.direction == 'L':
            self.image = transform.flip(self.frames[self.cur_frame],
                                        True, False)
        if self.status == 'walk' and self.direction == 'R':
            self.vx = 10
        elif self.status == 'walk' and self.direction == 'L':
            self.vx = -10
        if self.status == 'run' and self.direction == 'R':
            self.vx = 20
        elif self.status == 'run' and self.direction == 'L':
            self.vx = -20
        if not self.on_ground:
            self.vy += GRAVITY
        else:
            self.vy = 0
        if self.status == 'jump' and self.on_ground:
            self.vy = -30
        self.rect = self.rect.move(self.vx, self.vy)


class Background(sprite.Sprite):
    def __init__(self, layer):
        super().__init__(all_sprites, background_sprites)
        self.back = True
        self.lay = layer
        if layer == 1:
            self.image = load_image('background/1.png')
        elif layer == 2:
            self.image = load_image('background/2.png')
        elif layer == 3:
            self.image = load_image('background/3.png')
        elif layer == 4:
            self.image = load_image('background/4.png')
        elif layer == 5:
            self.image = load_image('background/5.png')
        elif layer == 6:
            self.image = load_image('background/6.png')
        elif layer == 7:
            self.image = load_image('background/7.png')
        self.rect = self.image.get_rect()
        if layer == 6:
            self.rect = self.rect.move(0, 620)
        elif layer == 7:
            self.rect = self.rect.move(0, 250)


for i in range(1, 8):
    Background(i)
ground = Ground()
player = Player(W // 2, 710)
camera = Camera()

while True:
    for e in event.get():
        if e.type == QUIT:
            terminate()
        if e.type == KEYDOWN:
            if e.key == K_RIGHT:
                player.direction = 'R'
                player.walk()
            elif e.key == K_LEFT:
                player.direction = 'L'
                player.walk()
            if e.key == K_RIGHT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                player.direction = 'R'
                player.run()
            elif e.key == K_LEFT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                player.direction = 'L'
                player.run()
            if e.key == K_SPACE:
                player.jump()
            if e.key == K_f:
                player.attack()
        if e.type == KEYUP:
            player.idle()
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.update()
    all_sprites.draw(screen)
    display.flip()
    clock.tick(FPS)
