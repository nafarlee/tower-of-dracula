import pygame
import math

from Actor import Actor

class Bat(Actor):
    """Class the represents bats in the game world."""

    cost = 35

    def __init__(self, xpos, ypos):
        Actor.__init__(self)
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
            self.frame = self.FPS

        f = math.floor(self.frame / 10)
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
