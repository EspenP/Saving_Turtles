#!/usr/bin/python3
import pygame
import numpy as np
import random
from ypstruct import structure
from PIL import Image


def image_to_tile(path_to_image, TILESIZE):
  img = Image.open(path_to_image)
  img = img.resize((TILESIZE, TILESIZE))
  return pygame.image.fromstring(img.tobytes(), img.size, img.mode)

# Which tile is this pixel in?
def which_tile(pos, game):
  x = pos[0]
  y = pos[1]
  x_ind = x // game.tilesize
  y_ind = game.height - (y // game.tilesize)
  return (x_ind, y_ind)

# Takes a numpy array of turtle objects, and the game object
def move_turtles(game):
  for turtle in game.turtle_list:
    ind = game.iteration
    tilesize = game.tilesize
    posx = turtle.rect.centerx # Pixel
    posy = turtle.rect.centery
    tile = which_tile((posx,posy),game)
    # print("\nGoing to ", turtle.path[ind])
    # print("\nAt ", which_tile((posx,posy),game))
    if ind >= len(turtle.path) - 1:
      game.screen.blit(turtle.surf, turtle.rect)
      continue
    if turtle.path[ind] == tile:
      ind += 1
      game.iteration = ind
    diffx = turtle.path[ind][0] - tile[0]
    diffy = turtle.path[ind][1] - tile[1]
    movex = 1
    movey = 1
    if not diffy:
      movey = 0
    if diffy > 0:
      movey *= -1
    if not diffx:
      movex = 0
    elif diffx < 0:
      movex *= -1
    turtle.rect.centerx += movex
    turtle.rect.centery += movey
    game.screen.blit(turtle.surf, turtle.rect)

def create_random_path(game):
  tile_size = game.tilesize
  lower_bound = 0 # Remember this is the top of the screen in pygame
  high_bound = game.height # And this is the bottom
  left_bound = 0
  right_bound = game.width
  game_map = game.map1
  start = which_tile(game.start, game)
  end = which_tile(game.end, game)
  print("End, start", end, start)
  tile_wise_path = []

  def is_end_path(pos):
    return pos[0] < left_bound or pos[0] > right_bound \
           or pos[1] < lower_bound or pos[1] > high_bound \
           or pos == end

  def remove_tile(tile, choices):
    for i in range(len(choices)):
      if tile[0] == choices[i][0] and tile[1] == choices[i][1]:
        return np.delete(choices, i, 0)
    return choices

  # Create a tile-by-tile path
  current_tile = start
  prev_tile = current_tile
  while True:
    x, y = current_tile
    choices = np.array([[x + 1,y],
                        [x - 1,y],
                        [x,y + 1],
                        [x,y - 1],
                        [x + 1,y + 1],
                        [x + 1,y - 1],
                        [x - 1, y + 1],
                        [x - 1, y - 1]])

    # Make sure to not travel back to previous tile
    choices = remove_tile(prev_tile, choices)

    # Randomly choose the next tile
    next_ind = random.randrange(len(choices))
    prev_tile = current_tile
    tile_wise_path.append(prev_tile)
    if is_end_path(prev_tile):
      break
    current_tile = (choices[next_ind][0],choices[next_ind][1])

  print("\nCHOSE THIS PATH: ", tile_wise_path)
  return tile_wise_path
