import pygame

from Simon import Simon
from Bat import Bat
from Ghoul import Ghoul

class World(object):
    """Class that represents the state of the game world"""

    FPS = 60

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
        if self.frame < self.FPS:
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
