#!/usr/bin/env python
#Perfect World Runtime - 80 seconds
'''Castlevania Tower Defense Game'''

__author__ = 'farley'

import sys, os
import pygame
from random import randrange
from pygame.locals import *

FPS = 60
WINDOW_WIDTH = int(raw_input("Enter desired window width: "))
assert WINDOW_WIDTH >= 640, "Window is gonna be too short"
WINDOW_HEIGHT = int(raw_input("Enter desired window height: " ))
assert WINDOW_HEIGHT >= 480, "Window is gonna be too thin"
BG_COLOR = pygame.Color('#271b8f')

def main():
    '''Run the game with default settings'''

    #init
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.mixer.music.load("sounds/vamp.mp3")
    pygame.mixer.music.play(-1)

    font = pygame.font.SysFont(None, 50)

    inputs = {
            "up":       False, 
            "down":     False,
            "left":     False, 
            "right":    False, 
            "a":        False, 
            "b":        False
    }
    fpsclock = pygame.time.Clock()
    camerax = 600
    cameray = 300
    playerx = 1388
    playery = 950
    masker = False

    enemy_type = "Zombie"

    world = World(playerx, playery)
    
    #Game Loop
    while True:
        #Input Handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type is MOUSEBUTTONUP:
                mousex, mousey = event.pos
                xpos = mousex + camerax
                ypos = mousey + cameray
                world.create_enemy(xpos, ypos, enemy_type)


            if event.type == KEYDOWN:
                move = 30
                if event.key == K_UP:
                    cameray -= move
                if event.key == K_DOWN:
                    cameray += move
                if event.key == K_LEFT:
                    camerax -= move
                if event.key == K_RIGHT:
                    camerax += move
                if event.key == K_c:
                    camerax = world.simon.rect.x - WINDOW_WIDTH /2
                    cameray = world.simon.rect.y - WINDOW_HEIGHT /2

                if event.key == K_m:
                    masker = True
                if event.key == K_b:
                    masker = False
                if event.key == K_o:
                    camerax = 700
                    cameray = 400

                if event.key == K_1:
                    enemy_type = "Zombie"
                if event.key == K_2:
                    enemy_type = "Bat"

                if event.key == K_w:
                    inputs["up"] = True
                if event.key == K_s:
                    inputs["down"] = True
                if event.key == K_a:
                    inputs["left"] = True
                if event.key == K_d:
                    inputs["right"] = True
                if event.key == K_SPACE:
                    inputs["a"] = True
                if event.key == K_LSHIFT:
                    inputs["b"] = True

                if event.key == K_p:
                    world.create_enemy(randrange(1400), randrange(800))

            if event.type == KEYUP:
                if event.key == K_w:
                    inputs["up"] = False
                if event.key == K_s:
                    inputs["down"] = False
                if event.key == K_a:
                    inputs["left"] = False
                if event.key == K_d:
                    inputs["right"] = False
                if event.key == K_SPACE:
                    inputs["a"] = False
                if event.key == K_LSHIFT:
                    inputs["b"] = False


        #MAIN UPDATING PROCEDURE
        world.update(inputs)

        #Drawing Prodecures
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
            cameray += 2

        camera = Rect(camerax, cameray, WINDOW_WIDTH, WINDOW_HEIGHT)
        screen.fill(BG_COLOR)
        screen.blit(world.background, (-camerax, -cameray))

                    

        for sprite in world.all_sprites:
            if camera.colliderect(sprite.rect):
                screen.blit(sprite.image,
                           (sprite.rect.x-camera.x-sprite.hitboxoffset,
                            sprite.rect.y-camera.y))

        if masker:
            if world.simon.is_attacking:
                box = world.simon.attack
                pygame.draw.rect(screen, (255, 0, 0), (box.x-camera.x, 
                                 box.y-camera.y, box.width, box.height))
            for box in world.obstacles:
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 255, 0), (box.x-camera.x, 
                                     box.y-camera.y, box.width, box.height))
            for steps in world.top_stairs:
                box = Rect((steps[0] - world.stair_width/2, steps[1]), 
                           (world.stair_width, world.stair_height))
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 0, 255), (box.x-camera.x, 
                                     box.y-camera.y, box.width, box.height))
            for steps in world.bot_stairs:
                box = Rect((steps[0] - world.stair_width/2, steps[1]), 
                           (world.stair_width, world.stair_height))
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 0, 255), (box.x-camera.x, 
                                     box.y-camera.y, box.width, box.height))
            for enemy in world.enemies:
                box = enemy.rect
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 255, 255), (box.x-camera.x, 
                                     box.y-camera.y, box.width, box.height))

        label = font.render(str(world.simon.health), 1, (255,255,255))
        screen.blit(label, (10, 10)) 
        label = font.render(str(world.time), 1, (255,255,255))
        screen.blit(label, (10, 60)) 

        label = font.render(enemy_type, 1, (255,255,255))
        screen.blit(label, (10, 110)) 

        pygame.display.flip()


        fpsclock.tick(FPS)
        pygame.display.set_caption('Vania ' + str(int(fpsclock.get_fps())))


class World(object):
    '''Class that represents the state of the game world'''
    def __init__(self, playerx, playery):
        self.simon = Simon(playerx, playery)
        self.obstacles = self.generate_obstacles()
        self.background = (pygame.image.load
                ("level/background.png").convert_alpha())
        self.enemies = []
        self.all_sprites = []
        self.all_sprites.append(self.simon)
        self.gravity = 3
        self.frame = 0
        self.time_limit = 180
        self.time = self.time_limit

        self.stair_width = 100
        self.stair_height = 40
        self.bot_stairs = [
                (320, 808),
                (94, 582),
                (752, 584),
                (1275,582),
                (2660, 520),
                (2799, 390),
        ]
        self.top_stairs = [
                (94, 582),
                (235, 440),
                (814,520),
                (1137, 454),
                (2799, 390),
                (2567, 164),
        ]

    def update(self, inputs):
        '''call all world processing routines'''
        if self.frame < FPS:
            self.frame  += 1
        else:
            self.frame = 0
            self.time -= 1

        self.simon.update(inputs, self)
        for i, enemy in enumerate(self.enemies):
            enemy.update(self)
            if self.simon.is_attacking:
                box = self.simon.attack
                if box.colliderect(enemy.rect):
                    self.destroy_actor(i)
            box = self.simon.rect
            if (box.colliderect(enemy)):
                if box.x < enemy.rect.x:
                    self.simon.recieve_hit("Right")
                else:
                    self.simon.recieve_hit("Left")
                    


    def generate_obstacles(self):
        '''Returns a list of rectangle objects based on image mask'''
        background_mask = (pygame.image.load
                ("level/backgroundmask.png").convert_alpha())
        level_mask = pygame.mask.from_surface(background_mask)
        level_collisions = level_mask.get_bounding_rects()
        return level_collisions

    def create_enemy(self, xpos, ypos, type="Bat"):
        '''create an enemy in the game world'''
        if type is "Zombie":
            self.enemies.append(Zombie(xpos, ypos))
            self.all_sprites.append(self.enemies[-1])
        elif type is "Bat":
            self.enemies.append(Bat(xpos, ypos))
            self.all_sprites.append(self.enemies[-1])
        
    def destroy_actor(self, index):
        '''removes an enemy in the game world'''
        del self.enemies[index]
        del self.all_sprites[index+1]

class Actor(pygame.sprite.Sprite):
    '''Base class for all entities in the game world'''

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
    '''Class the represents bats in the game world.'''
    def __init__(self, xpos, ypos):
        Actor.__init__(self, xpos, ypos)
        self.image1 = pygame.image.load("enemy/bat1.png")
        self.image2 = pygame.image.load("enemy/bat2.png")
        self.image3 = pygame.image.load("enemy/bat3.png")
        self.image = self.image1

        self.hitboxoffset = 0
        self.rect = Rect(xpos+self.hitboxoffset-30/2, ypos-30/2, 30, 50)
        self.swoop = 120
        self.swoop_frame = self.swoop
        self.swoop_velocity = 5
        self.swoop_decay = .1
        self.velocity = 0
        self.xvector = 0
        self.yvector = 0

    def update(self, world):
        '''enemy AI processing'''
        self.movx = 0
        self.movy = 0
        self.image = self.image1

        print self.velocity
        print self.swoop_decay

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
        if f is 1 or f is 4:
            self.image = self.image1
        elif f is 2 or f is 5:
            self.image = self.image2
        elif f is 3:
            self.image = self.image3

        if self.movx < 0:
            self.direction = "Left"
        elif self.movx > 0:
            self.direction = "Right"

        if self.direction is "Right":
            self.image = pygame.transform.flip(self.image, True, False)

class Zombie(Actor):
    '''Class that represents zombies in the game world'''
    def __init__(self, xpos, ypos):
        Actor.__init__(self, xpos, ypos)
        self.image1 = pygame.image.load("enemy/zombie1.png")
        self.image2 = pygame.image.load("enemy/zombie2.png")
        self.image = self.image1
        self.hitboxoffset = 0

        self.rect = Rect(xpos+self.hitboxoffset-32/2, ypos-61/2, 32, 61)

    def update(self, world):
        '''Enemy AI processing'''
        self.movx = 0
        self.movy = 0
        self.image = self.image1
        if world.simon.rect.x < self.rect.x:
            self.movx -= self.move
        elif world.simon.rect.x > self.rect.x:
            self.movx += self.move
        if world.simon.rect.y < self.rect.y:
            self.movy -= self.move
        elif world.simon.rect.y > self.rect.y: 
            self.movy += self.move

        self.rect.x += self.movx
        self.rect.y += self.movy

        if self.frame > 0:
            self.frame -= 1
        else:
            self.frame = FPS

        f = self.frame / 15
        if f is 1 or f is 3:
            self.image = self.image1
        else:
            self.image = self.image2

        if self.movx < 0:
            self.direction = "Left"
        elif self.movx > 0:
            self.direction = "Right"

        if self.direction is "Right":
            self.image = pygame.transform.flip(self.image, True, False)



    def recieve_hit(self):
        '''actions to take when hit by player1's attack'''
        pass
        

class Simon(Actor):
    '''Class that represents player 1 in the game world'''
    def __init__(self, xpos, ypos):
        Actor.__init__(self, xpos, ypos)

        self.image = pygame.image.load("simon/stand.png")
        self.hitboxoffset = 56
        self.rect = Rect(xpos+self.hitboxoffset, ypos, 32, 61)
        self.maxhealth = 3
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

        self.attack = Rect(0,0,0,0)
        self.attack_frame = -1
        self.attack_size = (50, 15)

        self.move = 2
        self.jump_velocity = 8.0
        self.jump_decay = .25
        self.velocity = 0
        self.sjmod = 1

        self.climb_index = -1

        self.spritesheet = {}
        os.chdir("simon")
        for files in os.listdir("."):
            if files.endswith(".png"):
                self.spritesheet[files] = (pygame.image.load
                        (files).convert_alpha())
        os.chdir("..")

    def die(self):
        pygame.quit()
        sys.exit()

    def recieve_hit(self, enemyrelpos):
        if not self.invul:
            self.health -= 1
            if self.health is 0:
                self.die()
            self.invul = True
            self.invul_frame = 0

            if not self.is_climbing:
                self.attack_frame = -1
                self.is_attacking = False
                self.attack = Rect(0,0,0,0)
                self.left_jump = False
                self.right_jump = False

                self.rect.y -= 5
                self.is_big_toss = True
                self.is_jumping = True
                self.velocity = self.jump_velocity
                if enemyrelpos is "Left":
                    self.right_jump = True
                else:
                    self.left_jump = True

            

    def update(self, inputs, world):
        '''update the state of Simon based on inputs and previous state'''
        self.inputs = inputs
        self.movx = 0
        self.movy = 0
        self.image = self.spritesheet["stand.png"]

        if self.invul is False:
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
            if self.inputs["b"] and self.is_attacking is False:
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
            if self.inputs["b"] and self.is_attacking is False:
                self.is_attacking = True
                self.attack_frame = 1

        #Disallow movement if falling
        elif self.is_falling:
            self.image = self.spritesheet["jump.png"]
            pass
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
                            hook = Rect( (step[0] - world.stair_width/2, 
                                step[1]), (world.stair_width, 
                                    world.stair_height))
                            player = Rect(self.rect.x, self.rect.y,
                                          self.rect.width, self.rect.height)

                            if hook.colliderect(player):
                                self.is_climbing = True
                                self.climb_index = i
                                self.rect.x = step[0]
                    elif self.inputs["down"]:
                        for i, step in enumerate(world.top_stairs):
                            hook = Rect( (step[0] - world.stair_width/2, 
                                step[1]), (world.stair_width, 
                                    world.stair_height))
                            player = Rect(self.rect.x, self.rect.y,
                                          self.rect.width, self.rect.height)

                            if hook.colliderect(player):
                                self.is_climbing = True
                                self.climb_index = i
                                self.rect.x = step[0]


        #Character action definitions
        if self.is_climbing is False:
            foot = self.rect.y + self.rect.height + 4
            for box in world.obstacles:
                if box.collidepoint(self.rect.x, foot) == False:
                    self.is_falling = True

            if self.left_jump:
                self.movx -= self.move * self.sjmod
            elif self.right_jump:
                self.movx += self.move * self.sjmod

            self.movy -= self.velocity
            self.movy += world.gravity

            
            #Gravity and collission handling
            for box in (world.obstacles):
                if self.rect.colliderect(box):
                    self.rect.y = box.y - self.rect.height
                    self.velocity = 0
                    self.is_falling = False
                    self.is_jumping = False
                    self.left_jump = False
                    self.right_jump = False
                    self.is_big_toss = False

                for box in world.obstacles:
                    if box.colliderect(self.rect.x, self.rect.y+self.movy, 
                                    self.rect.width, self.rect.height/10):
                        self.movy += self.rect.height/10
                        self.velocity = 0
                        self.is_falling = True

            self.rect.y += self.movy

            newx = self.rect.x + self.movx
        
            for box in world.obstacles:
                if box.colliderect(newx, self.rect.y-world.gravity, 
                        self.rect.width, self.rect.height):
                    newx = self.rect.x
            self.rect.x = newx

#Sprite processing
        if self.is_jumping is False:
            if self.movx is 0:
                self.is_standing = True
            else:
                self.is_standing = False
        else:
            self.image = self.spritesheet["jump.png"]

        if self.is_standing is False and self.is_jumping is False:
            if self.movx is not 0:
                
                f = world.frame / 15
                if f is 1 or f is 3:
                    self.image = self.spritesheet["walk1.png"]
                else:
                    self.image = self.spritesheet["walk2.png"]

        if self.is_climbing:
            f = world.frame / 15
            if f is 1 or f is 3:
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
            if f is 3:
                if self.direction is "Left":
                    self.attack = Rect((self.rect.x - 60, self.rect.y + 20), 
                            (self.attack_size))
                else:
                    self.attack = Rect((self.rect.x + self.rect.width + 10, 
                            self.rect.y + 20), (self.attack_size))
            if self.attack_frame < 29:
                self.attack_frame += 1
            else:
                self.attack_frame = -1
                self.is_attacking = False
                self.attack = Rect(0,0,0,0)
        
        if self.is_big_toss:
            self.image = self.spritesheet["damage.png"]


        if self.movx < 0:
            self.direction = "Left"
        elif self.movx > 0:
            self.direction = "Right"

        if self.direction is "Right":
            self.image = pygame.transform.flip(self.image, True, False)


if __name__ == "__main__":
    main()

