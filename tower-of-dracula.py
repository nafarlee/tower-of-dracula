#!/usr/bin/env python
"""Castlevania Tower Defense Game"""

import sys
import os
import socket
import cPickle as pickle

import pygame

__author__ = 'Nicholas Farley'

BG_COLOR = pygame.Color('#271b8f')
FPS = 60

WINDOW_WIDTH = int(raw_input("Enter desired window width: "))
assert WINDOW_WIDTH >= 640, "Window == gonna be too short"

WINDOW_HEIGHT = int(raw_input("Enter desired window height: "))
assert WINDOW_HEIGHT >= 480, "Window == gonna be too thin"


def choose_player_type():
    """Choose which player to be"""
    plyr_type = raw_input("Would you like to play as Simon or Dracula? ").lower()

    if plyr_type[0] == 's':
        first_player_main()

    elif plyr_type[0] == 'd':
        second_player_main()

    else:
        print "invalid choice"
        choose_player_type()

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
            send_world_report(world, client_socket)
            enemy_spawn = receive_spawn_input(client_socket)
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

        world_report = receive_world_report(connection)
        send_spawn_input(enemy_spawn, connection)

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

def send_world_report(world, socket):
    """send the pertinent world information to the second player"""
    world_report = {
        "Simon": world.simon.rect,
        "Health": world.simon.health,
        "MP": world.mp,
        "Time": world.time,
        "Enemies": [],
        "Winner": world.winner
    }

    for enemy in world.enemies:
        enemy_summary = (enemy.__name__, enemy.rect)
        world_report["Enemies"].append(enemy_summary)

    socket.sendall(pickle.dumps(world_report))

def receive_world_report(connection):
    """receive the pertinent world informtion from the first player"""
    data = connection.recv(1024)
    if not data:
        return None
    else:
        return pickle.loads(str(data))

def send_spawn_input(enemy_spawn_summary, socket):
    """send spawn inputs to the first player"""
    socket.sendall(pickle.dumps(enemy_spawn_summary))

def receive_spawn_input(connection):
    """recieve possible spawn inputs from the second player"""
    data = connection.recv(1024)
    if not data:
        return None
    else:
        return pickle.loads(str(data))

def youwin(screen, socket):
    font_size = 100
    font = pygame.font.SysFont(None, font_size)

    label = "YOU WIN!"
    label = font.render(label, 1, (255, 255, 255))
    labelx = WINDOW_WIDTH/3 - font_size
    labely = WINDOW_HEIGHT/2

    screen.blit(label, (labelx, labely))
    pygame.display.flip()

    pygame.time.delay(4000)
    socket.close()
    pygame.quit()
    sys.exit()

def youlose(screen, socket):
    font_size = 100
    font = pygame.font.SysFont(None, font_size)

    label = "YOU LOSE!"
    label = font.render(label, 1, (255, 255, 255))
    labelx = WINDOW_WIDTH/3 - font_size
    labely = WINDOW_HEIGHT/2

    screen.blit(label, (labelx, labely))
    pygame.display.flip()

    pygame.time.delay(4000)
    socket.close()
    pygame.quit()
    sys.exit()


class World(object):
    """Class that represents the state of the game world"""
    def __init__(self, playerx, playery):
        self.simon = Simon(playerx, playery)
        self.obstacles = self.generate_mask_boxes("assets/levels/backgroundmask.png")
        self.background = pygame.image.load("assets/levels/background.png").convert_alpha()
        self.death = self.generate_mask_boxes("assets/levels/backgrounddeath.png")
        self.death = self.death[0]
        self.goal = pygame.Rect(6960, 190, 75, 75)
        self.enemies = []
        self.all_sprites = []
        self.all_sprites.append(self.simon)
        self.gravity = 3
        self.frame = 0
        self.time_limit = 240
        self.time = self.time_limit
        self.winner = 0

        self.mp_max = 60
        self.mp = self.mp_max
        self.mp_regen = 5

        self.stair_width = 100
        self.stair_height = 40
        self.bot_stairs = [
            (320, 808),
            (94, 582),
            (752, 584),
            (1275, 582),
            (2660, 520),
            (2799, 390),
        ]
        self.top_stairs = [
            (94, 582),
            (235, 440),
            (814, 520),
            (1137, 454),
            (2799, 390),
            (2567, 164),
        ]

    def update(self, inputs):
        """call all world processing routines"""
        if self.frame < FPS:
            self.frame += 1
        else:
            self.frame = 0
            self.time -= 1
            if self.mp < self.mp_max:
                self.mp += self.mp_regen

        self.simon.update(inputs, self)

        if self.simon.health == 0:
            self.p2win()
        if self.simon.rect.colliderect(self.death):
            self.p2win()
        if self.time == 0:
            self.p2win()
        if self.simon.rect.colliderect(self.goal):
            self.p1win()

        for i, enemy in enumerate(self.enemies):
            enemy.update(self)
            if self.simon.is_attacking:
                box = self.simon.attack
                if box.colliderect(enemy.rect):
                    self.destroy_actor(i)
            box = self.simon.rect
            if box.colliderect(enemy):
                if box.x < enemy.rect.x:
                    self.simon.receive_hit("Right")
                else:
                    self.simon.receive_hit("Left")

    def generate_mask_boxes(self, imagemask):
        """Returns a list of rectangle objects based on image mask"""
        background_mask = (pygame.image.load(imagemask).convert_alpha())
        level_mask = pygame.mask.from_surface(background_mask)
        level_boxes = level_mask.get_bounding_rects()
        return level_boxes

    def create_enemy(self, xpos, ypos, type="Bat"):
        """create an enemy in the game world"""
        unspawnable_box = self.simon.rect.inflate(300, 300)
        if not unspawnable_box.collidepoint(xpos, ypos):
            if type == "Ghoul" and self.mp >= Ghoul.cost:
                self.mp -= Ghoul.cost
                self.enemies.append(Ghoul(xpos, ypos))
                self.all_sprites.append(self.enemies[-1])
            elif type == "Bat" and self.mp >= Bat.cost:
                self.mp -= Bat.cost
                self.enemies.append(Bat(xpos, ypos))
                self.all_sprites.append(self.enemies[-1])

    def destroy_actor(self, index):
        """removes an enemy in the game world"""
        del self.enemies[index]
        del self.all_sprites[index+1]

    def p1win(self):
        self.winner = 1

    def p2win(self):
        self.winner = 2

class Actor(pygame.sprite.Sprite):
    """Base class for all entities in the game world"""

    def __init__(self, xpos, ypos):
        pygame.sprite.Sprite.__init__(self)
        self.movy = 0
        self.movx = 0
        self.move = 1
        self.hitboxoffset = 0
        self.image = None
        self.rect = None
        self.direction = "Left"
        self.maxhealth = 1
        self.health = self.maxhealth
        self.frame = FPS
        return

class Bat(Actor):
    """Class the represents bats in the game world."""

    cost = 35

    def __init__(self, xpos, ypos):
        Actor.__init__(self, xpos, ypos)
        self.image1 = pygame.image.load("assets/bat/bat1.png")
        self.image2 = pygame.image.load("assets/bat/bat2.png")
        self.image3 = pygame.image.load("assets/bat/bat3.png")
        self.image = self.image1

        self.hitboxoffset = 0
        self.rect = pygame.Rect(xpos+self.hitboxoffset-30/2, ypos-30/2, 30, 50)
        self.swoop = 120
        self.swoop_frame = self.swoop
        self.swoop_velocity = 5
        self.swoop_decay = .1
        self.velocity = 0
        self.xvector = 0
        self.yvector = 0
        self.__name__ = "Bat"

    def update(self, world):
        """enemy AI processing"""
        self.movx = 0
        self.movy = 0
        self.image = self.image1

        if self.velocity >= self.swoop_decay:
            self.velocity -= self.swoop_decay

        if self.swoop_frame > 0:
            self.swoop_frame -= 1
        else:
            self.swoop_frame = self.swoop
            self.velocity = self.swoop_velocity
            self.yvector = world.simon.rect.y

            if world.simon.rect.x < self.rect.x:
                self.xvector = -1
            else:
                self.xvector = 1

        if self.xvector < 0:
            self.movx -= self.velocity
        elif self.xvector > 0:
            self.movx += self.velocity

        if self.yvector <= self.rect.y:
            self.yvector -= 5
            self.movy -= self.velocity
        elif self.yvector > self.rect.y:
            self.movy += self.velocity

        self.rect.x += self.movx
        self.rect.y += self.movy


        if self.frame > 0:
            self.frame -= 1
        else:
            self.frame = FPS

        f = self.frame / 10
        if f == 1 or f == 4:
            self.image = self.image1
        elif f == 2 or f == 5:
            self.image = self.image2
        elif f == 3:
            self.image = self.image3

        if self.movx < 0:
            self.direction = "Left"
        elif self.movx > 0:
            self.direction = "Right"

        if self.direction == "Right":
            self.image = pygame.transform.flip(self.image, True, False)

class Ghoul(Actor):
    """Class that represents Ghouls in the game world"""

    cost = 10

    def __init__(self, xpos, ypos):
        Actor.__init__(self, xpos, ypos)
        self.image1 = pygame.image.load("assets/ghoul/ghoul1.png")
        self.image2 = pygame.image.load("assets/ghoul/ghoul2.png")
        self.image = self.image1
        self.hitboxoffset = 0
        self.is_grounded = False
        self.is_vector_set = False
        self.xvector = 0
        self.__name__ = "Ghoul"

        self.rect = pygame.Rect(xpos+self.hitboxoffset-32/2, ypos-61/2, 32, 61)

    def update(self, world):
        """Enemy AI processing"""
        self.movx = 0
        self.movy = 0
        self.image = self.image1

        if self.is_grounded:
            if self.is_vector_set:
                self.movx = self.xvector
            else:
                if world.simon.rect.x < self.rect.x:
                    self.xvector -= self.move
                elif world.simon.rect.x > self.rect.x:
                    self.xvector += self.move
                self.is_vector_set = True

            newx = self.rect.x + self.movx
            for box in world.obstacles:
                if box.colliderect(newx, self.rect.y, self.rect.width,
                                   self.rect.height):
                    self.xvector *= -1
        else:
            self.movy += world.gravity
            foot = self.rect.y + self.rect.height + 5
            for box in world.obstacles:
                if box.collidepoint(self.rect.x + self.rect.width/2, foot):
                    self.is_grounded = True

        self.rect.x += self.movx
        self.rect.y += self.movy

        if self.frame > 0:
            self.frame -= 1
        else:
            self.frame = FPS

        f = self.frame / 15
        if f == 1 or f == 3:
            self.image = self.image1
        else:
            self.image = self.image2

        if self.movx < 0:
            self.direction = "Left"
        elif self.movx > 0:
            self.direction = "Right"

        if self.direction == "Right":
            self.image = pygame.transform.flip(self.image, True, False)

class Simon(Actor):

    static_image = pygame.image.load("assets/simon/stand.png")
    """Class that represents player 1 in the game world"""
    def __init__(self, xpos, ypos):
        Actor.__init__(self, xpos, ypos)

        self.image = pygame.image.load("assets/simon/stand.png")
        self.hitboxoffset = 56
        self.rect = pygame.Rect(xpos+self.hitboxoffset, ypos, 32, 61)
        self.maxhealth = 7
        self.health = self.maxhealth

        self.is_jumping = False
        self.is_climbing = False
        self.is_falling = False
        self.is_attacking = False
        self.left_jump = False
        self.right_jump = False
        self.is_standing = True
        self.is_big_toss = False
        self.invul = False
        self.invul_frame = -1
        self.max_invul_frames = 120

        self.inputs = []

        self.attack = pygame.Rect(0, 0, 0, 0)
        self.attack_frame = -1
        self.attack_size = (50, 15)

        self.move = 2
        self.jump_velocity = 8.0
        self.jump_decay = .25
        self.velocity = 0
        self.sjmod = 1

        self.climb_index = -1

        self.spritesheet = {}
        os.chdir("assets/simon")
        for files in os.listdir("."):
            if files.endswith(".png"):
                self.spritesheet[files] = (pygame.image.load
                                           (files).convert_alpha())
        os.chdir("../..")

    def receive_hit(self, enemyrelpos):
        if not self.invul:
            self.health -= 1
            self.invul = True
            self.invul_frame = 0

            if not self.is_climbing:
                self.attack_frame = -1
                self.is_attacking = False
                self.attack = pygame.Rect(0, 0, 0, 0)
                self.left_jump = False
                self.right_jump = False

                self.rect.y -= 3
                self.is_big_toss = True
                self.is_jumping = True
                self.velocity = self.jump_velocity
                self.right_jump = bool(enemyrelpos == "Left")

    def update(self, inputs, world):
        """update the state of Simon based on inputs and previous state"""
        self.inputs = inputs
        self.movx = 0
        self.movy = 0
        self.image = self.spritesheet["stand.png"]

        if not self.invul:
            pass
        elif self.invul_frame < self.max_invul_frames:
            self.invul_frame += 1
        else:
            self.invul_frame = -1
            self.invul = False


        #Check valid input based on state
        if self.is_big_toss:
            self.velocity -= self.jump_decay
        elif self.is_jumping:
            if self.inputs["b"] and not self.is_attacking:
                self.is_attacking = True
                self.attack_frame = 1
            self.velocity -= self.jump_decay
        elif self.is_climbing:
            if self.is_attacking:
                pass
            elif self.inputs["up"]:
                if world.top_stairs[self.climb_index][0] < self.rect.x:
                    self.rect.x -= 1
                    self.rect.y -= 1
                    self.direction = "Left"
                else:
                    self.rect.x += 1
                    self.rect.y -= 1
                    self.direction = "Right"
                    if self.rect.y < world.top_stairs[self.climb_index][1]:
                        self.is_climbing = False
            elif self.inputs["down"]:
                if world.bot_stairs[self.climb_index][0] < self.rect.x:
                    self.rect.x -= 1
                    self.rect.y += 1
                    self.direction = "Left"
                else:
                    self.rect.x += 1
                    self.rect.y += 1
                    self.direction = "Right"
                    if self.rect.y > world.bot_stairs[self.climb_index][1]:
                        self.is_climbing = False
            if self.inputs["b"] and not self.is_attacking:
                self.is_attacking = True
                self.attack_frame = 1

        #Disallow movement if falling
        elif self.is_falling:
            self.image = self.spritesheet["jump.png"]
        else:
            if self.is_attacking:
                pass
            else:
                if self.inputs["a"]:
                    self.is_jumping = True
                    self.velocity = self.jump_velocity

                    if self.inputs["left"]:
                        self.left_jump = True
                    elif self.inputs["right"]:
                        self.right_jump = True

                if self.inputs["b"]:
                    self.is_attacking = True
                    self.attack_frame = 1
                else:
                    if self.inputs["left"]:
                        self.movx -= self.move
                    elif self.inputs["right"]:
                        self.movx += self.move
                    #Stair Mounting
                    elif self.inputs["up"]:
                        for i, step in enumerate(world.bot_stairs):
                            hook = pygame.Rect((step[0] - world.stair_width/2,
                                                step[1]), (world.stair_width,
                                                           world.stair_height))
                            player = pygame.Rect(self.rect.x, self.rect.y,
                                                 self.rect.width, self.rect.height)

                            if hook.colliderect(player):
                                self.is_climbing = True
                                self.climb_index = i
                                self.rect.x = step[0]
                    elif self.inputs["down"]:
                        for i, step in enumerate(world.top_stairs):
                            hook = pygame.Rect((step[0] - world.stair_width/2,
                                                step[1]), (world.stair_width,
                                                              world.stair_height))
                            player = pygame.Rect(self.rect.x, self.rect.y,
                                                 self.rect.width, self.rect.height)

                            if hook.colliderect(player):
                                self.is_climbing = True
                                self.climb_index = i
                                self.rect.x = step[0]


        #Character action definitions
        if not self.is_climbing:
            foot = self.rect.y + self.rect.height + 4
            for box in world.obstacles:
                if not box.collidepoint(self.rect.x, foot):
                    self.is_falling = True

            if self.left_jump:
                self.movx -= self.move * self.sjmod
            elif self.right_jump:
                self.movx += self.move * self.sjmod

            self.movy -= self.velocity
            self.movy += world.gravity


            #Gravity and collission handling
            for box in world.obstacles:
                if self.rect.colliderect(box):
                    self.rect.y = box.y - self.rect.height
                    self.velocity = 0.0
                    self.is_falling = False
                    self.is_jumping = False
                    self.left_jump = False
                    self.right_jump = False
                    self.is_big_toss = False

                for box in world.obstacles:
                    if box.colliderect(self.rect.x, self.rect.y+self.movy,
                                       self.rect.width, self.rect.height/10):
                        self.movy += self.rect.height/10
                        self.velocity = 0.0
                        self.is_falling = True

            self.rect.y += self.movy

            newx = self.rect.x + self.movx

            for box in world.obstacles:
                if box.colliderect(newx, self.rect.y-world.gravity,
                                   self.rect.width, self.rect.height):
                    newx = self.rect.x
            self.rect.x = newx

       #Sprite processing
        if not self.is_jumping:
            self.is_standing = bool(self.movx == 0)
        else:
            self.image = self.spritesheet["jump.png"]

        if not self.is_standing and not self.is_jumping:
            if self.movx != 0:

                f = world.frame / 15
                if f == 1 or f == 3:
                    self.image = self.spritesheet["walk1.png"]
                else:
                    self.image = self.spritesheet["walk2.png"]

        if self.is_climbing:
            f = world.frame / 15
            if f == 1 or f == 3:
                self.image = self.spritesheet["stairs1.png"]
            else:
                self.image = self.spritesheet["stairs2.png"]

        if self.is_attacking:
            f = self.attack_frame / 10 + 1
            if self.is_jumping:
                self.image = self.spritesheet["jumpattack" + str(f) + ".png"]
            elif self.is_climbing:
                self.image = self.spritesheet["stairsattack" + str(f) +".png"]
            else:
                self.image = self.spritesheet["attack" + str(f) + ".png"]
            if f == 3:
                if self.direction == "Left":
                    self.attack = pygame.Rect((self.rect.x - 60, self.rect.y + 20),
                                              (self.attack_size))
                else:
                    self.attack = pygame.Rect((self.rect.x + self.rect.width + 10,
                                               self.rect.y + 20), (self.attack_size))
            if self.attack_frame < 29:
                self.attack_frame += 1
            else:
                self.attack_frame = -1
                self.is_attacking = False
                self.attack = pygame.Rect(0, 0, 0, 0)

        if self.is_big_toss:
            self.image = self.spritesheet["damage.png"]


        if self.movx < 0:
            self.direction = "Left"
        elif self.movx > 0:
            self.direction = "Right"

        if self.direction == "Right":
            self.image = pygame.transform.flip(self.image, True, False)

        if self.invul_frame % 2 == 0:
            self.image = self.spritesheet["flash.png"]


if __name__ == "__main__":
    choose_player_type()
