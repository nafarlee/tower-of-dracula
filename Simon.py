import os

import pygame

from Actor import Actor

class Simon(Actor):

    static_image = pygame.image.load("assets/simon/stand.png")
    """Class that represents player 1 in the game world"""
    def __init__(self, xpos, ypos):
        Actor.__init__(self)

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
