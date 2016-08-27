import socket
import sys

import pygame

from Simon import Simon
from Bat import Bat
from Ghoul import Ghoul
import end
import network

def main(fps, bg_color, window_width, window_height):
    """Play the game as Dracula"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_port = int(raw_input("Enter the port number to listen on: "))
    s.bind(('', listen_port))
    s.listen(1)
    print "Waiting for connection now at", str(socket.gethostbyname(socket.gethostname()))
    connection = s.accept()[0]

    #init
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))

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

        camera = pygame.Rect(camerax, cameray, window_width, window_height)
        screen.fill(bg_color)
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
                end.youlose(screen, connection)
            elif winner == 2:
                end.youwin(screen, connection)

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
        screen.blit(label, (10, window_height-50))

        label = "MP: " + str(monster_points)
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, window_height-100))

        label = "[1] Ghoul | Bat [2]"
        label = font.render(label, 1, (255, 255, 255))
        screen.blit(label, (10, window_height-150))

        pygame.display.flip()
        fpsclock.tick(fps)
        pygame.display.set_caption('Vania ' + str(int(fpsclock.get_fps())))
