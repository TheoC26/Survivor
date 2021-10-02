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
        print(img_loc)
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
    textrect.topleft = (x,y)
    surface.blit(textobj, textrect)

class Button():
    def __init__(self, x, y, image, scale, animation=True):
        width = image.get_width()
        height = image.get_height()
        self.animation = animation
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
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

