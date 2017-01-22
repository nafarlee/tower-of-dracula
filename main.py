#!/usr/bin/env python
"""Castlevania Tower Defense Game"""


import pygame

import first_player
import second_player

__author__ = 'Nicholas Farley'

BG_COLOR = pygame.Color('#271b8f')
FPS = 60

WINDOW_WIDTH = int(input("Enter desired window width: "))
assert WINDOW_WIDTH >= 640, "Window == gonna be too short"

WINDOW_HEIGHT = int(input("Enter desired window height: "))
assert WINDOW_HEIGHT >= 480, "Window == gonna be too thin"


def choose_player_type():
    """Choose which player to be"""
    player_type = input("Would you like to play as Simon or Dracula? ").lower()

    if player_type[0] == 's':
        return "first"
    elif player_type[0] == 'd':
        return "second"
    else:
        print "invalid choice"
        return choose_player_type()

if __name__ == "__main__":
    player_type = choose_player_type()
    if player_type == "first":
        first_player.main(FPS, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT)
    elif player_type == "second":
        second_player.main(FPS, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT)
