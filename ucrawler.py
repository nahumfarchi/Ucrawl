#Ucrawler is a turn-based dungeon crawler in which the maze is generated by crawling a seed web
#page. The maze's structure is built from the graph returned by crawl_web().
#
#To win, you must reach the page with the highest page rank and kill all the crawlers (little c's).
#Also, the size and the amount of crawlers in each room is dependent on it's page rank.
#
#Use 'wsad' to move and the spacebar to shoot. (Hint: you can do more than one action per turn.
#(ie 'ss d' will move twice down, shoot and then move right once)"
#
#For best results run this from the command line, as it doesn't work as well from the python gui.
#
#Created by Nahum Farchi, 2012
#
#This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative Commons, 444 Castro Street, Suite 900, Mountain View, #California, 94041, USA.

#from sys import stdout
import os
import random
from time import sleep
from search_engine import get_page, get_next_target, get_all_links, union, add_page_to_index, add_to_index, crawl_web, lookup, compute_ranks

###################################################################################################
################################## Game code ######################################################
###################################################################################################

#clear = lambda: os.system('cls')
def clear():
    for i in xrange(1,25):
        print

def add_vectors(v, u):
    """
    Adds the two vectors, v and u.
    """
    return (v[0] + u[0], v[1] + u[1])

def room_xy(room, x, y, value=None):
    """
    Returns the (x,y) tile of room.
    """
    return room[x][y]

def room_wh(room):
    """
    Returns the width and height of room.
    """
    if isinstance(room, str):
        room = dungeon[room]
    return len(room), len(room[0])

def room_center(dungeon, room_name):
    room = dungeon[room_name]
    w, h = room_wh(room)
    x, y = int(w/2), int(h/2)
    tile = room[x][y]
    while tile != ' ':
        x = x + 1
        y = y + 1
        tile = room[x][y]
    return (x, y)

def create_room(w, h):
    """
    Creates a new room. The rooms is a list of lists, where every list represents a column. Tiles
    can be got like so: room[x][y].
    """
    # map[0] gives a list which represents the row, or the x. Then map[x][y]
    # gives the yth place in the column x.
    room = [[' ' for j in range(h)] for i in range(w)]
    for x in range(w):
        for y in range(h):
            if y == 0 or y == (h-1):
                room[x][y] = '-'
            elif x == 0 or x == (w-1):
                room[x][y] = '|'
    return room

def clear_room(dungeon, room_name):
    room = dungeon[room_name]
    w, h = room_wh(room)
    for x in range(0,w):
        for y in range(0,h):
            if (x and y != 0) and x != (w-1) and y != (h-1):
                room[x][y] = ' '

def add_door(room, v):
    pass

def get_room_name(dungeon, room):
    """
    Finds the name of a given room. If the room doesn't exist returns None.
    """
    for n in dungeon:
        if dungeon[n] == room:
            return n
    return None

def print_room(dungeon, room):
    """
    Prints out the room. This is the basic graphics function.
    Clear(), stdout.flush() arn't entirely clear to me.
    """
    if not isinstance(room, str):
        name = get_room_name(dungeon, room)
    else:
        name = room
        room = dungeon[name]
    w, h = room_wh(room)
    room_str = ''
    for y in range(h):
        row = ''
        for x in range(w):
            #print room
            tile = room[x][y]
            if isinstance(tile, list):
                row = row + room[x][y][0]
            else:
                row = row + room[x][y]
        #print row
        room_str = room_str + '\n' + row
    room_str = room_str + '\n\n'
    #clear()
    #print "Room: ", name
    #print "Hp: ", player['hp']
    #print room
    #stdout.write("Room: %s" % name)
    #stdout.write("%s" % room_str)
    #stdout.flush()
    print room_str

def create_dungeon(graph, ranks):
    """
    Creates a new dungeon out of the graph rooms. The size of each room depends on it's rank.
    """
    dungeon = {}
    w, h = 150, 100
    for r in graph:
        name, w, h = r, int(w*ranks[r]+10), int(h*ranks[r]+10)
        dungeon[name] = create_room(w, h)
    return dungeon
    
def print_dungeon(dungeon):
    """
    Prints out the whole dungeon... Kind of useless cause I couldn't get it to build all the rooms
    as a single dungeon with hallways and all.
    """
    for r in dungeon:
        print_room(dungeon[r])

def create_crit(dungeon, room, pos, symbol, type, hp=1, dir=None, score=None):
    """
    The basic crit. Its type can be 'player' or 'crawler'.
    """
    crit = {'dungeon': dungeon,
              'room': dungeon[room],
              'room_name': room,
              'symbol': symbol,
              'pos': (pos[0], pos[1]),
              'lastpos': (pos[0], pos[1]),
              'hp': hp,
              'type': type,
              'dir': dir,
              'score': score}
    return crit

def create_crit_p(p, dungeon, room, pos, symbol, type, hp=1, dir=None, score=None):
    #print "in create_crit_p"
    if random.random() <= p:
        "creating crit..."
        return create_crit(dungeon, room, pos, symbol, type, hp, dir, score)
    else:
        return None

"""def create_crits(n, dungeon, room, positions, symbol, type, hp=1, dir=None):
    crits = []
    w, h = room_wh(room)
    for i in xrange(n):
        if positions[i] == 'rand':
            x = random.randint(0, w-1)
            y = random.randint(0, h-1)
            pos = (x, y)
        else:
            pos = positions[i]
        crits.append(create_crit(dungeon, room, pos, symbol, type, hp, dir))
    return crits"""

def create_crits_p(p_dict, n, dungeon, room_name, positions, symbol, type, hp=1, dir=None):
    crits = []
    w, h = room_wh(dungeon[room_name])
    p = p_dict[room_name]*2
    print "p =", p
    for i in xrange(n):
        if positions[i] == 'rand':
            pos = (random.randint(0, w-1), random.randint(0, h-1))
        else:
            pos = positions[i]
        c = create_crit_p(p, dungeon, room_name, pos, symbol, type, hp, dir)
        if c:    
            crits.append(c)
    return crits

def count_crits(crits, room_name):
    result = 0
    if room_name in crits:
        for c in crits[room_name]:
            if c['type'] == 'crawler':
                result = result + 1
    return result

def create_door(dungeon, room, pos, symbol, destination):
    """
    Create a new door. A door is a list with a symbol and a destination room. It is saved in the
    room's list and no where else.
    """
    dungeon[room][pos[0]][pos[1]] = [symbol, destination]

def create_doors(dungeon, symbol, graph):
    for room in graph:
        i = 1
        for destination in graph[room]:
            create_door(dungeon, room, (0,i), symbol, destination)
            i = i + 1

def create_doors_p(dungeon, room_name, symbol, graph, positions, p=0.8):
    n = len(graph[room_name])
    used = []
    len_positions = len(positions)
    for destination in graph[room_name]:
        created = False
        j = 0
        while not created:
            if destination not in graph:
                break
            #print "j =", j
            pos = positions[j]
            if random.random() <= p and pos not in used:
                create_door(dungeon, room_name, pos, symbol, destination)
                used.append(pos)
                created = True
            j = j + 1
            if len(used) == len_positions:
                break
            elif j >= len(positions):
                j = 0
    
def blit(obj):
    """
    Blits the obj unto the room it is in. An obj is a dictionary with all the relevent keys.
    """
    # An object is a dictionary with the keys: 'dungeon', 'room', 'symbol', 'pos', 'lastpos'
    x = obj['pos'][0]
    y = obj['pos'][1]
    lastx= obj['lastpos'][0]
    lasty = obj['lastpos'][1]
    room = obj['room']
    if x < len(room) and y < len(room[0]):
        room[lastx][lasty] = ' '
        room[x][y] = obj['symbol']

def find_door(dungeon, room, destination):
    pass

def collision_detection(obj1, obj2):
    if obj1['pos'] == obj2['pos']:
        return True
    return False

def collision_detection_crits(player, crits):
    if player['room_name'] in crits:
        crits_list = crits[player['room_name']]
    else:
        crits_list = []
    n = len(crits_list)
    tokill = []
    for i in range(n):
        for j in range(i+1, n):
            criti, critj = crits_list[i], crits_list[j]
            
            if collision_detection(criti, critj):
                if criti['type'] == 'bullet' or critj['type'] == 'bullet':
                    tokill.append(criti)
                    tokill.append(critj)
                else:
                    crits_list[i]['pos'] = crits_list[i]['lastpos']
                    crits_list[j]['pos'] = crits_list[j]['lastpos']
    if tokill != []:
        print "Hit!"
        sleep(0.4)
    for c in tokill:
        if c['type'] == 'crawler':
            c['hp'] = c['hp'] - 1
            if c['hp'] < 1:
                player['score'] = player['score'] + 100*ranks[player['room_name']]
                kill_crit(c, crits)
        elif c['type'] == 'bullet':          
            kill_crit(c, crits)

#def collision_detection_bu

def move(dungeon, obj, v, crits):
    """
    Moves obj according to the vector v.
    """
    # An object is a dictionary with the keys: 'dungeon', 'room', 'symbol', 'pos', 'lastpos'
    if v == None:
        return
    room = obj['room']
    newpos = add_vectors(obj['pos'], v)
    tile = room[newpos[0]][newpos[1]]
    if obj['type'] == 'bullet' and (tile == '-' or tile == '|' or isinstance(tile, list)):
        kill_crit(obj, crits)                        
    elif tile == ' ':
        obj['lastpos'] = obj['pos']
        obj['pos'] = newpos
    elif obj['type'] == 'bullet' and tile != '-' and tile != '|' and tile != '@':
        obj['lastpos'] = obj['pos']
        obj['pos'] = newpos
    elif tile == 'c':
        if obj['type'] == 'player':
            obj['hp'] = obj['hp'] - 1
            print "You were hit!"
            sleep(1)
    elif tile == 'U' and obj['type'] == 'crawler':
        player['hp'] = player['hp'] - 1
        print "You were hit!"
        sleep(0.5)
    elif isinstance(tile, list):
        if tile[0] == '@' and obj['type'] == 'player':
            obj['room_name'] = tile[1]
            obj['room'] = dungeon[tile[1]]
            startingpos = room_center(dungeon, obj['room_name'])
            obj['pos'], obj['lastpos'] = startingpos, startingpos

def blit_crits(crits, room):
    if room in crits:
        for c in crits[room]:
            blit(c)

def crit_action(crit, action, crits):
    if crit['type'] == 'player':
        #i = 0
        #print "action = ", action
        for s in action:          
            if s == ' ':
                v, direction = cal_dir(crit['dir'])
                pos = crit['pos']
                return create_crit(dungeon, crit['room_name'], pos, '*', 'bullet', 1, crit['dir'])
            if s == 'x':
                break
            elif s != None:
                #print "s =", s
                v, direction = cal_dir(s)
                crit['dir'] = direction
                move(dungeon, crit, v, crits)
    elif crit['type'] == 'crawler':
        v, direction = cal_dir(action)
        move(dungeon, crit, v, crits)
    elif crit['type'] == 'bullet':
        v, direction = cal_dir(crit['dir'])
        move(dungeon, crit, v, crits)
        
    return None    

def cal_dir(direction):
    if direction == 'left' or direction == 'a':
        return (-1,0), 'left'
    elif direction == 'right' or direction == 'd':
        return (1,0), 'right'
    elif direction == 'down' or direction == 's':
        return (0,1), 'down'
    elif direction == 'up' or direction == 'w':
        return (0,-1), 'up'

def crit_ai(crit):
    """
    Returns an action for the crit to follow.
    """
    if crit['type'] == 'crawler':
        # Crawlers move at random.
        return random.choice(['left','right','up','down'])
    #if crit['type'] == 'bullet':
    #    return crit['dir']
    return None

def kill_crit(crit, crits):
    crits_list = crits[crit['room_name']]
    x, y = crit['pos'][0], crit['pos'][1]
    crit['room'][x][y] = ' '
    crits_list.remove(crit)

def graphics(clear, player, ranks, toclear=True):
    player_room = player['room']
    player_room_name = player['room_name']
    if toclear:
        clear()
    print "Room: ", player_room_name
    print "Score: ", player['score']
    print "HP: ", player['hp']
    print "Difficulty: ", ranks[player_room_name]
    print "Crawlers: ", count_crits(crits, player_room_name) #len(crits[player_room_name])
    print_room(dungeon, player_room)
    #print "Hp: ", player['hp']
    print "What do you do? ('wsad' to move, spacebar to shoot, x to exit)"
    print "=>",

def create_row(start, end, y):
    return [(i,y) for i in range(start,end)]

def create_column(start, end, x):
    return [(x,i) for i in range(start,end)]

def largest(dict):
    return max(v for k,v in dict.iteritems())

# Intro
print "Ucrawler is a turn-based dungeon crawler in which the maze is generated by crawling a seed web page.\n"
print "The difficulty of each page is according to it's page rank.\n"
print "Use 'wsad' to move and the spacebar to shoot. (Hint: you can do more than one action each turn. ie 'ss d' will move twice down, shoot and then move right once)\n"
#print "To win, you must reach ", toughest_room, "and kill all the crawlers (the little c's).\n" 
print "Please enter a seed page (press enter to use default)"
print "=>",
seed_page = raw_input()
if seed_page == '' or seed_page == None:
    seed_page = 'http://udacity.com/cs101x/urank/index.html'

# Initilize game world
random.seed()
#print "Please enter a seed page"
#seed_page = intro()
#seed_page = 'http://udacity.com/cs101x/urank/zinc.html'
print "seed_page =", seed_page
#seed_page = 'http://ninjasandrobots.com/pricing-in-reverse'
index, graph = crawl_web(seed_page, 10)
ranks = compute_ranks(graph)

player_room_name = seed_page
#player_room_name = 'http://udacity.com/cs101x/urank/zinc.html'
#player_room_name = 'http://udacity.com/cs101x/urank/kathleen.html'
#player_room_name = 'http://udacity.com/cs101x/urank/arsenic.html'
print "Generating dungeon...\n"
dungeon = create_dungeon(graph, ranks)
center = room_center(dungeon, player_room_name)
player = create_crit(dungeon, player_room_name, center, 'U', 'player', 3, 'up', 0)
toughest_room = [k for k, v in ranks.iteritems() if v == max(v for k, v in ranks.iteritems())][0]
print "To win, you must reach ", toughest_room, "and kill all the crawlers (little c's).\n"
print "Press enter to start..."
raw_input()
#intro(toughest_room)

crits = {}
for room_name in dungeon:
    #print "room_name =", room_name
    #n = int(ranks[room_name] * 50)
    w, h = room_wh(room_name)
    #print "w =", w
    #sleep(1)
    #print "room_name =", room_name
    #n = 6
    #positions = [(i,1) for i in range(1,n+1)] + [(i,h-2) for i in range(1,n+1)]
    #print "positions =", positions
    crit_positions = create_row(1, w-1, 1) + create_row(1, w-1, 2) + create_row(1, w-1, h-2) + create_row(1, w-1, h-3)
    n = len(crit_positions)
    #crits[room_name] = create_crits_p(ranks, n, dungeon, room_name, crit_positions, 'c', 'crawler')
    crits[room_name] = create_crits_p(ranks, n, dungeon, room_name, crit_positions, 'c', 'crawler')

    door_positions = create_row(1, w-1, 0) + create_row(1, w-1, h-1) #+ create_column(1, h-1, 0) + create_column(1, h-1, w-1)
    #print "doors: ", len(graph[room_name])
    #print "door_positions: ", len(door_positions)
    create_doors_p(dungeon, room_name, '@', graph, door_positions, 0.01)
    #crits[room_name] = create_crits(n, dungeon, room_name, positions, 'c', 'crawler')
    #print "crits num =", len(crits[room_name])
#positions = [(i,1) for i in range(1,6)] + [(i,5) for i in range(1,6)]
#crits = create_crits(10, dungeon, player_room_name, positions, 'c', 'crawler')

### kill_crit() test
#crits = create_crits(1, dungeon, player_room_name, [(3,1)], 'c', 'crawler')
#crits_list = crits[player_room_name]
#c = crits_list[0]
#kill_crit(c, crits_list)

#create_doors(dungeon, '@', graph)
#w, h = room_wh(player_room_name)
#positions = create_row(1, w-1, 0) + create_row(1, w-1, h-1) + create_column(1, h-1, 0) + create_column(1, h-1, w-1)
#print positions
#create_doors_p(dungeon, player_room_name, '@', graph, positions, 0.01)

blit(player)
blit_crits(crits, player_room_name)

graphics(clear, player, ranks, True)
gameover = False

while not gameover:
    # Player input
    keypress = raw_input()

    # Game logic
    result = crit_action(player, keypress, crits)
    if result:
        crits[player_room_name].append(result)
    if player_room_name in crits:
        for c in crits[player_room_name]:
            action = crit_ai(c)
            crit_action(c, action, crits)

    collision_detection_crits(player, crits)

    crawler_count = count_crits(crits, player_room_name)
    if keypress == 'x':
        gameover = True
        break
    if player['hp'] < 1:
        print "Game over!"
        gameover = True
        break
    elif crawler_count <= 0:
        if player_room_name == toughest_room and crawler_count <= 0:
            print "You win!"
            gameover = True
            break

    # Update vars
    player_room = player['room']
    player_room_name = player['room_name']

    # Blit everything unto the room
    clear_room(dungeon, player_room_name)
    blit_crits(crits, player_room_name)
    blit(player)

    # "Graphics"
    graphics(clear, player, ranks, True)


