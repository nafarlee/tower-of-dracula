import pygame

def blit_large_label(screen, message):
    """Display a large heading in the center of the game screen"""
    font_size = 100
    width, height = screen.get_size()
    labelx = width/3 - font_size
    labely = height/2
    font = pygame.font.SysFont(None, font_size)
    label = font.render(message, 1, (255, 255, 255))

    screen.blit(label, (labelx, labely))