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
pygame.display.set_caption("SURVIVOR")
#--------------STARTING STUFF--------------------

#--------------GLOBAL VARIABLES--------------------
TILE_SIZE = 16
TILE_TYPES = 22
#--------x-----GLOBAL VARIABLES---------x-----------

#--------------WINDOW SIZE FUNCTION-----------------
display, screen, WIDTH, HEIGHT, RATIO, WINDOW_SIZE = framework.screen_size(1200, 800, 4)
#------X-------WINDOW SIZE FUNCTION-------X---------

#images
img_list = framework.load_tiles('tiles/ground blocks/ground_', TILE_TYPES, TILE_SIZE)
load_img = pygame.image.load("uibuttons/ui_0.png")
save_img = pygame.image.load("uibuttons/ui_1.png")
pause_img = pygame.image.load("uibuttons/pause.png")
# backgrounds
background_1_img = pygame.image.load("backgrounds/background_1.png")
background_1_img = pygame.transform.scale(background_1_img, (int(background_1_img.get_width()*1.2), int(background_1_img.get_height()*1.2)))
background_2_img = pygame.image.load("backgrounds/background_2.png")
background_3_img = pygame.image.load("backgrounds/background_3.png")
background_4_img = pygame.image.load("backgrounds/background_4.png")

#sounds
jump_sound = pygame.mixer.Sound('sounds/jump.wav')
grass_sounds = [pygame.mixer.Sound('sounds/grass_0.wav'), pygame.mixer.Sound('sounds/grass_1.wav')]

# music
pygame.mixer.music.load('sounds/music.wav')
pygame.mixer.music.play(-1)

# make buttons
save_button = framework.Button(WINDOW_SIZE[0] // 2, HEIGHT // 2, save_img, 6)
load_button = framework.Button(WINDOW_SIZE[0] // 2, HEIGHT // 2 + 200, load_img, 6)
pause_button = framework.Button(WINDOW_SIZE[0] - 40, 40, pause_img, 3, False)


background_objects = framework.create_backround(2000, 1000, 30)

game_map = framework.load_map('0')
true_scroll = [0, 0]
offset = [0, 0]
map_number = 0

player_action = 'idle'
player_frame = 0
player_flip = False
player_rect = pygame.Rect(916, 10, 8, 15)
moving_right = False
moving_left = False
player_y_momentum = 0
air_timer = 0
player_jump_height = -4
player_speed = 2
player_health = 100

enemy_group = []
enemy_timer = 0
enemy_difficulty = 15
enemy_difficulty_counter = 0

enemy = framework.Enemy(random.randint(0, 1000), random.randint(0, 1000), random.randint(5, 20))
enemy_group.append(enemy)

mute = False

game_screen = False
pause_screen = False
start_screen = True

run = True
while run:
    while start_screen:
        display.blit(background_1_img, (0,0))

        for event in pygame.event.get():
            if event.type == QUIT:
                game_screen = False
                pause_screen = False
                start_screen = False
                run = False
        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        framework.draw_text("Survivor", font, BLACK, screen, WIDTH // 2, HEIGHT // 3)
        if save_button.draw(screen):
            animation_frames, animation_database = framework.load_animations_player('black', 4)
            display, screen, WIDTH, HEIGHT, RATIO, WINDOW_SIZE = framework.screen_size(1200, 800, 4)
            map_number = 0
            game_screen = True
            pause_screen = False
            start_screen = False
        if load_button.draw(screen):
            animation_frames, animation_database = framework.load_animations_player('pink', 4)
            display, screen, WIDTH, HEIGHT, RATIO, WINDOW_SIZE = framework.screen_size(1200, 800, 4)
            map_number = 1
            game_screen = True
            pause_screen = False
            start_screen = False
        pygame.display.update()
        clock.tick(60)

    while pause_screen:
        display.blit(background_1_img, (0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                game_screen = False
                pause_screen = False
                start_screen = False
                run = False

        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        if load_button.draw(screen):
            game_screen = True
            pause_screen = False
            start_screen = False
        pygame.display.update()
        clock.tick(60)

    while game_screen:
        enemy_timer += 1
        if enemy_timer > enemy_difficulty*60:
            enemy_difficulty_counter += 1
            if enemy_difficulty_counter > 15:
                enemy_difficulty -= 1
                if enemy_difficulty <= 1:
                    enemy_difficulty = 1
                enemy_difficulty_counter = 0
            enemy_timer = 0
            enemy = framework.Enemy(random.randint(0, 1000), random.randint(0, 1000), random.randint(5, 20))
            enemy_group.append(enemy)

        if map_number == 0:
            game_map = framework.load_map('0')
        elif map_number == 1:
            game_map = framework.load_map('1')

        true_scroll[0] += (player_rect.x - true_scroll[0] - WIDTH//RATIO//2 - 4)/10
        true_scroll[1] += (player_rect.y - true_scroll[1] - HEIGHT // RATIO // 2 - 7)/7
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        display.blit(background_1_img, (0,0))


        for background_object in background_objects:
            obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0], background_object[1][1] - scroll[1] * background_object[0], background_object[1][2], background_object[1][3])
            if .21 < background_object[0] < 0.31:
                pygame.draw.rect(display, (200, 120, 80), obj_rect)
            if .11 < background_object[0] < 0.22:
                pygame.draw.rect(display, (130, 100, 110), obj_rect)
            if background_object[0] < 0.15:
                pygame.draw.rect(display, (0, 40, 65), obj_rect)



        tile_rects = []
        for y, row in enumerate(game_map):
            for x, tile in enumerate(row):
                if tile >= 0:
                    display.blit(img_list[tile], (x * TILE_SIZE - scroll[0] - offset[0], y * TILE_SIZE - scroll[1] - offset[1]))
                if tile != -1 and tile != 0 and tile != 1 and tile != 2 and tile != 3:
                    tile_rects.append(pygame.Rect(x*TILE_SIZE - offset[0], y*TILE_SIZE, TILE_SIZE, TILE_SIZE))



        player_movement = [0,0]
        if moving_right:
            player_movement[0] += player_speed
        if moving_left:
            player_movement[0] -= player_speed
        player_movement[1] += player_y_momentum
        player_y_momentum += .2
        # if player_y_momentum > 5:
        #     player_y_momentum = 5
        if player_movement[0] > 0 and air_timer < 6:
            player_action, player_frame = framework.change_animation(player_action, player_frame, 'running')
            player_flip = False
        if player_movement[0] == 0:
            player_action, player_frame = framework.change_animation(player_action, player_frame, 'idle')
        if player_movement[0] < 0 and air_timer < 6:
            player_action, player_frame = framework.change_animation(player_action, player_frame, 'running')
            player_flip = True
        if player_y_momentum > 1.5 or player_y_momentum < 0:
            if player_movement[0] > 0:
                player_flip = False
            elif player_movement[0] < 0:
                player_flip = True
            player_action, player_frame = framework.change_animation(player_action, player_frame, 'jump')


        player_frame += 1
        if player_frame > len(animation_database[player_action])-1:
            player_frame = 0
        player_image_id = animation_database[player_action][player_frame]
        player_image = animation_frames[player_image_id]
        player_rect, collisions, player_y_momentum = framework.move_player(player_rect, player_movement, tile_rects, player_y_momentum)
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
                        player_y_momentum = player_jump_height
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

        for enimy in enemy_group:
            enimy.draw(display, scroll, player_rect, random.randrange(1, 3))



        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        if pause_button.draw(screen):
            game_screen = False
            pause_screen = True
            start_screen = False
        pygame.display.update()
        clock.tick(60)

pygame.quit()
sys.exit()