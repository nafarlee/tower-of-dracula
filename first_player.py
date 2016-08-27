import pygame

import sys
import socket

import network
import end
from World import World
from Ghoul import Ghoul
from Bat import Bat

def main(fps, bg_color, window_width, window_height):
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
    screen = pygame.display.set_mode((window_width, window_height))

    pygame.mixer.music.load("assets/music/vamp.mp3")
    pygame.mixer.music.play(-1)

    client_socket = None
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
        leftx = camerax + window_width / 4
        rightx = camerax + window_width - (window_width/4)

        if world.simon.rect.x < leftx:
            camerax -= world.simon.move
        elif world.simon.rect.x > rightx:
            camerax += world.simon.move

        topy = cameray + window_height / 4
        bottomy = cameray + window_height - (window_height/4)

        if world.simon.rect.y < topy:
            cameray -= 1
        elif world.simon.rect.y > bottomy:
            cameray += 5

        camera = pygame.Rect(camerax, cameray, window_width, window_height)
        screen.fill(bg_color)
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
            end.youwin(screen, client_socket)
        elif world.winner == 2:
            end.youlose(screen, client_socket)

        pygame.display.flip()

        #FRAMERATE MANAGEMENT
        fpsclock.tick(fps)
        pygame.display.set_caption('Vania ' + str(int(fpsclock.get_fps())))
