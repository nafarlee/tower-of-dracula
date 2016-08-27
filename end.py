import sys

import render
import pygame

def youwin(screen, socket):
    render.blit_large_label(screen, "You Win!")
    pygame.display.flip()

    pygame.time.delay(4000)
    socket.close()
    pygame.quit()
    sys.exit()

def youlose(screen, socket):
    render.blit_large_label(screen, "You Lose!")
    pygame.display.flip()

    pygame.time.delay(4000)
    socket.close()
    pygame.quit()
    sys.exit()