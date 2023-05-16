import json
import pygame
from queue import PriorityQueue
import pyautogui as auto
from buttons2 import *

pygame.init()
WIDTH = 800
WIN = pygame.display.set_mode((1400, WIDTH))
pygame.display.set_caption("MADY Robotics 🤖")
current_ends = 0



RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)




class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.colour =  BLACK
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.colour == RED

    def is_open(self):
        return self.colour == GREEN

    def is_barrier(self):
        return self.colour == WHITE

    def is_start(self):
        return self.colour == ORANGE

    def is_end(self):
        return self.colour == TURQUOISE
    
    def is_chargePoint(self):
        return self.colour == GREEN

    def reset(self):
        self.colour = BLACK

    #def make_closed(self):
    #    self.colour = RED
    #
    #def make_open(self):
    #    self.colour = GREEN

    def make_barrier(self):
        self.colour = WHITE

    def make_end(self):
        self.colour = TURQUOISE

    def make_path(self):
        self.colour = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row +1][self.col].is_barrier():  #DOWN
            self.neighbors.append(grid[self.row +1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():   # UP
            self.neighbors.append(grid[self.row -1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col+ 1].is_barrier():  #RIGHT
            self.neighbors.append(grid[self.row ][self.col+1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  #LEFT
            self.neighbors.append(grid[self.row][self.col - 1])
    
    def __lt__(self,other):
        return False

    def make_start(self):
        self.colour = ORANGE
        
    def make_chargePoint(self):
        self.colour = GREEN




def draw_text (text, font, text_col, x, y) :
    img = font.render (text, True, text_col)
    screen.blit (img, (x, y))

def buttons_def():
    b0 = Button((850, 30), "FindAll", 40, "black on white", command=pressO)
    b7 = Button((850, 100), "FindOne", 40, "black on white", command = pressSpace)
    b1 = Button((850, 170), "Manhatthan heuristic", 30, "white on red", command=pressM)
    b2 = Button((850, 240), "Mixed Heuristics", 30, "white on red", command=pressX)
    b3 = Button((850, 310), "Euclides Heuristic", 30, "white on red", command = pressE)
    b4 = Button((850, 380), "Chebyshev Heuristic", 30, "white on red", command = pressP)
    b5 = Button((850, 450), "Clear Grid", 30, "white on blue", command = pressC)
    b6 = Button((850, 520), "Reload map", 30, "white on blue", command = pressR)
    b9 = Button((850, 590), "BiggerMap", 30, "white on blue", command = pressB)
    b10 = Button((1100, 590), "SmallerMap", 30, "white on blue", command = pressK)
    b8 = Button((850, 660), "SaveMap", 30, "white on blue", command = pressS)
#find_paths_button = Button

def pressO():
    auto.press('o')
def pressQ():
    auto.press('q')
def pressP():
    auto.press('p')
def pressC():
    auto.press('c')
def pressX():
    auto.press('x')
def pressE():
    auto.press('e')
def pressS():
    auto.press('s')
def pressM():
    auto.press('m')
def pressSpace():
    auto.press(' ')
def pressR():
    auto.press('r')
def pressB():
    auto.press('b')
def pressK():
    auto.press('k')
    

        
def clear_grid(grid, ends, start, barriers):
    for row in grid:
        for spot in row:
            if spot not in ends and spot != start and spot not in barriers:
                spot.reset()
    return True


    


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()
        

import math

def heuristic_euclidean(node1, node2):
    dx = node1.col - node2.col
    dy = node1.row - node2.row
    h1 = int(math.sqrt(dx*dx + dy*dy))
    return  h1 # calcolo della radice quadrata della somma dei quadrati delle differenze


def heuristic_mix(node1, node2):
    x1, x2 = node1
    y1, y2 = node2
    dx1 = abs(x1 - y1)
    dy1 = abs(x2 - y2)
    h1 = dx1 + dy1 # distanza di Manhattan
    dx2 = abs(x1 - y1)
    dy2 = abs(x2 - y2)
    h2 = max(dx2, dy2) # distanza di Chebyshev
    dx3 = x1 - y1
    dy3 = x2 - y2
    h3 = int(math.sqrt(dx3*dx3 + dy3*dy3))
    return min(h1, h2, h3) # utilizzo della minima delle due euristiche

def heuristic_Manhattan(node1, node2):
    x1, x2 = node1
    y1, y2 = node2
    dx1 = abs(x1 - y1)
    dy1 = abs(x2 - y2)
    h1 = dx1 + dy1 # distanza di Manhattan
    return h1

def heuristic_Chebyshev(node1, node2):
    x1, x2 = node1
    y1, y2 = node2
    dx2 = abs(x1 - y1)
    dy2 = abs(x2 - y2)
    h2 = max(dx2, dy2) # distanza di Chebyshev
    return h2 # utilizzo della massima delle due euristiche


def algorithm(draw, grid, start, end, h):
    count = 0
    open_set = PriorityQueue()   # returns the smallest value in the list
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type ==pygame.QUIT:
                pygame.quit()
                
                
        current = open_set.get()[2]      # returns the best value
        open_set_hash.remove(current)
        
        if current == end:
            return came_from, g_score[end]

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    #neighbor.make_open()
        #draw()
        #if current != start and current not in ends and current not in shortest_paths :
        #    current.make_closed()

    return start, float("inf")

def save_to_file(grid, filename="temp.json"):
    barrier = list()
    ends = list()
    for x in grid:
        for spot in x:
            if spot.is_barrier():
                barrier.append((spot.row,spot.col))
    #for x in grid:
    #    for spot in x:
    #        if spot.is_end():
    #            ends.append((spot.row,spot.col))
    res = {"rows":len(grid),  "barrier":barrier} # "start": (start.row,start.col), "ends": (end.row,end.col) ADDTO HANDLE ENDS, BUT NEEDS MORE IMPLEMENTATION
    data = json.dumps(res,indent=4)
    with open(filename,"w") as data_file:
        data_file.write(data)


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid

def make_grid_from_file(filename, width):
    f = open(filename)

    data = json.load(f)

    rows = int(data['rows'])
    cols = int(data['rows'])
    grid = []
    gap = width // rows
    
    start = None
    ends = []
    
    barrier = {(ele[0],ele[1]) for ele in data['barrier']}
    end = {(ele[0],ele[1]) for ele in data['ends']}
    start = (data['start'][0],data['start'][1])
    
    
    for i in range(rows):
        grid.append([])
        for j in range(cols):
            spot = Spot(i, j, gap, rows)
            if (i,j) in barrier:
                spot.make_barrier()
            elif (i,j) == start:
                spot.make_start()
                start = spot
            elif (i,j) in end:
                spot.make_end()
                pos = [i,j]
                print("posizione end:" + str(i) + " " + str(j))
                row, col = get_clicked_pos_mod(j,i, rows, width)
                print("rows: " + str(row) + " cols: " + str(col))
                fine = grid[row][col]
                
                
                #
                #helper_end = spot
                ends.append(fine)
                
                
                #help_end = spots
            grid[i].append(spot)
     
    return grid,start, ends, rows, list(barrier) # NOT PASSEB BECAUSE METHOD JUST USES BARRIERS FOR INSTANCE
    
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap),(width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j* gap, 0), (j* gap,width))

def draw(win, grid, rows, width): 
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    
    
    draw_grid(win, rows, width) #disegna la griglia per i quadratini
    pygame.display.update()
    buttons.update()
    buttons.draw(screen)
    clock.tick(600)
    pygame.display.update()

def get_clicked_pos_mod(y,x, rows, width):
    gap = width //rows
    row = y//gap
    col = x//gap
    return row, col


def get_clicked_pos(pos, rows, width):
    gap = width //rows
    y,x = pos
    row = y//gap
    col = x//gap
    return row, col

def main(win, width, filename):
    
    def find_all_ends(win, grid, ROWS, width, PoC, heuristic, MAX_SOC_ABS, lowbattery, ends, SoC, start):
        
        control = 100

        while control == 100:
                    
                    
                    if SoC < lowbattery:
                                    
                        came_from, path_length=algorithm(lambda: draw(win, grid, ROWS, width), grid, start, PoC, heuristic) 
                        reconstruct_path(came_from, PoC, lambda: draw(win, grid, ROWS, width))
                        start = PoC
                        SoC = MAX_SOC_ABS
                        
                    else:
                            
                        for end in ends:        
                            for row in grid:
                                for spot in row:
                                    spot.update_neighbors(grid)
                            
                        
                        
                        
        
                        paths = []
                        shortest_paths = []
                        for end in ends:
                            came_from, path_length = algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end, heuristic)
                            if path_length != float("inf"):
                                print(SoC)
                                paths.append((came_from, end, path_length))
                        
                                
    
                        if paths:
                            shortest_path, nearest_end, _ = min(paths, key=lambda path_end_length: path_end_length[2])
                            shortest_paths.append(shortest_path)
                            for shortest_path in shortest_paths :
                                reconstruct_path(shortest_path, nearest_end, lambda: draw(win, grid, ROWS, width)) 
                            SoC = SoC - path_length
                            start = nearest_end
                            ends.remove(nearest_end)
                            nearest_end.make_start()
                            draw(win, grid, ROWS, width)
                        else:
                            print("No path found to any endpoint")
                            control = 1
        return start
    
    start = None
    ends = []
    barriers = []
    heuristic = heuristic_mix
    global current_ends
    PoC = None
    if filename is not None:
        grid, start, ends, ROWS,  barriers = make_grid_from_file(filename,width) # NOT PASSED BECAUSE JSON HASN'T
    else:
        ROWS = 100 #Be careful because sometimes row's number can be a problem of outOfBoundExeption
        grid = make_grid(ROWS, width)
        
    max_value = ROWS
    max_SoC = ROWS * 10
    MAX_SOC_ABS = 1000
    lowbattery = max_SoC / 5
    SoC = MAX_SOC_ABS
    run = True
    
    buttons_def()
    draw(win, grid, ROWS, width)
    while run:
        
        for event in pygame.event.get():
            
            
            
            if event.type == pygame.QUIT:
                run = False
            
            elif pygame.mouse.get_pressed()[0] : # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                print("rows: " + str(row) + " cols: " + str(col))
                if row < max_value and col < max_value:
                    spot = grid[row][col]
                    if not start and all(spot != end for end in ends):
                        start = spot
                        start.make_start()

                    elif spot not in ends and spot != start and spot not in barriers:
                        end = spot
                        end.make_end()
                        ends.append(end)
                        current_ends = current_ends +1 
                print(ROWS)
                draw(win, grid, ROWS, width)
                
            elif pygame.mouse.get_pressed()[2] : # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if row < max_value and col < max_value:
                    spot = grid[row][col]
                    if spot != start and all(spot != end for end in ends):
                        barrier = spot
                        barriers.append(spot)
                        barrier.make_barrier()
                draw(win, grid, ROWS, width)  
            
            if event.type == pygame.KEYDOWN:  #DELETE
                if event.key == pygame.K_z:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if row < max_value and col < max_value:
                        spot = grid[row][col]
                        if spot == start :
                            start = None
                            spot.reset()     
                        elif spot in ends:
                            ends.remove(spot)
                            spot.reset()
                            current_ends = current_ends - 1 
                        elif spot in barriers:
                             barriers.remove(spot)
                             spot.reset()
                        elif spot == PoC:
                            PoC = None
                            spot.reset()
                draw(win, grid, ROWS, width)
                
                if event.key == pygame.K_0:
                    if PoC == None:
                        pos = pygame.mouse.get_pos()
                        row, col = get_clicked_pos(pos, ROWS, width)
                        if row < max_value and col < max_value:
                            spot = grid[row][col]
                            if spot not in ends and spot != start and spot not in barriers:
                                PoC = spot
                                PoC.make_chargePoint()
                draw(win, grid, ROWS, width)   
                if event.key == pygame.K_SPACE and start and ends:
                        
                        
                    if SoC < lowbattery:
                                    
                        came_from, path_length=algorithm(lambda: draw(win, grid, ROWS, width), grid, start, PoC, heuristic) 
                        reconstruct_path(came_from, PoC, lambda: draw(win, grid, ROWS, width))
                        start = PoC
                        SoC = MAX_SOC_ABS
                        
                    else:
                            
                        for end in ends:        
                            for row in grid:
                                for spot in row:
                                    spot.update_neighbors(grid)
                            
                        
                        
                        
        
                        paths = []
                        shortest_paths = []
                        for end in ends:
                            came_from, path_length = algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end, heuristic)
                            if path_length != float("inf"):
                                print(SoC)
                                paths.append((came_from, end, path_length))
                        
                                
    
                        if paths:
                            shortest_path, nearest_end, _ = min(paths, key=lambda path_end_length: path_end_length[2])
                            shortest_paths.append(shortest_path)
                            for shortest_path in shortest_paths :
                                reconstruct_path(shortest_path, nearest_end, lambda: draw(win, grid, ROWS, width)) 
                            SoC = SoC - path_length
                            start = nearest_end
                            ends.remove(nearest_end)
                            nearest_end.make_start()
                            draw(win, grid, ROWS, width)
                        else:
                            print("No path found to any endpoint")
            
                if event.key == pygame.K_c: 
                    start = None
                    ends = []
                    PoC = None
                    grid = make_grid(ROWS, width)
                    draw(win, grid, ROWS, width)
                    
                if event.key == pygame.K_m:
                    heuristic = heuristic_Manhattan
                    draw(win, grid, ROWS, width)
                if event.key == pygame.K_p:
                    heuristic = heuristic_Chebyshev
                    draw(win, grid, ROWS, width)
                if event.key == pygame.K_x:
                    heuristic = heuristic_mix
                    draw(win, grid, ROWS, width)
                if event.key == pygame.K_e:
                    heuristic == heuristic_euclidean # type: ignore
                    draw(win, grid, ROWS, width)
                
                if event.key == pygame.K_r:
                    start = None
                    ends = []
                    PoC = None
                    grid, start, end, ROWS,  barriers = make_grid_from_file(filename, width)
                    draw(win, grid, ROWS, width)
                    

                if event.key == pygame.K_s:
                    grid = save_to_file(grid, filename="saved") #FOR INSTANCE, WE JUST SAVE BARRIERS ONLY FILES
                    start = None
                    ends = []
                    grid = make_grid(ROWS, width)
                
                if event.key == pygame.K_o:
                    start = find_all_ends(win, grid, ROWS, width, PoC, heuristic, MAX_SOC_ABS, lowbattery, ends, SoC, start)
                
                    
                if event.key == pygame.K_b:
                    nome = 'maps/stalla_100.json'
                    PoC = None
                    start = None
                    ends = []
                    print(ROWS)
                    main(WIN,WIDTH, nome)
                    print(ROWS)
                    draw(win, grid, ROWS, width)
                
                if event.key == pygame.K_k:
                    nome = 'maps/stalla1.json'
                    PoC = None
                    start = None
                    ends = []
                    print(ROWS)
                    main(WIN,WIDTH, nome)
                    print(ROWS)
                    draw(win, grid, ROWS, width)     
                    
        if run == False:
            pygame.quit()
            sys.exit()        
                            
    pygame.quit()
    
                    
                    
main(WIN, WIDTH, 'maps/stalla_ends.json')