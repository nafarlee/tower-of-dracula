#!/usr/bin/env python
'''Castlevania Tower Defense Game'''
__author__ = 'farley'
import pygame, sys, os
from pygame.locals import *



FPS = 60
WINDOW_WIDTH = int(raw_input("Enter Screen width: "))
WINDOW_HEIGHT = int(raw_input("Enter Screen height: " ))
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
    playerx = 1388
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
            if world.simon.is_attacking:
                box = world.simon.attack
                pygame.draw.rect(screen, (255, 0, 0), (box.x-camera.x, 
                                 box.y-camera.y, box.width, box.height))
                pass
            for box in world.obstacles:
                if box.colliderect(camera):
                    pygame.draw.rect(screen, (0, 255, 0), (box.x-camera.x, 
                                     box.y-camera.y, box.width, box.height))

        for sprite in world.all_sprites:
            if camera.colliderect(sprite.rect):
                screen.blit(sprite.image, (sprite.rect.x-camera.x-sprite.hitboxoffset,
                            sprite.rect.y-camera.y))

        pygame.display.flip()
        fpsclock.tick(FPS)

        if world.frame < FPS:
            world.frame  += 1
        else:
            world.frame = 0
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
        self.frame = 0

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
        self.hitboxoffset = 0
        self.xpos = xpos
        self.ypos = ypos
        self.image = None

class Simon(Actor):
    '''Class that represents player 1 in the game world'''
    def __init__(self, xpos, ypos):
        Actor.__init__(self, xpos, ypos)

        self.image = pygame.image.load("simon/stand.png")
        self.hitboxoffset = 56
        self.rect = Rect(xpos+self.hitboxoffset, ypos, 32, 61)


        self.is_jumping = False
        self.direction = "Left"
        self.is_falling = False
        self.is_attacking = False
        self.left_jump = False
        self.right_jump = False
        self.inputs = []
        self.is_standing = True
        self.attack_frame = -1

        self.attack = Rect(0,0,0,0)

        self.attack_size = (50, 15)

        self.move = 2
        self.gravity = 3
        self.jump_height = 65
        self.velocity = 0
        self.sjmod = 1
        self.tip = 0
        self.count = 0

        self.spritesheet = {}
        os.chdir("simon")
        for files in os.listdir("."):
            if files.endswith(".png"):
                self.spritesheet[files] = pygame.image.load(files).convert_alpha()
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

        #Main input processing
        if self.is_jumping:
            if self.inputs["b"] and self.is_attacking is False:
                self.is_attacking = True
                self.attack_frame = 1
            if self.rect.y < self.tip:
                self.velocity = 0

        elif self.is_falling:
            self.image = self.spritesheet["jump.png"]
            pass
        else:
            if self.is_attacking:
                pass
            else:
                if self.inputs["a"]:
                    self.is_jumping = True
                    self.velocity = self.jump_height *.075
                    self.tip = self.rect.y - self.jump_height

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

        #Main character processing
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

        if self.is_attacking:
            f = self.attack_frame / 15 + 1
            print self.attack_frame
            if self.is_jumping:
                self.image = self.spritesheet["jumpattack" + str(f) + ".png"]
            else:
                self.image = self.spritesheet["attack" + str(f) + ".png"]
            if f is 3:
                if self.direction is "Left":
                    self.attack = Rect((self.rect.x - 60, self.rect.y + 20), (self.attack_size))
                else:
                    self.attack = Rect((self.rect.x + self.rect.width + 10, self.rect.y + 20), (self.attack_size))
            if self.attack_frame < 44:
                self.attack_frame += 1
            else:
                self.attack_frame = -1
                self.is_attacking = False
                self.attack = Rect(0,0,0,0)


        if self.movx < 0:
            self.direction = "Left"
        elif self.movx > 0:
            self.direction = "Right"
        else:
            pass

        if self.direction is "Right":
            self.image = pygame.transform.flip(self.image, True, False)
        
        print self.rect.center

        


if __name__ == "__main__":
    main()

