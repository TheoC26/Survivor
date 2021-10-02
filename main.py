import pygame, sys, random
from pygame.locals import *
import csv
import framework
pygame.mixer.pre_init()
pygame.init()

WHITE = (255,255,255)
BLACK = (200, 200, 200)
BLUE = (100, 200, 220)

font = pygame.font.SysFont('Avenir', 50)

clock = pygame.time.Clock()
pygame.display.set_caption("platformer")
#--------------STARTING STUFF--------------------

#--------------GLOBAL VARIABLES--------------------
TILE_SIZE = 16
TILE_TYPES = 21
#--------x-----GLOBAL VARIABLES---------x-----------

#--------------WINDOW SIZE FUNCTION-----------------
display, screen, WIDTH, HEIGHT, RATIO, WINDOW_SIZE = framework.screen_size(1200, 800, 1)
#------X-------WINDOW SIZE FUNCTION-------X---------

#images
img_list = framework.load_tiles('tiles/ground blocks/ground_', TILE_TYPES, TILE_SIZE)

#sounds
jump_sound = pygame.mixer.Sound('sounds/jump.wav')
grass_sounds = [pygame.mixer.Sound('sounds/grass_0.wav'), pygame.mixer.Sound('sounds/grass_1.wav')]

#music
pygame.mixer.music.load('sounds/music.wav')
pygame.mixer.music.play(-1)


animation_frames = {}
animation_database = {}
animation_database['running'] = framework.load_animation('animation/running', [5, 5, 5, 5, 5], animation_frames)
animation_database['idle'] = framework.load_animation('animation/idle', [7, 7, 7, 7, 7], animation_frames)
animation_database['jump'] = framework.load_animation('animation/jump', [5, 5, 5, 5, 5], animation_frames)


def generate_chunk():
    number = random.randint(0,3)
    chunk = framework.load_map(str(number))
    return chunk


background_objects = framework.create_backround(4000, 2000, 30)


# background_objects = [[0.25,[120,50,70,400]],[0.25,[280,70,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles, player_y_momentum):
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


game_map = framework.load_map('0')
player_action = 'idle'
player_frame = 0
player_flip = False
player_rect = pygame.Rect(1600, 10, 8, 15)
moving_right = False
moving_left = False
player_y_momentum = 0
air_timer = 0
true_scroll = [0, 0]
offset = [0, 0]

mute = False

game_screen = False
pause_screen = False
start_screen = True

run = True
while run:
    while start_screen:
        display.fill(BLUE)
        framework.draw_text("Survivor", font, BLACK, display, WIDTH//2-60, HEIGHT//3-60)
        for event in pygame.event.get():
            if event.type == QUIT:
                game_screen = False
                pause_screen = False
                start_screen = False
                run = False
            if event.type == MOUSEBUTTONDOWN:
                game_screen = True
                pause_screen = False
                start_screen = False
        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        clock.tick(60)

    while game_screen:
        # print(offset[0])
        true_scroll[0] += (player_rect.x - true_scroll[0] - WIDTH//RATIO//2 - 4)/10
        true_scroll[1] += (player_rect.y - true_scroll[1] - HEIGHT // RATIO // 2 - 7)/10
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        display.fill((160, 244, 255))


        # generate infenint world
        # right
        if player_rect.x > (len(game_map[0]) - 10)*16:
            number_chunks = len(game_map) // TILE_SIZE
            right_chunks = []
            full_chunk = []
            for x in range(number_chunks):
                right_chunks.append(generate_chunk())
            for chunk in right_chunks:
                for row in chunk:
                    full_chunk.append(row)
            y = 0
            for row in game_map:
                for x in full_chunk[y]:
                    row.append(x)
                y+=1

        # left
        # if player_rect.x < 10 * 16:
        #     offset[0] -= 16*16
        #     print('true')
        #     number_chunks = len(game_map) // TILE_SIZE
        #     print(number_chunks)
        #     left_chunks = []
        #     full_chunk = []
        #     for x in range(number_chunks):
        #         left_chunks.append(generate_chunk())
        #     for chunk in left_chunks:
        #         for row in chunk:
        #             full_chunk.append(row)
        #     y = 0
        #     for row in game_map:
        #         game_map[y] = full_chunk[y]+game_map[y]
        #         y += 1

        # down
        if player_rect.y > (len(game_map)-10)*TILE_SIZE:
            number_chunks = len(game_map[0])//TILE_SIZE
            down_chunks = []
            for x in range(number_chunks):
                down_chunks.append(generate_chunk())
            for i in range(16):
                line = []
                for c in range(number_chunks):
                    line = line+down_chunks[c][i]
                game_map.append(line)



        for background_object in background_objects:
            obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0], background_object[1][1] - scroll[1] * background_object[0], background_object[1][2], background_object[1][3])
            if .21 < background_object[0] < 0.31:
                pygame.draw.rect(display, (14, 222, 200), obj_rect)
            if .11 < background_object[0] < 0.22:
                pygame.draw.rect(display, (8, 100, 65), obj_rect)
            if background_object[0] < 0.15:
                pygame.draw.rect(display, (8, 30, 65), obj_rect)



        tile_rects = []
        for y, row in enumerate(game_map):
            for x, tile in enumerate(row):
                if tile >= 0:
                    display.blit(img_list[tile], (x * TILE_SIZE - scroll[0] - offset[0], y * TILE_SIZE - scroll[1] - offset[1]))
                if tile != -1 and tile != 0 and tile != 1 and tile != 2 and tile != 3:
                    tile_rects.append(pygame.Rect(x*TILE_SIZE - offset[0], y*TILE_SIZE, TILE_SIZE, TILE_SIZE))


        player_movement = [0,0]
        if moving_right:
            player_movement[0] += 2
        if moving_left:
            player_movement[0] -= 2
        player_movement[1] += player_y_momentum
        player_y_momentum += .2
        if player_y_momentum > 5:
            player_y_momentum = 5

        if player_movement[0] > 0:
            player_action, player_frame = framework.change_animation(player_action, player_frame, 'running')
            player_flip = False
        if player_movement[0] == 0:
            player_action, player_frame = framework.change_animation(player_action, player_frame, 'idle')
        if player_movement[0] < 0:
            player_action, player_frame = framework.change_animation(player_action, player_frame, 'running')
            player_flip = True
        if air_timer > 6:
            player_action, player_frame = framework.change_animation(player_action, player_frame, 'jump')


        player_frame += 1
        if player_frame > len(animation_database[player_action])-1:
            player_frame = 0
        player_image_id = animation_database[player_action][player_frame]
        player_image = animation_frames[player_image_id]
        player_rect, collisions, player_y_momentum = move(player_rect, player_movement, tile_rects, player_y_momentum)
        display.blit(pygame.transform.flip(player_image, player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))

        if collisions['bottom']:
            air_timer = 0
            player_y_momentum = 0
        else:
            air_timer += 1

        if mute:
            pygame.mixer.music.fadeout(1000)  # use pygame.mixer.music.play() to start again


        for event in pygame.event.get():
            if event.type == QUIT:
                game_screen = False
                pause_screen = False
                start_screen = False
                run = False

            if event.type == KEYDOWN:
                if event.key == K_m:
                    # pygame.mixer.music.fadeout(1000) use pygame.mixer.music.play() to start again
                    mute = not mute
                    pygame.mixer.music.play()
                if event.key == K_RIGHT:
                    moving_right = True
                if event.key == K_LEFT:
                    moving_left = True
                if event.key == K_UP:
                    if air_timer < 6:
                        if not mute:
                            jump_sound.play()
                        player_y_momentum = -5
                if event.key == K_1:
                    display, screen, WIDTH, HEIGHT, RATIO, WINDOW_SIZE = framework.screen_size(600, 400, 2)
                if event.key == K_2:
                    display, screen, WIDTH, HEIGHT, RATIO, WINDOW_SIZE = framework.screen_size(900, 600, 3)
                if event.key == K_3:
                    display, screen, WIDTH, HEIGHT, RATIO, WINDOW_SIZE = framework.screen_size(1200, 800, 4)
                if event.key == K_4:
                    display, screen, WIDTH, HEIGHT, RATIO, WINDOW_SIZE = framework.screen_size(1500, 1000, 5)

            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                if event.key == K_LEFT:
                    moving_left = False

        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        clock.tick(60)

pygame.quit()
sys.exit()