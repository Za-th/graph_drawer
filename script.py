import tkinter as tk
from tkinter import ttk
from math import sqrt
from math import inf
from typing import Set

### WINDOW
root = tk.Tk()
root.title("Graph Drawer")
root.geometry('1200x800+400+1200')
root.resizable(False, False)
# canvas for drawing graph
canvas = tk.Canvas(root, width=1000, height=800, bg='white')
canvas.pack(side='right')

### VARIABLES
# list of unique ids canvas uses to draw vertices
vertices = []
# dict of id: (vertex,vertex) of id canvas draws edges with and vertex edge is between
edges = {}
# dict of id: weight for edge ids
edge_weights = {}
# list of ids of vertices currently focused, used for adding edges
selected = []
# list of ids of edges currently focused, used for changing edge weights
selected_edges = []
# dict of edge/vertex id: label id, labels are id number for vertices and edge weight for edges
labels = {}
# adjacency graph, vertex id: [neighbour ids], is updated with add/remove vertex/edge functions
adjacency_graph = {}

### FUNCTIONS

# Helpers

# returns if edge exists between u and v
def edge_check(v,u):
    for k in edges:
        if (edges[k][0]==v and edges[k][1]==u
            or
            edges[k][0]==u and edges[k][1]==v):
                return True
    return False

# returns a,b,c such that ax+by+c=0 is a line between the points Q and P
def line_equation(Q,P):
    a = Q[1] - P[1]
    b = P[0] - Q[0]
    c = a*(P[0]) + b*(P[1])
    c = c*-1
    return a,b,c

# returns distance a point is from a line
def point_dist(Q,P,point):
    a,b,c = line_equation(Q,P)
    x,y = point
    denom = sqrt(a**2+b**2)
    if denom != 0:
        return abs(a*x+b*y+c)/denom
    else:
        return 0

# returns a dict of edge id: [neighbour edge ids]
def create_edge_adjacency_graph():
    graph = {}
    edge_list = []
    for e in edges:
        edge_list.append(e)
        graph[e] = []

    for i in range(len(edge_list)):
        e1 = edge_list[i]
        for j in range(i+1,len(edge_list)):
            e2 = edge_list[j]
            if any(x in edges[e2] for x in edges[e1]):
                graph[e1].append(e2)
                graph[e2].append(e1)
    return graph

# returns if graph is connected given an adjacency graph representing edges
def is_connected(adjacency_graph):
    if len(vertices) > 0:
        if inf in dijkstra(vertices[0],adjacency_graph).values():
            return False
    return True

# returns if there is a cycle in the graph given an adjacency graph representing edges
def contains_cycle_loop(v, visited, parent, adjacency_graph):
    visited.append(v)
    for neighbour in adjacency_graph[v]:
        if neighbour not in visited:
            if contains_cycle_loop(neighbour, visited, v, adjacency_graph) == True:
                return True
        elif parent != neighbour:
            return True
    return False
def contains_cycle(adjacency_graph):
    visited = []
    for v in vertices:
        if v not in visited:
            if contains_cycle_loop(v, visited, -1, adjacency_graph) == True:
                return True
    return False

# return id of edge between vertices
def find_edge(u,v):
    for e in edges:
        a,b = edges[e]
        if u in [a,b] and v in [a,b]:
            return e
    return None

# Main Functions

def add_vertex(x,y):
    v = canvas.create_oval(x-20,y-20,x+20,y+20,width=0, fill='grey')
    vertices.append(v)
    # create label
    t = canvas.create_text(
        (x,y),
        text = v,
        font='tkDefaultFont 12',
        fill='white'
    )
    labels[v] = t 
    # add to adjacency graph
    adjacency_graph[v] = []

def add_edge(v,u):
    if v == u:
        return

    x1,y1,_,_ = canvas.coords(v)
    x2,y2,_,_ = canvas.coords(u)
    # draw line
    e = canvas.create_line(
        (x1+20,y1+20),
        (x2+20,y2+20),
        width = 4,
        fill = 'grey'
    )
    # lower line in canvas stack so it is below other elements
    canvas.tag_lower(e)
    # add edge and edge weight to list
    edges[e] = (v,u)
    edge_weights[e] = '1'

    # create label in middle of line for weight
    d = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    t = (d/2)/d
    t = canvas.create_text(
        (((1-t)*x1+t*x2),((1-t)*y1+t*y2)),
        text = 1,
        font='tkDefaultFont 12',
    )
    labels[e] = t
    # put label at top of stack
    canvas.tag_raise(t)

    # add to adjacency graph
    adjacency_graph[v].append(u)
    adjacency_graph[u].append(v)

def delete_vertex(v):
    # vertex
    canvas.delete(v)
    vertices.remove(v)
    # label
    canvas.delete(labels[v])
    del labels[v]
    # delete all edges from v
    edges_to_delete = []
    for e in edges:
        if (v in edges[e]):
            edges_to_delete.append(e)
    for e in edges_to_delete:
        delete_edge(e)
    # adjacency graph
    del adjacency_graph[v]
    for x in adjacency_graph:
        try:
            adjacency_graph[x].remove(v)
        except:
            pass
    # unselect vertex
    try:
        unselect_vertex(v)
    except:
        pass

def delete_edge(e):
    # adjacency graph
    v,u = edges[e]
    adjacency_graph[v].remove(u)
    adjacency_graph[u].remove(v)
    # edge
    canvas.delete(e)
    del edges[e]
    # edge weight
    del edge_weights[e]
    # label
    canvas.delete(labels[e])
    del labels[e]
    # unselect edge
    try:
        unselect_edge(e)
    except:
        pass

def select_vertex(v):
    selected.append(v)
    # add outline
    canvas.itemconfig(v, width='3')

def select_edge(e):
    selected_edges.append(e)
    canvas.itemconfig(e, width=10)

def unselect_edge(e):
    canvas.itemconfig(e, width=3)
    selected_edges.remove(e)

def unselect_vertex(v):
    canvas.itemconfig(v, width='0')
    selected.remove(v)

def uncolour_edges():
    for e in edges:
        canvas.itemconfig(e, fill='grey')

def delete_all():
    to_delete = [v for v in vertices]
    for v in to_delete:
        delete_vertex(v)

def is_safe(v, graph, color, c):
    for neighbor in graph[v]:
        if color[neighbor] == c:
            return False
    return True
def graph_coloring_util(i, graph, color, m):
    if i == len(graph):
        return True  # Everything colored, a solution is found
    
    v = list(graph.keys())[i]
 
    for c in range(1, m + 1):
        if is_safe(v, graph, color, c):
            color[v] = c
 
            # Recur for the next vertices
            if graph_coloring_util(i + 1, graph, color, m):
                return True
 
            # Backtrack
            color[v] = 0
    return False  # No solution found for this coloring
# finds chromatic number and colours vertices
# will not colour vertices past 12 colours
def graph_coloring():
    if len(vertices) == 0:
        return 0
    m = len(vertices)
    colour = {v:0 for v in adjacency_graph.keys()}
 
    if not graph_coloring_util(0, adjacency_graph, colour, m):
        print("No feasible solution exists")
        return 0
     
    # colour vertices
    colors = ['#e32636', '#5d8aa8', '#a4c639', '#915c83', '#008000', '#8db600',
              '#00ffff', '#7fffd4', '#4b5320', '#e9d66b', '#87a96b', '#ff9966']
    for v in colour:
        ### TODO generate colours ??
        try:
            canvas.itemconfig(v, fill=colors[colour[v]])
        except:
            break
 
    # Count unique colors to determine chromatic number
    unique_colors = set(colour.keys())
    return len(unique_colors)
# finds edge chromatic number and colours edges
def graph_edge_colouring():
    if len(edges) == 0:
        return 0
    graph = create_edge_adjacency_graph()
    # this isn't perfectly optimal as the max degree could be less
    m = max(len(graph[i]) for i in graph) + 1
    colour = {e:0 for e in graph.keys()}

    if not graph_coloring_util(0, graph, colour, m):
        print("No feasible solution exists")
        return 0
    
    # colour vertices
    colors = ['#e32636', '#5d8aa8', '#a4c639', '#915c83', '#008000', '#8db600',
              '#00ffff', '#7fffd4', '#4b5320', '#e9d66b', '#87a96b', '#ff9966']
    for e in colour:
        ### TODO generate colours ??
        try:
            canvas.itemconfig(e, fill=colors[colour[e]])
            # canvas.itemconfig(e, border=)
        except:
            break
 
    # Count unique colors to determine chromatic number
    unique_colors = set(colour.keys())
    return len(unique_colors)

# finds Minimum Spanning Tree (colours edges of MST)
def kruskals():
    uncolour_edges()

    if not is_connected(adjacency_graph):
        return None

    weights = {k: v for k, v in sorted(edge_weights.items(), key=lambda item: item[1])}
    print(weights)
    subgraph = []
    adj_graph = {v: [] for v in vertices}
    for e in weights:
        v,u = edges[e]
        adj_graph[v].append(u)
        adj_graph[u].append(v)
        if contains_cycle(adj_graph):
            adj_graph[v].pop()
            adj_graph[u].pop()
        else:
            subgraph.append(e)
            if is_connected(adj_graph):
                for e in subgraph:
                    canvas.itemconfig(e, fill='#318ce7')
                return subgraph
    return None

# finds max distance from a given vertex to all other vertices in the graph, given an adjacency graph representing edges
def dijkstra(v, adjacency_graph):
    dist = {}
    not_visited = []
    for u in vertices:
        dist[u] = inf
        not_visited.append(u)
    dist[v] = 0

    while not_visited:

        # Pick the minimum distance vertex from
        # the set of vertices not yet processed.
        w = inf
        u = -1
        for v in not_visited:
            if dist[v] < w:
                w = dist[v]
                u = v

        # graph is not connected
        if u == -1:
            return dist

        not_visited.remove(u)

        # Update dist value of the adjacent vertices
        for y in adjacency_graph[u]:
            weight = edge_weights[find_edge(u,y)]
            if weight == '\'':
                weight = 1
            if y in not_visited:
                dist[y] = min(dist[y], dist[u] + int(weight))
    return dist

### MOUSE HANDLING
def click_handler(event):
    x = event.x
    y = event.y
    picked_vertices = []
    picked_edges = []

    for e in selected_edges:
        unselect_edge(e)

    # find edge and vertices clicked on
    for v in vertices:
        a,b,c,d = canvas.coords(v)
        if (a<=x and x<=c and b<=y and y<=d):
            picked_vertices.append(v)
    for e in edges:
        a,b,c,d = canvas.coords(e)
        if point_dist((a,b),(c,d),(x,y)) <4:
            picked_edges.append(e)

    # left click - add vertex
    if event.num == 1:
        if len(picked_vertices) == 0:
            add_vertex(x,y)

    # middle click - delete vertex or edge
    if event.num == 2:
        # delete edges (do first to avoid double deleting)
        for e in picked_edges:
            delete_edge(e)
        # delete vertices
        for v in picked_vertices:
            delete_vertex(v)

    # right click - select edge/vertex and create edge between vertices
    if event.num == 3:
        # Select Vertices and Edges
        if len(selected) == 0:
            for v in picked_vertices:
                select_vertex(v)
            # Select edges if not creating an edge
            for e in picked_edges:
                select_edge(e)

        # Unselect Vertices
        elif len(picked_vertices) == 0:
            for v in selected:
                canvas.itemconfig(v, width='0')
            selected.clear()
        
        # Create Edges
        else:
            for v in selected:
                for u in picked_vertices:
                    # check edge doesn't exist already (only simple graphs)
                    if edge_check(v,u):
                        continue
                    add_edge(v,u)
                unselect_vertex(v)
canvas.bind("<Button>", click_handler)

### KEYBOARD HANDLING (for edge weights)
def key_handler(a): 
    if a.keysym == 'BackSpace':
        # remove last digit of weight
        for e in selected_edges:
            if len(edge_weights[e]) > 1:
                edge_weights[e] = edge_weights[e][:-1]
            else:
                edge_weights[e] = '\''
            # update label
            canvas.itemconfig(labels[e], text=edge_weights[e])
    ############ TODO delete
    elif a.keysym == 'a':
        print(is_connected(adjacency_graph))
    #############
    else:
        # add digit to end of weight
        for e in selected_edges:
            if edge_weights[e] == '\'':
                edge_weights[e] = a.keysym
            else:
                edge_weights[e] += a.keysym
            # update label
            canvas.itemconfig(labels[e], text=edge_weights[e])
for i in range(10): 
    root.bind(str(i), key_handler)
root.bind('<BackSpace>', key_handler)

# TODO delete
root.bind('a', key_handler)
#####

########################################
### WIDGETS
# notebook for flipping between buttons and edge/vertex list
notebook = ttk.Notebook(root)
notebook.place(x=0,y=0)

# frame for buttons
buttons = tk.Frame(notebook, width=200, height=800)
notebook.add(buttons, text='Buttons')

# Buttons

ttk.Button(
   buttons,
   text="Chromatic Number", 
   command=graph_coloring
).grid(column=0,row=0)

ttk.Button(
   buttons,
   text="Chromatic Edge Number", 
   command=graph_edge_colouring
).grid(column=0,row=1)
ttk.Button(
   buttons,
   text="MST", 
   command=kruskals
).grid(column=0,row=2)

ttk.Button(
    buttons,
    text='Delete All',
    comman = delete_all
).grid(column=0,row=3)

root.mainloop()

# TODO
# edge vertex list
# zoom