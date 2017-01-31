import pygame
import math

from Actor import Actor

class Bat(Actor):
    """Class the represents bats in the game world."""

    cost = 35
    hitbox_offset = 0
    swoop_delay = 120
    swoop_initial_velocity = 5
    swoop_acceleration = -.1

    def __init__(self, xpos, ypos):
        super().__init__()

        self.images = [
            pygame.image.load("assets/bat/bat1.png"),
            pygame.image.load("assets/bat/bat2.png"),
            pygame.image.load("assets/bat/bat3.png")
        ]
        self.image = self.images[0]

        self.rect = pygame.Rect(xpos+Bat.hitbox_offset-30/2, ypos-30/2, 30, 50)
        self.frames_till_swoop = Bat.swoop_delay
        self.velocity = 0
        self.xvector = 0
        self.yvector = 0
        self.__name__ = "Bat"

    def _render(self, movx):
        if self.frame > 0:
            self.frame -= 1
        else:
            self.frame = Actor.FPS

        f = math.floor(self.frame / 10)
        image = self.images[0]
        if f == 1 or f == 4:
            image = self.images[0]
        elif f == 2 or f == 5:
            image = self.images[1]
        elif f == 3:
            image = self.images[2]

        if movx < 0:
            self.direction = "Left"
        elif movx > 0:
            self.direction = "Right"

        if self.direction == "Right":
            image = pygame.transform.flip(image, True, False)

        return image

    def update(self, world):
        """enemy AI processing"""
        movx = 0
        movy = 0
        self.image = self.images[0]

        self.velocity = max(self.velocity + Bat.swoop_acceleration, 0)

        if self.frames_till_swoop > 0:
            self.frames_till_swoop -= 1
        else:
            self.frames_till_swoop = Bat.swoop_delay
            self.velocity = Bat.swoop_initial_velocity
            self.yvector = world.simon.rect.y

            if world.simon.rect.x < self.rect.x:
                self.xvector = -1
            else:
                self.xvector = 1

        if self.xvector < 0:
            movx = -self.velocity
        elif self.xvector > 0:
            movx = self.velocity

        if self.yvector <= self.rect.y:
            self.yvector -= 5
            movy = -self.velocity
        else:
            movy = +self.velocity

        self.rect.x += movx
        self.rect.y += movy

        self.image = self._render(movx)
