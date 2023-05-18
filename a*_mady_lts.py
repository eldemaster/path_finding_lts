import json
import pygame
from queue import PriorityQueue
import pyautogui as auto
from buttons2 import *

pygame.init()
pygame.mixer.init()
WIDTH = 800
WIN = pygame.display.set_mode((1500, WIDTH), pygame.RESIZABLE)
pygame.display.set_caption("MADY Robotics 🤖")
font = pygame.font.SysFont("Arial", 40)
fonth = pygame.font.SysFont("Menlo", 35)


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


class Label:
    def __init__(self, text, x, y):
        self.x = x
        self.y = y
        self.set(text)

    def set(self, text):
        self.text = font.render(text, 1, pygame.Color("White"))
        size = w, h = self.text.get_size()
        self.rect = pygame.Rect(self.x, self.y, w, h)
        self.surface = pygame.Surface(size)
        self.surface.blit(self.text, (0, 0))

class SmallLabel:
    def __init__(self, text, x, y):
        self.x = x
        self.y = y
        self.set(text)

    def set(self, text):
        self.text = fonth.render(text, 1, pygame.Color("Black"), pygame.Color("white"))
        size = w, h = self.text.get_size()
        self.rect = pygame.Rect(self.x, self.y, w, h)
        self.surface = pygame.Surface(size)
        self.surface.blit(self.text, (0, 0))

lab1 = Label("", 850, 730)
labh = SmallLabel(" Mixed ", 900, 30)
labb = SmallLabel("Battery:",900, 100)

def buttons_def():
    findEnds = Button((850, 30), "FindAll", 40, "black on white", "white on green", command=pressO), 
    Button((850, 100), "FindOne", 40, "black on white", "white on green", command = pressSpace)
    heuristics = Button((850, 170), "Manhatthan heuristic", 30, "white on red", command=pressM),
    Button((850, 240), "Mixed Heuristics", 30, "white on red", command=pressX),
    Button((850, 310), "Euclides Heuristic", 30, "white on red", command = pressE), 
    Button((850, 380), "Chebyshev Heuristic", 30, "white on red", command = pressP)
    editMap = Button((850, 450), "Clear Grid", 30, "white on blue", command = pressC),
    Button((850, 520), "Reload map", 30, "white on blue", command = pressR),
    Button((850, 660), "SaveMap", 30, "white on blue", command = pressS),
    Button((1000, 450), "RemoveGrid", 30, "white on blue", command = pressW)
    smallerMaps = Button((850, 570), "SmallerMap", 20, "white on blue", command = pressK), 
    Button((1000, 570), "SmallerMapENDS", 20, "white on blue", command = pressD)
    biggerMaps = Button((1000, 610), "BiggerMapENDS", 20, "white on blue", command = pressB), 
    Button((850, 610), "BiggerMap", 20, "white on blue", command = pressG)
    
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
def pressG():
    auto.press('g')
def pressD():
    auto.press('d')
def pressW():
    auto.press('w')

        
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
    x1, x2 = node1
    y1, y2 = node2
    dx = x1-y1
    dy = x2-y2
    h1 = int(math.sqrt(dx*dx + dy*dy))
    return  h1 # calcolo della radice quadrata della somma dei quadrati delle differenze


def heuristic_mix(node1, node2):
    h1 = heuristic_Manhattan(node1, node2) # distanza di Manhattan
    h2 = heuristic_Chebyshev(node1, node2) # distanza di Chebyshev
    h3 = heuristic_euclidean(node1, node2)
    return min(h1, h2, h3) # utilizzo della minima delle tre euristiche

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
                    
    return start, float("inf")

def save_to_file(grid, start, PoC, filename="temp.json"):
    barrier = list()
    ends = list()
    for x in grid:
        for spot in x:
            if spot.is_barrier():
                barrier.append((spot.row,spot.col))
    for x in grid:
        for spot in x:
            if spot.is_end():
                ends.append((spot.row,spot.col))
    res = {"rows":len(grid),  "barrier":barrier, "start": (start.row,start.col), "ends": ends, "PoC":(PoC.row,PoC.col)}
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

    rows = data['rows']
    grid = []
    gap = width // rows
    
    start = None
    PoC = None
    
    if data['PoC'] != 'None':
        PoC = (data['PoC'][0],data['PoC'][1])
    
    barrier = {(ele[0],ele[1]) for ele in data['barrier']}
    
    if data['start'] != 'None':
        start = (data['start'][0],data['start'][1])
    if data['ends'] != 'None':
        ends2 = data['ends']
    
    ends = []
    
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            if (i,j) in barrier:
                spot.make_barrier()
            elif data['start'] != None and (i,j) == start:
                spot.make_start()
                start = spot
            elif data['PoC'] != None and (i,j) == PoC:
                spot.make_chargePoint()
                PoC = spot
            elif data['ends'] != 'None' and [i,j] in ends2:
                spot.make_end()
                ends.append(spot)
            grid[i].append(spot)

    return grid,start, ends, rows, list(barrier), PoC 
    
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap),(width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j* gap, 0), (j* gap,width))

def draw(win, grid, rows, width, grid_show):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    
    if grid_show:
        draw_grid(win, rows, width) #disegna la griglia per i quadratini
    WIN.blit(labb.surface, (1200, 100))
    WIN.blit(lab1.surface, (850, 730))
    WIN.blit(labh.surface, (1200, 30))
    buttons.update()
    buttons.draw(screen)
    clock.tick(1000)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width //rows
    y,x = pos
    row = y//gap
    col = x//gap
    
    return row, col


def main(win, width, filename):
    
    def find_ends(win, grid, ROWS, width, PoC, heuristic, max_SoC, ends, SoC, start, control):
        
        if control != 100:
            RunOnce = True
            Run = False
        elif control == 100:
            RunOnce = False
            Run = True
                    
        while   RunOnce or Run:
                      
                if  RunOnce or Run:   
                
                
                            
                        for end in ends:        
                            for row in grid:
                                for spot in row:
                                    spot.update_neighbors(grid)
                            
                        
                        
                        
        
                        paths = []
                        shortest_paths = []
                        for end in ends:
                            came_from, path_length = algorithm(lambda: draw(win, grid, ROWS, width, grid_show), grid, start, end, heuristic)
                            if path_length != float("inf"):
                                paths.append((came_from, end, path_length))
                                
                        
                                
    
                        if paths:
                            shortest_path, nearest_end, shortest_path_length = min(paths, key=lambda path_end_length: path_end_length[2])
                            next_path_to_PoC, path_to_PoC_length = algorithm(lambda: draw(win, grid, ROWS, width, grid_show), grid, nearest_end, PoC, heuristic)
                            
                            
                            if SoC < (path_to_PoC_length + shortest_path_length):
                                came_from, path_length=algorithm(lambda: draw(win, grid, ROWS, width, grid_show), grid, start, PoC, heuristic)
                                lab1.set("Recharging battery")
                                reconstruct_path(came_from, PoC, lambda: draw(win, grid, ROWS, width, grid_show))
                                start = PoC
                                SoC = max_SoC
                            else:    
                                shortest_paths.append(shortest_path)
                                for shortest_path in shortest_paths :
                                    reconstruct_path(shortest_path, nearest_end, lambda: draw(win, grid, ROWS, width, grid_show))   
                                lab1.set("Path length:" + str(int(shortest_path_length)))
                                
                                
                                
                                  
                                SoC = SoC - shortest_path_length
                                start = nearest_end
                                ends.remove(nearest_end)
                                nearest_end.make_start()
                            RunOnce = False
                            battery_perc = int((SoC/max_SoC)*100)
                            labb.set("Battery: " + str(battery_perc) + "%")
                            draw(win, grid, ROWS, width, grid_show)
                                
                        else:
                            lab1.set("No path found to any endpoint")
                            Run = False
                            RunOnce = False
        return start, SoC

    
    start = None
    grid_show=True
    ends = []
    barriers = []
    heuristic = heuristic_mix
    PoC = None
    if filename is not None:
        grid, start, ends, ROWS,  barriers, PoC= make_grid_from_file(filename,width) # NOT PASSED BECAUSE JSON HASN'T
    else:
        ROWS = 100 #Be careful because sometimes row's number can be a problem of outOfBoundExeption
        grid = make_grid(ROWS, width)
        
    max_value = ROWS
    max_SoC = int(ROWS * 10)
    
    SoC = max_SoC
    run = True
    
    buttons_def()
    draw(win, grid, ROWS, width, grid_show)
    while run:
        
        for event in pygame.event.get():
            
            
            if event.type == pygame.QUIT:
                run = False
            
            elif pygame.mouse.get_pressed()[0] : # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if row < max_value and col < max_value:
                    spot = grid[row][col]
                    if not start and all(spot != end for end in ends):
                        start = spot
                        start.make_start()
                        lab1.set("Start created")
                        

                    elif spot not in ends and spot != start and spot not in barriers:
                        end = spot
                        end.make_end()
                        ends.append(end)
                        lab1.set("End added")
                draw(win, grid, ROWS, width, grid_show)
                
            elif pygame.mouse.get_pressed()[2] : # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if row < max_value and col < max_value:
                    spot = grid[row][col]
                    if spot != start and all(spot != end for end in ends):
                        barrier = spot
                        barriers.append(spot)
                        barrier.make_barrier()
                        lab1.set("Barrier created")
                draw(win, grid, ROWS, width, grid_show)  
            
            if event.type == pygame.KEYDOWN:  #DELETE
                if event.key == pygame.K_z:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if row < max_value and col < max_value:
                        spot = grid[row][col]
                        if spot == start :
                            start = None
                            spot.reset()   
                            lab1.set("Start removed")  
                        elif spot in ends:
                            ends.remove(spot)
                            spot.reset()
                            lab1.set("End removed")  
                        elif spot in barriers:
                             barriers.remove(spot)
                             spot.reset()
                             lab1.set("Barrier removed")  
                        elif spot == PoC:
                            PoC = None
                            spot.reset()
                            lab1.set("Point of Charge removed")  
                draw(win, grid, ROWS, width, grid_show)
                
                if event.key == pygame.K_0:
                    if PoC == None:
                        pos = pygame.mouse.get_pos()
                        row, col = get_clicked_pos(pos, ROWS, width)
                        if row < max_value and col < max_value:
                            spot = grid[row][col]
                            if spot not in ends and spot != start and spot not in barriers:
                                PoC = spot
                                PoC.make_chargePoint()
                                lab1.set("Point of Charge added")  
                draw(win, grid, ROWS, width, grid_show)   
                if event.key == pygame.K_SPACE and start and ends:
                           
                    start, SoC = find_ends(win, grid, ROWS, width, PoC, heuristic, max_SoC, ends, SoC, start, 1)
            
                if event.key == pygame.K_o:
                    
                    start, SoC = find_ends(win, grid, ROWS, width, PoC, heuristic, max_SoC, ends, SoC, start, 100)
                
                if event.key == pygame.K_c: 
                    start = None
                    ends = []
                    PoC = None
                    grid = make_grid(ROWS, width)
                draw(win, grid, ROWS, width, grid_show)
                    
                if event.key == pygame.K_m:
                    heuristic = heuristic_Manhattan
                    labh.set(" Manhattan ")  
                draw(win, grid, ROWS, width, grid_show)
                if event.key == pygame.K_p:
                    heuristic = heuristic_Chebyshev
                    labh.set(" Chebyshev ")
                draw(win, grid, ROWS, width, grid_show)
                if event.key == pygame.K_x:
                    heuristic = heuristic_mix
                    labh.set(" Mixed ")
                draw(win, grid, ROWS, width, grid_show)
                if event.key == pygame.K_e:
                    heuristic == heuristic_euclidean # type: ignore
                    labh.set(" Euclidean ")
                draw(win, grid, ROWS, width, grid_show)
                
                if event.key == pygame.K_r:
                    start = None
                    ends = []
                    PoC = None
                    grid, start, end, ROWS,  barriers , PoC = make_grid_from_file(filename, width)
                    lab1.set("Grid reset")  
                draw(win, grid, ROWS, width, grid_show)
                    

                if event.key == pygame.K_s:
                    grid = save_to_file(grid, start, PoC , filename="saved") #FOR INSTANCE, WE JUST SAVE BARRIERS ONLY FILES
                    lab1.set("Grid saved")  
                    start = None
                    ends = []
                    grid = make_grid(ROWS, width)
                
                    
                if event.key == pygame.K_g:
                    nome = 'maps/stalla_100.json'
                    main(WIN,WIDTH, nome)
                    draw(win, grid, ROWS, width, grid_show)
                
                if event.key == pygame.K_k:
                    nome = 'maps/stalla_50.json'
                    main(WIN,WIDTH, nome)
                    draw(win, grid, ROWS, width, grid_show)   
                
                if event.key == pygame.K_b:
                    nome = 'maps/stalla_100_ends.json'
                    main(WIN,WIDTH, nome)
                    draw(win, grid, ROWS, width, grid_show)   
                
                if event.key == pygame.K_d:
                    nome = 'maps/stalla_50_ends.json'
                    main(WIN,WIDTH, nome)
                    draw(win, grid, ROWS, width, grid_show)   
                    
                if event.key == pygame.K_w:
                    if grid_show:
                        grid_show = False
                    else: grid_show = True 
                    draw(win, grid, ROWS, width, grid_show)   
                    
                 
                    
        if run == False:
            pygame.quit()
            sys.exit()        
                            
    pygame.quit()
    

                    
                    
main(WIN, WIDTH, 'maps/labirinto_fixed.json')