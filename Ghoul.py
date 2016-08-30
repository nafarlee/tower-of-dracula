import pygame

from Actor import Actor

class Ghoul(Actor):
    """Class that represents Ghouls in the game world"""

    cost = 10
    spritesheet = [
        pygame.image.load("assets/ghoul/ghoul1.png"),
        pygame.image.load("assets/ghoul/ghoul2.png")
    ]
    hitboxoffset = 0
    __name__ = "Ghoul"

    def __init__(self, x_position, y_position):
        Actor.__init__(self)
        self.image = self.spritesheet[0]
        self.state = GhoulStates.DROPPING
        self.xvector = 0

        (width, height) = self.image.get_size()
        left = x_position - width / 2
        top = y_position - height / 2
        self.rect = pygame.Rect(left, top, width, height)

    def render(self):
        if self.frame == 30:
            self.frame = 0
        else:
            self.frame = self.frame + 1

        if self.frame < 15:
            self.image = self.spritesheet[0]
        else:
            self.image = self.spritesheet[1]

        if self.movx < 0:
            self.direction = "Left"
        elif self.movx > 0:
            self.direction = "Right"

        if self.direction == "Right":
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, world):
        """Enemy AI processing"""
        self.movx = 0
        self.movy = 0

        if self.state == GhoulStates.DROPPING:
            self.movy += world.gravity
            foot = self.rect.y + self.rect.height + 5
            for box in world.obstacles:
                if box.collidepoint(self.rect.x + self.rect.width/2, foot):
                    self.state = GhoulStates.LANDING

        elif self.state == GhoulStates.LANDING:
            if world.simon.rect.x < self.rect.x:
                self.xvector -= self.move
            elif world.simon.rect.x > self.rect.x:
                self.xvector += self.move
            self.state = GhoulStates.SHAMBLING

        elif self.state == GhoulStates.SHAMBLING:
            self.movx = self.xvector
            newx = self.rect.x + self.movx
            for box in world.obstacles:
                if box.colliderect(newx, self.rect.y, self.rect.width, self.rect.height):
                    self.xvector *= -1
                    break

        self.rect.move_ip(self.movx, self.movy)
        self.render()

class GhoulStates(object):
    DROPPING, LANDING, SHAMBLING = range(3)