'''Castlevania Tower Defense Game'''
__author__ = 'farley'
import pygame, sys, os
from pygame.locals import *

FPS = 60
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BG_COLOR = pygame.Color('#271b8f')

def main():
    '''Run the game with default settings'''
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.mixer.music.load("sounds/vamp.mp3")
    pygame.mixer.music.play(-1)

    inputs = {
            "up":       False, 
            "left":     False, 
            "right":    False, 
            "a":        False, 
            "b":        False, 
    }
    fpsclock = pygame.time.Clock()
    camerax = 735
    cameray = 453
    playerx = 1400
    playery = 950
    masker = False
    back = pygame.image.load("level/background.png").convert_alpha()
    mask = pygame.image.load("level/backgroundmask.png").convert_alpha()

    world = World(playerx, playery)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

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

                if event.key == K_m:
                    masker = True
                if event.key == K_b:
                    masker = False
                if event.key == K_o:
                    camerax = 700
                    cameray = 400

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


        world.simon.update(inputs, world)


        camera = Rect(camerax, cameray, WINDOW_WIDTH, WINDOW_HEIGHT)
        screen.fill(BG_COLOR)
        screen.blit(world.background, (-camerax, -cameray))
        if masker:
            for box in world.obstacles:
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 255, 0), (box.x-camera.x, 
                                     box.y-camera.y, box.width, box.height))
        for sprite in world.all_sprites:
            if camera.colliderect(sprite.rect):
                screen.blit(sprite.image, (sprite.rect.x-camera.x,
                            sprite.rect.y-camera.y))


        pygame.display.flip()
        fpsclock.tick(FPS)
        pygame.display.set_caption('Vania ' + str(int(fpsclock.get_fps())))


class World(object):
    '''Class that represents the state of the game world'''
    def __init__(self, playerx, playery):
        self.simon = Simon(playerx, playery)
        self.obstacles = self.mask_generate()
        self.background = pygame.image.load("level/background.png").convert_alpha()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.simon)
        self.gravity = 3

    def mask_generate(self):
        '''Returns a list of rectangle objects based on image mask'''
        background_mask = pygame.image.load("level/backgroundmask.png").convert_alpha()
        level_mask = pygame.mask.from_surface(background_mask)
        level_collisions = level_mask.get_bounding_rects()
        return level_collisions

class Actor(pygame.sprite.Sprite):
    '''Base class for all entities in the game world'''
    def __init__(self, xpos, ypos):
        pygame.sprite.Sprite.__init__(self)
        self.movy = 0
        self.movx = 0
        self.xpos = xpos
        self.ypos = ypos
        self.image = None

class Simon(Actor):
    '''Class that represents player 1 in the game world'''
    def __init__(self, xpos, ypos):
        Actor.__init__(self, xpos, ypos)

        self.image = pygame.image.load("simon/stand.png")
        self.rect = Rect(xpos, ypos, self.image.get_width(),
                         self.image.get_height())

        self.is_jumping = False
        self.direction = "Left"
        self.is_falling = False
        self.is_attacking = False
        self.left_jump = False
        self.right_jump = False
        self.inputs = []

        self.move = 2
        self.gravity = 3
        self.jump_height = 80
        self.velocity = 0
        self.sjmod = 1
        self.tip = 0

        self.spritesheet = {}
        os.chdir("simon")
        for files in os.listdir("."):
            if files.endswith(".png"):
                self.spritesheet[files] = pygame.image.load(files)
        os.chdir("..")

        for images in self.spritesheet:
            print images
            print self.spritesheet[images]

    def update(self, inputs, world):
        '''update the state of Simon based on inputs and previous state'''
        self.inputs = inputs
        self.movx = 0
        self.movy = 0
        self.image = self.spritesheet["stand.png"]

        if self.is_jumping:
            self.image = self.spritesheet["jump.png"]
            if self.rect.y < self.tip:
                self.velocity = 0

        elif self.is_falling:
            pass
        else:
            if self.inputs["a"]:
                self.is_jumping = True
                self.velocity = self.jump_height *.07
                self.tip = self.rect.y - self.jump_height

                if self.inputs["left"]:
                    self.left_jump = True
                elif self.inputs["right"]:
                    self.right_jump = True

            else:
                if self.inputs["left"]:
                    self.movx -= self.move
                elif self.inputs["right"]:
                    self.movx += self.move
        if self.inputs["up"]:
            self.movy -= self.gravity*3
        
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

        
        for box in (world.obstacles):
            if self.rect.colliderect(box):
                self.rect.y = box.y - self.rect.height
                self.velocity = 0
                self.is_falling = False
                self.is_jumping = False
                self.left_jump = False
                self.right_jump = False
        
        for box in world.obstacles:
            if box.colliderect(self.rect.x, self.rect.y+self.movy, 
                               self.rect.width, self.rect.height/10):
                self.movy += self.rect.height/10
                self.velocity = 0
                self.is_falling = True
        self.rect.y += self.movy

        newx = self.rect.x + self.movx
        for box in world.obstacles:
            if box.colliderect(newx, self.rect.y-world.gravity, self.rect.width, self.rect.height):
                newx = self.rect.x
        self.rect.x = newx

if __name__ == "__main__":
    main()

