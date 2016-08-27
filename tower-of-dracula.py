#!/usr/bin/env python
"""Castlevania Tower Defense Game"""

import sys
import socket
import cPickle as pickle

import pygame

import network
from World import World
from Simon import Simon
from Bat import Bat
from Ghoul import Ghoul

__author__ = 'Nicholas Farley'

BG_COLOR = pygame.Color('#271b8f')
FPS = 60

WINDOW_WIDTH = int(raw_input("Enter desired window width: "))
assert WINDOW_WIDTH >= 640, "Window == gonna be too short"

WINDOW_HEIGHT = int(raw_input("Enter desired window height: "))
assert WINDOW_HEIGHT >= 480, "Window == gonna be too thin"


def choose_player_type():
    """Choose which player to be"""
    player_type = raw_input("Would you like to play as Simon or Dracula? ").lower()

    if player_type[0] == 's':
        return "first"
    elif player_type[0] == 'd':
        return "second"
    else:
        print "invalid choice"
        return choose_player_type()

def first_player_main():
    """Play the game as Simon, with or without multiplayer"""
    network_type = raw_input("Play multiplayer? y/n ")

    is_multiplayer = bool(network_type == 'y')

    if is_multiplayer:
        server_ip = str(raw_input("Enter the ip address (eg 127.0.0.1): "))
        server_port = int(raw_input("Enter the port number of the server: "))
        if server_ip == "":
            server_ip = "localhost"


    #init
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.mixer.music.load("assets/music/vamp.mp3")
    pygame.mixer.music.play(-1)

    if is_multiplayer:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

    font = pygame.font.SysFont(None, 50)
    fpsclock = pygame.time.Clock()

    inputs = {
        "up": False,
        "down": False,
        "left": False,
        "right": False,
        "a": False,
        "b": False
    }
    camerax = 600
    cameray = 300
    playerx = 1388
    playery = 950
    debugging_masks = False

    enemy_type = "Ghoul"

    world = World(playerx, playery)

    #Game Loop
    while True:
        #Input Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not is_multiplayer:
                if event.type == pygame.MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    xpos = mousex + camerax
                    ypos = mousey + cameray
                    world.create_enemy(xpos, ypos, enemy_type)


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    debugging_masks = True
                if event.key == pygame.K_b:
                    debugging_masks = False

                if not is_multiplayer:
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        enemy_type = "Ghoul"
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        enemy_type = "Bat"

                if event.key == pygame.K_w:
                    inputs["up"] = True
                if event.key == pygame.K_s:
                    inputs["down"] = True
                if event.key == pygame.K_a:
                    inputs["left"] = True
                if event.key == pygame.K_d:
                    inputs["right"] = True
                if event.key == pygame.K_SPACE:
                    inputs["a"] = True
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    inputs["b"] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    inputs["up"] = False
                if event.key == pygame.K_s:
                    inputs["down"] = False
                if event.key == pygame.K_a:
                    inputs["left"] = False
                if event.key == pygame.K_d:
                    inputs["right"] = False
                if event.key == pygame.K_SPACE:
                    inputs["a"] = False
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    inputs["b"] = False

        #MAIN UPDATING PROCEDURE
        world.update(inputs)

        #BEGIN DRAWING PROCEDURES
        leftx = camerax + WINDOW_WIDTH / 4
        rightx = camerax + WINDOW_WIDTH - (WINDOW_WIDTH/4)

        if world.simon.rect.x < leftx:
            camerax -= world.simon.move
        elif world.simon.rect.x > rightx:
            camerax += world.simon.move

        topy = cameray + WINDOW_HEIGHT / 4
        bottomy = cameray + WINDOW_HEIGHT - (WINDOW_HEIGHT/4)

        if world.simon.rect.y < topy:
            cameray -= 1
        elif world.simon.rect.y > bottomy:
            cameray += 5

        camera = pygame.Rect(camerax, cameray, WINDOW_WIDTH, WINDOW_HEIGHT)
        screen.fill(BG_COLOR)
        screen.blit(world.background, (-camerax, -cameray))

        for sprite in world.all_sprites:
            if camera.colliderect(sprite.rect):
                screen.blit(sprite.image,
                            (sprite.rect.x-camera.x-sprite.hitboxoffset,
                             sprite.rect.y-camera.y))

        if debugging_masks:
            box = world.goal
            pygame.draw.rect(screen, (255, 0, 0), (box.x-camera.x,
                                                   box.y-camera.y,
                                                   box.width, box.height))

            if world.simon.is_attacking:
                box = world.simon.attack
                pygame.draw.rect(screen, (255, 0, 0), (box.x-camera.x,
                                                       box.y-camera.y, box.width, box.height))

            for box in world.obstacles:
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 255, 0), (box.x-camera.x,
                                                           box.y-camera.y, box.width, box.height))

            for steps in world.top_stairs:
                box = pygame.Rect((steps[0] - world.stair_width/2, steps[1]),
                                  (world.stair_width, world.stair_height))
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 0, 255), (box.x-camera.x,
                                                           box.y-camera.y, box.width, box.height))

            for steps in world.bot_stairs:
                box = pygame.Rect((steps[0] - world.stair_width/2, steps[1]),
                                  (world.stair_width, world.stair_height))

                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 0, 255), (box.x-camera.x,
                                                           box.y-camera.y, box.width, box.height))

            for enemy in world.enemies:
                box = enemy.rect
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 255, 255), (box.x-camera.x,
                                                             box.y-camera.y, box.width, box.height))

        #HUD
        label = "Health: " + str(world.simon.health) + "/" + str(world.simon.maxhealth)
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, 10))
        label = "Time: " + str(world.time)
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, 60))

        if not is_multiplayer:
            label = enemy_type + ": "
            if enemy_type == "Ghoul":
                label += str(Ghoul.cost)
            elif enemy_type == "Bat":
                label += str(Bat.cost)
            label = font.render(label, 1, (255, 255, 255))
            screen.blit(label, (10, 110))

            label = "MP: " + str(world.mp)
            label = font.render(label, 1, (255, 255, 255))
            screen.blit(label, (10, 160))
        #END DRAWING PROCEDURES


        #NETWORK INTERACTIONS
        if is_multiplayer:
            network.send_world_report(world, client_socket)
            enemy_spawn = network.receive_spawn_input(client_socket)
            if enemy_spawn != None:
                enemyx = enemy_spawn[0]
                enemyy = enemy_spawn[1]
                enemytype = enemy_spawn[2]
                world.create_enemy(enemyx, enemyy, enemytype)

        if world.winner == 1:
            youwin(screen, client_socket)
        elif world.winner == 2:
            youlose(screen, client_socket)

        pygame.display.flip()

        #FRAMERATE MANAGEMENT
        fpsclock.tick(FPS)
        pygame.display.set_caption('Vania ' + str(int(fpsclock.get_fps())))

def second_player_main():
    """Play the game as Dracula"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_port = int(raw_input("Enter the port number to listen on: "))
    s.bind(('', listen_port))
    s.listen(1)
    print "Waiting for connection now at", str(socket.gethostbyname(socket.gethostname()))
    connection = s.accept()[0]

    #init
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    #music commented out in second player game for presentation purposes
    #pygame.mixer.music.load("sounds/vamp.mp3")
    #pygame.mixer.music.play(-1)

    font = pygame.font.SysFont(None, 50)

    fpsclock = pygame.time.Clock()
    camerax = 600
    cameray = 300

    #data resources
    background = pygame.image.load("assets/levels/background.png").convert_alpha()
    simon = Simon(-1, -1)
    ghoul = Ghoul(-1, -1)
    bat = Bat(-1, -1)

    is_panning_up = False
    is_panning_down = False
    is_panning_left = False
    is_panning_right = False
    camera_pan_amount = 5

    enemy_type = "Ghoul"


    while True:
        #Input Handling
        enemy_spawn = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    is_panning_up = True
                if event.key == pygame.K_s:
                    is_panning_down = True
                if event.key == pygame.K_a:
                    is_panning_left = True
                if event.key == pygame.K_d:
                    is_panning_right = True

                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    enemy_type = "Ghoul"
                if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    enemy_type = "Bat"

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    is_panning_up = False
                if event.key == pygame.K_s:
                    is_panning_down = False
                if event.key == pygame.K_a:
                    is_panning_left = False
                if event.key == pygame.K_d:
                    is_panning_right = False

            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                xpos = mousex + camerax
                ypos = mousey + cameray
                enemy_spawn = (xpos, ypos, enemy_type)

        if is_panning_up:
            cameray -= camera_pan_amount
        if is_panning_down:
            cameray += camera_pan_amount
        if is_panning_left:
            camerax -= camera_pan_amount
        if is_panning_right:
            camerax += camera_pan_amount

        camera = pygame.Rect(camerax, cameray, WINDOW_WIDTH, WINDOW_HEIGHT)
        screen.fill(BG_COLOR)
        screen.blit(background, (-camerax, -cameray))

        world_report = network.receive_world_report(connection)
        network.send_spawn_input(enemy_spawn, connection)

        if world_report is None:
            print "Connection to Player 1 has Failed"
        else:
            simon_rect = world_report["Simon"]
            simon_health = world_report["Health"]
            monster_points = world_report["MP"]
            timeleft = world_report["Time"]
            enemies = world_report["Enemies"]
            winner = world_report["Winner"]
            if winner == 1:
                youlose(screen, connection)
            elif winner == 2:
                youwin(screen, connection)

        if camera.colliderect(simon_rect):
            simonx = simon_rect.x - camera.x - simon.hitboxoffset
            simony = simon_rect.y - camera.y
            screen.blit(simon.image, (simonx, simony))

        for enemy in enemies:
            enemy_rect = enemy[1]
            enemy_t = enemy[0]
            if camera.colliderect(enemy_rect):
                enemyx = enemy_rect.x - camera.x
                enemyy = enemy_rect.y - camera.y
                if enemy_t == "Ghoul":
                    screen.blit(ghoul.image, (enemyx, enemyy))
                elif enemy_t == "Bat":
                    screen.blit(bat.image, (enemyx, enemyy))

        label = "Simon Health: " + str(simon_health)
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, 10))

        label = "Time: " + str(timeleft)
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, 60))

        label = enemy_type + ": "
        if enemy_type == "Ghoul":
            label += str(Ghoul.cost)
        elif enemy_type == "Bat":
            label += str(Bat.cost)
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, WINDOW_HEIGHT-50))

        label = "MP: " + str(monster_points)
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, WINDOW_HEIGHT-100))

        label = "[1] Ghoul | Bat [2]"
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, WINDOW_HEIGHT-150))

        pygame.display.flip()
        fpsclock.tick(FPS)
        pygame.display.set_caption('Vania ' + str(int(fpsclock.get_fps())))

def youwin(screen, socket):
    blit_large_label(screen, "You Win!")
    pygame.display.flip()

    pygame.time.delay(4000)
    socket.close()
    pygame.quit()
    sys.exit()

def youlose(screen, socket):
    blit_large_label(screen, "You Lose!")
    pygame.display.flip()

    pygame.time.delay(4000)
    socket.close()
    pygame.quit()
    sys.exit()

def blit_large_label(screen, message):
    font_size = 100
    labelx = WINDOW_WIDTH/3 - font_size
    labely = WINDOW_HEIGHT/2
    font = pygame.font.SysFont(None, font_size)
    label = font.render(message, 1, (255, 255, 255))

    screen.blit(label, (labelx, labely))

if __name__ == "__main__":
    player_type = choose_player_type()
    if player_type == "first":
        first_player_main()
    elif player_type == "second":
        second_player_main()