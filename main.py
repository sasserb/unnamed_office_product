
import tkinter as tk

INF = 10000000
NUM_NODES = 1000

OVAL_Y_OFFSET = 20
OVAL_X_OFFSET = 40


class Network:

    def __init__(self, generation_key=[['s', 'e']]):
        self.avail_addr = [x for x in range(NUM_NODES)]
        self.start_node = Node(0, 's')
        self.end_node = Node(0, 'e')

        self.every_node = {self.start_node, self.end_node}

        self.curr_addrs = {'e', 's'}

        self.PFT = None
        self.topo_sort_list = []

        for i in generation_key:
            root = None
            for j in i:
                if j is 's':
                    root = 's'
                    root_node = self.start_node
                elif j is 'e':
                    root_node.add_successor(self.end_node)
                else:
                    if root is None:
                        root = j[0]
                        if root in self.curr_addrs:
                            for item in self.every_node:
                                if item.addr == root:
                                    root_node = item
                        else:
                            root_node = Node(j[1], j[0])
                            self.every_node.add(root_node)
                            self.curr_addrs.add(root)
                    else:
                        if j[0] in self.curr_addrs:
                            for item in self.every_node:
                                if item.addr == j[0]:
                                    nodo = item
                        else:
                            nodo = Node(j[1], j[0])
                            self.every_node.add(nodo)
                            self.curr_addrs.add(j[0])

                        root_node.add_successor(nodo)

    def asap_pathing(self):
        self.start_node.EST = 0
        for n in self.topo_sort_list:
            for adj in n.outgoing:
                if adj.EST < n.EST + n.cost:
                    adj.EST = n.EST + n.cost
        self.PFT = self.end_node.EST

    def alap_pathing(self):
        self.end_node.LST = 0
        for n in reversed(self.topo_sort_list):
            for adj in n.outgoing:
                if n.LST < n.cost + adj.LST:
                    n.LST = n.cost + adj.LST
        for n in self.topo_sort_list:
            n.LST = self.PFT - n.LST

    def set_slack(self):
        for n in self.topo_sort_list:
            n.slack = n.LST - n.EST

    def solve_net(self):
        self.start_node.topological_sort(self.topo_sort_list)
        self.asap_pathing()
        self.alap_pathing()
        self.set_slack()


class Node:
    def __init__(self, cost, addr):
        self.cost = cost
        self.addr = addr
        self.outgoing = []
        self.LST = -1 * INF
        self.EST = -1 * INF
        self.slack = None
        self.color = 'w'

    def add_successor(self, next_node):
        self.outgoing.append(next_node)

    def rem_successor(self, rem_node):
        self.outgoing = [i for i in self.outgoing if i != rem_node]

    def topological_sort(self, listo):

        self.color = 'g'
        for n in self.outgoing:
            if n.color == 'w':
                n.topological_sort(listo)
        self.color = 'b'
        listo.insert(0, self)

window = tk.Tk()

window.title('Get ready to draw')
mycanvas = tk.Canvas(window, width=1250, height=1000, bg='white')
mycanvas.grid(row=1, column=1)
#theoval = mycanvas.createoval(300, 200, 400, 500)


def on_left_click(event):
    pass
    #print('Button-2 pressed at x = % d, y = % d' % (event.x, event.y))
    if draw_mode.get() == 1:
        my_oval = mycanvas.create_oval(event.x - OVAL_X_OFFSET, event.y + OVAL_Y_OFFSET, event.x + OVAL_X_OFFSET, event.y - OVAL_Y_OFFSET, fill='white')
        mycanvas.addtag_withtag('node', my_oval)
        print(my_oval)
        print(mycanvas.gettags(my_oval))
    elif draw_mode.get() == 2:
        if mycanvas.find_withtag('current'):
            clicked_object_id = mycanvas.find_withtag('current')
            if 'node' in mycanvas.gettags(clicked_object_id):
                node_coords = mycanvas.coords(clicked_object_id)
                my_arrow = mycanvas.create_line(node_coords[2], node_coords[3] - OVAL_Y_OFFSET, 200, 200, arrow="last")
                mycanvas.addtag_withtag('vertex', my_arrow)

    elif draw_mode.get() == 3:
        pass


mycanvas.bind("<Button>", on_left_click)

'''Radio Buttons for selecting what a click does'''

radio_button_frame = tk.Frame(window)
radio_button_frame.grid(row=1, column=0)

draw_mode = tk.IntVar()
draw_mode.set(1)

R1 = tk.Radiobutton(radio_button_frame, text="Draw Nodes", var=draw_mode, value=1)
R1.pack()
R2 = tk.Radiobutton(radio_button_frame, text="Connect Nodes", var=draw_mode, value=2)
R2.pack()
R3 = tk.Radiobutton(radio_button_frame, text="Select", var=draw_mode, value=3)
R3.pack()

tk.mainloop()
list_net =[['s', [1,5],[2,2]], [[1,5],[3,2],[4,1]], [[2,2],[5,10]], [[3,2],[8,1]], [[4,1],[8,1]], [[5,10],[6,1]], [[8,1],[7,5]], [[6,1],[7,5]],[[7,5],'e']]
main_net = Network(generation_key=list_net)

main_net.solve_net()
print(main_net.PFT)
