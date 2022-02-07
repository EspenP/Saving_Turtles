#!/usr/bin/python3

# This is the basic game file. When done, this will be packed into a function
# that returns the end of game statistics, which will then be plotted and displayed to the user.

import pygame, sys
import random
import numpy as np
from PIL import Image
from ypstruct import structure

# Other files
import game_utils as gu
from turtle_class import turtle
from bridge_class import bridge


class game:
    pygame.init()

    """ DEFINE TILES """
    tilesize = 60
    W = 0  # WATER
    G = 1  # GRASS
    R = 2  # ROAD
    F = 3  # FOREST
    M = 4  # MUD
    X = 5  # CLIFF/FENCE - IMPASSABLE AREA

    # Defining tiles that should autopopulate in the map
    Tiles = (G, F, M)

    """DEFINE TILE COLORS/TEXTURES"""
    img_path = "assets/"
    WATER = gu.image_to_tile(img_path + "water.png", tilesize)
    GRASS = gu.image_to_tile(img_path + "grass.png", tilesize)
    ROAD = gu.image_to_tile(img_path + "road.png", tilesize)
    FOREST = gu.image_to_tile(img_path + "forest.png", tilesize)
    MUD = gu.image_to_tile(img_path + "mud.png", tilesize)
    IMPASSE = gu.image_to_tile(img_path + "cliff.png", tilesize)

    """ OTHER TEXTURES AND THINGS """
    REDX = None

    """LINK TILES AND TEXTURES/COLORS"""
    TileTexture = {W: WATER,
                   G: GRASS,
                   R: ROAD,
                   F: FOREST,
                   M: MUD,
                   X: IMPASSE}

    """DEFINE MAP"""
    # map1 = np.array([[F, G, F, G, G, G, G, G, R, R, G, G, G, G, G, G, W],
    #                [G, G, G, G, G, G, G, G, R, R, G, G, G, G, G, G, W],
    #                [G, G, F, G, G, G, G, G, R, R, G, G, G, G, G, G, W],
    #                [G, G, F, M, M, G, G, G, R, R, G, G, X, G, G, G, W],
    #                [G, G, F, M, M, G, G, G, R, R, G, G, G, G, G, G, W],
    #                [G, G, F, M, M, G, G, G, R, R, G, G, G, G, G, G, W],
    #                [G, M, F, G, G, X, G, G, R, R, G, G, X, G, G, G, W],
    #                [G, G, F, G, G, X, G, G, R, R, G, G, G, G, G, G, W],
    #                [G, G, F, M, G, G, G, G, R, R, G, G, G, G, G, G, W],
    #                [G, G, F, M, G, G, G, G, R, R, G, G, F, F, G, G, W],
    #                [G, G, G, G, G, G, G, G, R, R, G, G, G, G, G, G, W],
    #                [G, G, G, G, G, G, G, G, R, R, G, G, G, G, G, G, W]])

    map1 = np.array([random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17),
                     random.choices(Tiles, k=17)])

    # Creating the road and left water edge in the randomized map
    for i in range(12):
        map1[i, 8] = R
        map1[i, 9] = R
        map1[i, 16] = W

    """ DEFINE TILE SPEEDS """
    # Will multiply the movement by these numbers
    TileSpeed = {W: 4,
                 G: 3,
                 R: 3,
                 F: 1,
                 M: 2,
                 X: 1}

    """ GAME VARIABLES """
    # Map
    width = len(map1[0])
    height = len(map1)
    # print("MAP1 is {} long and {} high".format(width, height))
    start = (tilesize // 2, (height * tilesize) // 2 - tilesize // 2)
    end = (width * tilesize, (height * tilesize) // 2)
    game_active = True
    wall_list = []
    redx_list = []
    check_list = []
    water_list = []

    # Car
    road_edge_left = 8
    road_edge_right = 10
    car_spawn_top = road_edge_left * tilesize + (tilesize // 2)
    car_spawn_bot = road_edge_right * tilesize - (tilesize // 2)
    car_speed = 5
    car_picture = img_path + "car3.png"
    # print("THESE", road_edge_left, road_edge_right)

    # Bridge
    bridge_params = structure()
    bridge_params.top = height - 1
    bridge_params.bot = 0
    bridge_params.left = 8
    bridge_params.tilesize = tilesize
    brg = bridge(bridge_params)

    """ GAME OBJECTS """
    turtle_list = []
    retired_turtles = []  # Put turtles here once they are dead or stuck
    car_list = []
    clock = pygame.time.Clock()

    """ EVENTS """
    SPAWNCAR = pygame.USEREVENT
    pygame.time.set_timer(SPAWNCAR, 2000)  # Will probably make this a lot slower in the actual game

    """ HELPER FUNCTIONS """

    def init_turtles(self, params):
        num_turtles = params.npop
        turt_params = structure()
        turt_params.tilesize = self.tilesize
        turt_params.start = self.start
        for n in range(num_turtles):
            turt_params.path = self.create_random_path()
            turt_params.gene = gu.coords_to_cardinal(turt_params.path)
            t_obj = turtle(turt_params)
            self.turtle_list.append(t_obj)

    def init_children(self, gene_list, params):
        num_turtles = params.npop
        turt_params = structure()
        turt_params.tilesize = self.tilesize
        turt_params.start = self.start
        for gene in gene_list:
          turt_params.gene = gene
          turt_params.path = gu.card_to_coords(self.start, gene)
          t_obj = turtle(turt_params)
          self.turtle_list.append(t_obj)

    def calc_cost(self, turtle):
        cost = 1000

        # for coord in positioning:
        #     if coord[0] > x_pos_old:
        #         reward += 10
        #     elif coord[0] == x_pos_old:
        #         reward += 2
        #     elif coord[0] < x_pos_old:
        #         reward -= 5

        #     x_pos_old = coord[0]

        # Simpler to do it this way? With pixels instead of tiles
        cost -= 0.5*turtle.rect.centerx
        cost += 0.3*turtle.effort

        if turtle.bridge:
            cost -= 300
        if turtle.dead:
            cost += 600
        if turtle.stopped:
            cost += 200
        if turtle.safe:
            cost -= 1000
        return cost

    # Assumes a road of width 2 that vertically bisects the map in a straight line
    def spawn_car(self):
        top = random.randrange(2)  # Random chance that car starts at bottom or top
        spawnpoint = (None, None)
        car = structure()
        car.surf = gu.load_tilesz(self.car_picture, self.tilesize)
        if top == 1:
            spawnpoint = (self.car_spawn_top, 0)
            car.direction = 1
            car.surf = pygame.transform.rotozoom(car.surf, 90, 1)
        else:
            spawnpoint = (self.car_spawn_bot, self.height * self.tilesize)
            car.direction = -1
            car.surf = pygame.transform.rotozoom(car.surf, -90, 1)

        car.rect = car.surf.get_rect(center=spawnpoint)
        self.car_list.append(car)

    def move_cars(self):
        for car in self.car_list:
            # Check if car is out of map
            if car.direction == -1 and car.rect.centery < 0:
                self.car_list.remove(car)
                continue
            elif car.direction == 1 and car.rect.centery > (self.height * self.tilesize):
                self.car_list.remove(car)
                continue
            car.rect.centery += self.car_speed * car.direction
            self.screen.blit(car.surf, car.rect)

    def get_tile_speed(self, turtle):
        pos = (turtle.rect.centerx, turtle.rect.centery)
        x, y = self.which_tile(pos)
        y = self.height - y
        if x > self.width or y > self.height:
          turtle.stop()
          return 0
        tile_type = self.map1[y-1,x-1]
        # print("On tile {} {} which is a tile of type {}".format(x,y,tile_type))
        return self.TileSpeed[tile_type]

    def create_random_path(self):
        tile_size = self.tilesize
        lower_bound = 0 - 1  # Remember this is the top of the screen in pygame
        high_bound = self.height + 1  # And this is the bottom
        left_bound = 0 - 1
        right_bound = self.width + 1
        game_map = self.map1
        start = self.which_tile(self.start)
        end = self.which_tile(self.end)
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
            choices = np.array([[x + 1, y],
                                [x - 1, y],
                                [x, y + 1],
                                [x, y - 1],
                                [x + 1, y + 1],
                                [x + 1, y - 1],
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
            current_tile = (choices[next_ind][0], choices[next_ind][1])

        #print("\nCHOSE THIS PATH: ", tile_wise_path)
        return tile_wise_path

    def which_tile(self, pos):
        x = pos[0]
        y = pos[1]
        x_ind = x // self.tilesize
        y_ind = (self.height - 1) - (y // self.tilesize)
        return (x_ind, y_ind)

    def move_turtles(self):
        for turtle in self.turtle_list:
            path_ind = turtle.iteration
            tilesize = self.tilesize
            posx = turtle.rect.centerx  # Pixel
            posy = turtle.rect.centery
            current_tile = self.which_tile((posx, posy))

            # Check if turtle has reached goal
            if path_ind >= len(turtle.path) - 1:
                self.screen.blit(turtle.surf, turtle.rect)
                continue
            if turtle.path[path_ind] == current_tile:
                path_ind += 1
                turtle.iteration = path_ind
            elif turtle.path[path_ind] == current_tile and path_ind >= len(turtle.path):
                turtle.stop()
                continue
            # print("\nGoing to ", turtle.path[path_ind])
            diffx = turtle.path[path_ind][0] - current_tile[0]
            diffy = turtle.path[path_ind][1] - current_tile[1]
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
            speed = self.get_tile_speed(turtle)
            turtle.rect.centerx += speed * movex
            turtle.rect.centery += speed * movey
            turtle.animate(movex, movey)
            # print("\nMoved to ", which_tile((turtle.rect.centerx,turtle.rect.centery),game))
            turtle.effort += 1
            self.screen.blit(turtle.surf, turtle.rect)

    def pop_special_tiles_lists(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.map1[row][col] == self.X:
                    surface = self.TileTexture[self.map1[row][col]]
                    rect = surface.get_rect(topleft=(col * self.tilesize, row * self.tilesize))
                    self.wall_list.append(rect)
                elif self.map1[row][col] == self.W:
                    surface = self.TileTexture[self.map1[row][col]]
                    rect = surface.get_rect(topleft=(col * self.tilesize, row * self.tilesize))
                    self.water_list.append(rect)

    # Call this function when a turtle dies or is stopped.
    # This does several things
    # Puts the stopped turtles in a retired list
    # Adds a red x to represent each turtle.
    def filter_out_turtles(self):
        res_list = []
        for turtle in self.turtle_list:
            pos = (turtle.rect.centerx, turtle.rect.centery)
            if turtle.stopped:
                # Get a red X
                redx = structure()
                redx.surf = self.REDX
                redx.rect = redx.surf.get_rect(center=pos)
                self.redx_list.append(redx)
                # Calculate the cost of the turtle
                turtle.cost = self.calc_cost(turtle)
                # Add to retired turtles list
                self.retired_turtles.append(turtle)
            elif turtle.safe:
                check = structure()
                check.surf = self.CHECK
                check.rect = check.surf.get_rect(center=pos)
                self.check_list.append(check)
                turtle.cost = self.calc_cost(turtle)
                self.retired_turtles.append(turtle)
            else:
                res_list.append(turtle)
        self.turtle_list = res_list

    def display_markers(self):
        for x in self.redx_list:
            self.screen.blit(x.surf, x.rect)
        for x in self.check_list:
            self.screen.blit(x.surf, x.rect)


    def in_map(self, turtle):
        high = self.height * self.tilesize
        right = self.width * self.tilesize
        low = 0
        left = 0
        posx = turtle.rect.centerx
        posy = turtle.rect.centery
        if posx > right or posx < left:
            return False
        elif posy > high or posy < low:
            return False
        else:
            return True

    def check_collision(self):
        # Check for wall and car collisions
        for turtle in self.turtle_list:
            if not self.in_map(turtle):
                turtle.stop()
            for wall in self.wall_list:
                if turtle.rect.colliderect(wall):
                    # print("HIT WALL")
                    turtle.stop()
            for water in self.water_list:
                if turtle.rect.colliderect(water):
                    turtle.save()
            for car in self.car_list:
                if turtle.rect.colliderect(car):
                    if turtle.rect.colliderect(self.brg.rect):
                        turtle.bridge = True
                        continue
                    # print("HIT CAR")
                    turtle.kill()

    def display_bridge(self):
        self.screen.blit(self.brg.surf, self.brg.rect)

    """MAIN GAME FUNCTIONS"""

    def init_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.tilesize, self.height * self.tilesize))
        self.REDX = gu.load_half_tilesz(self.img_path + "redx.png", self.tilesize)
        self.CHECK = gu.load_half_tilesz(self.img_path + "check.png", self.tilesize)
        self.pop_special_tiles_lists()
        self.brg.load_pic(self.img_path + "bridge.jpeg", self.tilesize)

    def set_turtle_list(self, turtles):
        self.turtle_list = turtles

    def reset_turtles(self):
      for turtle in self.turtle_list:
        turtle.reset()
        turtle.rect.center = self.start

    def run_game(self):
        def display_map():
            """ DRAW MAP TO SCREEN """
            for row in range(self.height):
                for col in range(self.width):
                    surface = self.TileTexture[self.map1[row][col]]
                    rect = surface.get_rect(topleft=(col * self.tilesize, row * self.tilesize))
                    self.screen.blit(surface, rect)

        """ MAIN LOOP """
        while True:
            if not self.turtle_list: # This ends the round
                return
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == self.SPAWNCAR:
                    self.spawn_car()
            display_map()
            if self.turtle_list:
                self.move_turtles()
            if self.car_list:
                self.move_cars()
            self.check_collision()
            self.filter_out_turtles()
            if self.redx_list:
                self.display_markers()
            self.display_bridge()
            pygame.display.update()
            self.clock.tick(120)

    def reset(self):
        self.redx_list.clear()
        self.car_list.clear()
        self.check_list.clear()
        for turtle in self.turtle_list:
          turtle.reset()
          turtle.rect.center = self.start
