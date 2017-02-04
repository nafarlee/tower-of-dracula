import pygame
import math

from Actor import Actor
from Vector import Vector

class Bat(Actor):
    """The class that represents bats in the game world."""

    cost = 35
    hitbox_height = 50
    hitbox_width = 30
    hitbox_offset = 0
    swoop_delay = 100
    swoop_initial_velocity = Vector(5, 5)
    swoop_acceleration = Vector(-.1, -.1)

    def __init__(self, xpos, ypos):
        super().__init__()

        self.images = [
            pygame.image.load("assets/bat/bat1.png"),
            pygame.image.load("assets/bat/bat2.png"),
            pygame.image.load("assets/bat/bat3.png")
        ]
        self.image = self.images[0]

        self.rect = pygame.Rect(xpos-30/2, ypos-30/2, Bat.hitbox_width, Bat.hitbox_height)
        self.frames_till_swoop = Bat.swoop_delay
        self.velocity = Vector(0, 0)
        self.direction = Vector(1, 1)
        self.orientation = "Left"
        self.has_pitched = False
        self.is_swooping = False
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
            self.orientation = "Left"
        elif movx > 0:
            self.orientation = "Right"

        if self.orientation == "Right":
            image = pygame.transform.flip(image, True, False)

        return image

    def _initiate_swoop(self, simon_rect):
        self.is_swooping = True
        self.velocity = Bat.swoop_initial_velocity
        x_direction = 1 if self.rect.x <= simon_rect.x else -1
        y_direction = 1 if self.rect.y <= simon_rect.y else -1
        self.direction = Vector(x_direction, y_direction)
        self.has_pitched = False if y_direction == 1 else True

    def update(self, world):
        """enemy AI processing"""
