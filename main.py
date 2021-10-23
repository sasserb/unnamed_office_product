
import tkinter as tk

INF = 10000000
NUM_NODES = 1000

OVAL_Y_OFFSET = 20
OVAL_X_OFFSET = 40

global main_net


class Network:

    def __init__(self, generation_key=[['start', 'end']]):
        self.avail_addr = [x for x in range(NUM_NODES)]
        self.start_node = Node(0, 'start')
        self.end_node = Node(0, 'end')

        self.every_node = {self.start_node, self.end_node}

        self.curr_addrs = {'end', 'start'}

        self.PFT = None
        self.topo_sort_list = []

        for i in generation_key:
            root = None
            for j in i:
                if j is 'start':
                    root = 'start'
                    root_node = self.start_node
                elif j is 'end':
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


class MousePosition():
    def __init__(self):
        self.x = 0
        self.y = 0

    def motion(self, event):
        self.x = event.x
        self.y = event.y


window = tk.Tk()

window.title('Get ready to draw')
mycanvas = tk.Canvas(window, width=1250, height=1000, bg='white')
mycanvas.grid(row=1, column=1)
Mouse = MousePosition()
#theoval = mycanvas.createoval(300, 200, 400, 500)


''' Function Name: confirm_and_close
    Purpuse: will save the changes from the edit pop up and update the text on the oval; is trigger from the confirm
    button on the edit window
    Arguments: popup_fillout: tk.Toplevel(); the frame that the edit interface is loaded in
                oval_id: (x,); the unique identifier of the node that is being edited
                name_entry: tk.Entry(); the tkinter widget that holds the text of the name
                cost_entry: tk.Entry(); the tkinter widgit that holds the text of the cost'''


def confirm_and_close(popup_fillout, oval_id, name_entry, cost_entry):
    new_name = name_entry.get()
    new_cost = cost_entry.get()

    mycanvas.addtag_withtag('name=' + new_name, oval_id)
    mycanvas.addtag_withtag('cost=' + new_cost, oval_id)

    #mycanvas.itemconfig(oval_id, text=new_name)
    tags_list = mycanvas.gettags(oval_id)
    name_id = -1
    for tag in tags_list:
        if 'nodenameid:' in tag:
            name_id = tag.replace('nodenameid:', '')
    mycanvas.itemconfigure(name_id, text=f'{new_name}\n{new_cost}')

    popup_fillout.destroy()


''' Function Name: edit_node
    Purpose: launches the edit window for the node that's clicked on
    Arguments: oval_id: (x,); the unique identifier of the node that's being edited'''


def edit_node(oval_id):
    popup_fillout = tk.Toplevel()
    tk.Label(popup_fillout, text='Node Information').grid(row=0, column=0, columnspan=2)
    tags_list = mycanvas.gettags(oval_id)
    old_name = ''
    old_cost = ''
    for tag in tags_list:
        if 'name=' in tag:
            old_name = tag.replace('name=', '')
            mycanvas.dtag(oval_id, tag)
        elif 'cost=' in tag:
            old_cost = tag.replace('cost=', '')
            mycanvas.dtag(oval_id, tag)
    tk.Label(popup_fillout, text="Node Name:").grid(row=1, column=0)
    name_entry = tk.Entry(popup_fillout, width=20)
    name_entry.insert(0, old_name)
    name_entry.grid(row=1, column=1)

    tk.Label(popup_fillout, text="Node Cost:").grid(row=2, column=0)
    cost_entry = tk.Entry(popup_fillout, width=20)
    cost_entry.insert(0, old_cost)
    cost_entry.grid(row=2, column=1)

    tk.Button(popup_fillout, text='Confirm', command=lambda pop=popup_fillout, oval=oval_id, name=name_entry, cost=cost_entry: confirm_and_close(pop, oval, name, cost)).grid(row=4, column=0)


''' Function Name: on_left_click
    Purpose: triggers everytime the LMB is clicked while in the canvas; will do a multitude of things depending on
    which mode is selected in the checkboxes
    Arguments: event: the event of the left click; event.x and event.y will give coords of click'''


def on_left_click(event):

    # The mode selected is draw node
    if draw_mode.get() == 1:
        # created the node and text
        my_oval = mycanvas.create_oval(event.x - OVAL_X_OFFSET, event.y + OVAL_Y_OFFSET, event.x + OVAL_X_OFFSET, event.y - OVAL_Y_OFFSET, fill='white')
        my_text = mycanvas.create_text(event.x, event.y, text='', state=tk.DISABLED)
        '''Create pop up window to fill in info for'''
        # edit_node(my_oval)

        # adds the tags for the node and name
        mycanvas.addtag_withtag('node', my_oval)
        mycanvas.addtag_withtag(f'nodenameid:{my_text}', my_oval)
        mycanvas.addtag_withtag(f'addr:{my_oval}', my_oval)
        mycanvas.addtag_withtag('nodename', my_text)
        mycanvas.addtag_withtag(f'nodeid:{my_oval}', my_text)
        
    # The mode selected is connect nodes
    elif draw_mode.get() == 2:
        global last_clicked_node
        if mycanvas.find_withtag('current'):
            # if the LMB was triggered on an object in the canvas
            clicked_object_id = mycanvas.find_withtag('current')
            # if the object clicked was a node
            if 'node' in mycanvas.gettags(clicked_object_id):
                # if the node clicked is not the second one
                if last_clicked_node is None:
                    last_clicked_node = mycanvas.coords(clicked_object_id)
                    last_clicked_node.append(clicked_object_id)
                # the node clicked is the second one
                else:
                    node_coords = mycanvas.coords(clicked_object_id)
                    my_arrow = mycanvas.create_line(last_clicked_node[2], last_clicked_node[3] - OVAL_Y_OFFSET,
                                                    node_coords[0], node_coords[1] + OVAL_Y_OFFSET,
                                                    arrow="last")
                    mycanvas.addtag_withtag('vertex', my_arrow)
                    mycanvas.addtag_withtag(f'arrowto:{clicked_object_id[0]}', my_arrow)
                    mycanvas.addtag_withtag(f'arrowfrom:{last_clicked_node[4]}', my_arrow)

                    mycanvas.addtag_withtag(f'to:{clicked_object_id[0]}', last_clicked_node[4])
                    last_clicked_node = None

    elif draw_mode.get() == 3:
        pass

    elif draw_mode.get() == 4:
        if mycanvas.find_withtag('current'):
            if 'node' in mycanvas.gettags(mycanvas.find_withtag('current')):
                ovoid = mycanvas.find_withtag('current')
                edit_node(ovoid)

    elif draw_mode.get() == 5:
        if mycanvas.find_withtag('current'):
            if 'node' in mycanvas.gettags('current'):
                nameid = ''
                for tag in mycanvas.gettags('current'):
                    if 'nodenameid:' in tag:
                        nameid = tag.replace('nodenameid:', '')
                mycanvas.delete(mycanvas.find_withtag(nameid))

                mycanvas.delete(mycanvas.find_withtag('current'))

                if mycanvas.find_withtag(f'arrowfrom:{mycanvas.find_withtag("current")}'):
                    pass
                if mycanvas.find_withtag(f'arrowto:{mycanvas.find_withtag("current")}'):
                    pass

            elif 'vertex' in mycanvas.gettags('current'):

                mycanvas.delete(mycanvas.find_withtag('current'))


mycanvas.bind("<Button>", on_left_click)
mycanvas.bind("<Motion>", lambda event: Mouse.motion(event))

'''Radio Buttons for selecting what a click does'''
global last_clicked_node
last_clicked_node = None


def radio_button_reset():
    global last_clicked_node
    last_clicked_node = None



''' Function Name: solve_node
    Purpose: is called by solve_network and will return the list of all the outputs and cost of the
    outgoing connections
    Arguments:
            node_addr: int; the unique address the node node that's being looked at'''


def solve_node(node_addr):
    twolist = []

    if node_addr is 'start':
        twolist.append('start')
        node_id = mycanvas.find_withtag('name=start')
        '''
    elif node_addr is 'end':
        twolist.append('end')
        node_id = mycanvas.find_withtag('name=end')
        '''
    else:
        node_id = mycanvas.find_withtag(f'addr:{node_addr}')
        nodecost = 0
        for tag in mycanvas.gettags(node_id):
            if 'cost=' in tag:
                if tag.replace('cost=', '') is '':
                    nodecost = 0
                else:
                    nodecost = float(tag.replace('cost=', ''))
        twolist.append([node_addr, nodecost])

    for tag in mycanvas.gettags(node_id):
        adjcostlist = []
        if 'to:' in tag:
            adjaddr = int(tag.replace('to:', ''))
            adjid = mycanvas.find_withtag(f'addr:{adjaddr}')
            adjcost = 0
            for adjtag in mycanvas.gettags(adjid):
                if 'cost=' in adjtag:
                    if adjtag.replace('cost=', '') is '':
                        adjcost = 0
                    else:
                        adjcost = float(adjtag.replace('cost=', ''))
            adjcostlist = [adjaddr, adjcost]

        if adjcostlist:
            twolist.append(adjcostlist)

    return twolist


''' Function Name: grab_every_addr
    Purpose: the function is called recursively in order to add every address in the network to the addrset variable
    Arguments:
            addrset: set; the set of every address in the network at the end, should only be added to
            addr: int; the addr of the node to be searched from'''


def grab_every_addr(addrset, addr):

    nodeid = mycanvas.find_withtag(f'addr:{addr}')
    listo = []

    for tag in mycanvas.gettags(nodeid):
        if 'to:' in tag:
            addrset.add(int(tag.replace('to:', '')))
            listo.append(int(tag.replace('to:', '')))

    for item in listo:
        addrset = grab_every_addr(addrset, item)

    return addrset


''' Function Name: solve_network
    Purpose: is called when the solve network button is pressed; will call and do everything necessary in order to
    completely solve the network'''


def solve_network():
    
    onelist = []
    addrset = set()
    startid = mycanvas.find_withtag('name=start')
    addrset.add(int(startid[0]))
    for tag in mycanvas.gettags(startid):
        # print(tag)
        if 'to:' in tag:
            addrset.add(int(tag.replace('to:', '')))

    # after this line, addrset will contain every address in the network
    addrset = grab_every_addr(addrset, startid[0])

    # for every address in the network, create the connections list
    for x in addrset:
        onelist.append(solve_node(x))
    print(onelist)

    for i in range(len(onelist)):
        for j in range(len(onelist[i])):
            if mycanvas.find_withtag('name=start') == mycanvas.find_withtag(f'addr:{onelist[i][j][0]}'):
                onelist[i][j] = 'start'
            elif mycanvas.find_withtag('name=end') == mycanvas.find_withtag(f'addr:{onelist[i][j][0]}'):
                onelist[i][j] = 'end'
    print(onelist)

    global main_net
    main_net = Network(generation_key=onelist)
    main_net.solve_net()
    print(main_net.PFT)


radio_button_frame = tk.Frame(window)
radio_button_frame.grid(row=1, column=0)

draw_mode = tk.IntVar()
draw_mode.set(1)

R1 = tk.Radiobutton(radio_button_frame, text="Draw Nodes", var=draw_mode, value=1, command=radio_button_reset)
R1.pack()
R2 = tk.Radiobutton(radio_button_frame, text="Connect Nodes", var=draw_mode, value=2, command=radio_button_reset)
R2.pack()
R3 = tk.Radiobutton(radio_button_frame, text="Select", var=draw_mode, value=3, command=radio_button_reset)
R3.pack()
R4 = tk.Radiobutton(radio_button_frame, text="Edit", var=draw_mode, value=4, command=radio_button_reset)
R4.pack()
R5 = tk.Radiobutton(radio_button_frame, text="Delete", var=draw_mode, value=5, command=radio_button_reset)
R5.pack()

trigger_button = tk.Button(window, text='Solve Network', command=solve_network)
trigger_button.grid(row=1, column=2)

tk.mainloop()
