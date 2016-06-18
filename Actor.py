import pygame

class Actor(pygame.sprite.Sprite):
    """Base class for all entities in the game world"""

    FPS = 60

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.movy = 0
        self.movx = 0
        self.move = 1
        self.hitboxoffset = 0
        self.image = None
        self.rect = None
        self.frame = 0
        self.direction = "Left"
        self.maxhealth = 1
        self.health = self.maxhealth
        return
