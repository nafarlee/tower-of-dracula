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
        self.has_landed = False
        self.is_vector_set = False
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
        self.image = self.spritesheet[0]

        if self.has_landed:
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
                    self.has_landed = True

        self.rect.x += self.movx
        self.rect.y += self.movy

        self.render()