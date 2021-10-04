import pygame, sys, random
from pygame.locals import *
import csv
pygame.mixer.pre_init()
pygame.init()

WHITE = (0,0,0)
BLACK = (200, 200, 200)
BLUE = (100, 200, 220)

font = pygame.font.SysFont('Arial', 20)

def screen_size(width, height, ratio):
    WINDOW_SIZE = (width, height)
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
    display = pygame.Surface((width // ratio, height // ratio))
    return display, screen, width, height, ratio, WINDOW_SIZE

def load_tiles(path, tile_types, tile_size):
    images = []
    for x in range(tile_types):
        if x >= 10:
            img = pygame.image.load(str(path)+str(x)+'.png').convert_alpha()
        else:
            img = pygame.image.load(path+'0'+str(x)+'.png').convert_alpha()
        img = pygame.transform.scale(img, (tile_size, tile_size))
        images.append(img)
    return images

def load_map(chunk_number):
    map_data = []
    for row in range(150):
        r = [-1] * 150
        map_data.append(r)
    with open(f'map{chunk_number}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                map_data[x][y] = int(tile)
    return map_data

def load_animation(path,frame_durations, animation_frames):
    animation_name = path.split('/')[-2]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_animation(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame

def create_backround(number,location_range, size):
    background_objects = []
    for i in range(0,number):
        temp_list = []
        temp_list.append(float("." + str(i // 8)))
        temp_small = []
        temp_small.append(random.randint(-location_range, location_range))
        temp_small.append(random.randint(-location_range, location_range))
        temp_small.append(random.randint(1, size))
        temp_small.append(random.randint(1, size))
        temp_list.append(temp_small)
        background_objects.append(temp_list)

    return background_objects

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.center = (x,y)
    surface.blit(textobj, textrect)

def load_animations_player(color, speed):
    animation_frames = {}
    animation_database = {}
    animation_database['running'] = load_animation('player_animation/running/'+color, [speed, speed, speed, speed, speed], animation_frames)
    animation_database['idle'] = load_animation('player_animation/idle/'+color, [7, 7, 7, 7, 7], animation_frames)
    animation_database['jump'] = load_animation('player_animation/jump/'+color, [5, 5, 5, 5, 5], animation_frames)
    return animation_frames, animation_database

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def collision_test_enemy(player_rect, enemy_list):
    hit_list = []
    for enemy in enemy_list:
        if player_rect.collidrect(enemy):
            hit_list.append(enemy)
    return hit_list

def move_player(rect, movement, tiles, player_y_momentum):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False, }
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        if movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
            player_y_momentum = 0

    return rect, collision_types, player_y_momentum

def scale(val, src, dst):
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]


class Button():
    def __init__(self, x, y, image, scale, animation=True):
        width = image.get_width()
        height = image.get_height()
        self.animation = animation
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        if self.animation:
            if self.rect.collidepoint(pos):
                surface.blit(self.image, (self.rect.x, self.rect.y - 5))
            else:
                surface.blit(self.image, (self.rect.x, self.rect.y))
        else:
            surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

class Enemy():
    def __init__(self, x, y, radius):
        self.radius = radius
        self.enemy_rect = pygame.Rect(x, y, radius, radius)

    def draw(self, surface, scroll, rect, speed):
        # distance = abs((self.enemy_rect.centery + self.enemy_rect.centerx) - (rect.centery + rect.centerx))
        distance = abs(self.enemy_rect.centerx - rect.centerx)
        color = abs(distance)
        if color > 255:
            color = 255
        pygame.draw.circle(surface, (200, color, 85), (self.enemy_rect.centerx - scroll[0], self.enemy_rect.centery - scroll[1]), self.radius)
        if self.enemy_rect.x > rect.x:
            self.enemy_rect.x -= speed
        if self.enemy_rect.x < rect.x:
            self.enemy_rect.x += speed
        if self.enemy_rect.y > rect.y:
            self.enemy_rect.y -= speed/1.2
        if self.enemy_rect.y < rect.y:
            self.enemy_rect.y += speed/1.2

        # self.enemy_rect = rect