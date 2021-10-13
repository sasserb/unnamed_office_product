
INF = 10000000

class Network:
    def __init__(self):
        self.avail_addr = [x for x in range(1000)]
        self.start_node = Node(0, self.avail_addr.pop())
        self.end_node = Node(0, self.avail_addr.pop())
        self.PFT = None
        self.topo_sort_list = []

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
        # print(listo)


main_net = Network()
place = Node(5, main_net.avail_addr.pop())
place.outgoing.append(main_net.end_node)
main_net.start_node.add_successor(place)
place2 = Node(20, main_net.avail_addr.pop())
place2.outgoing.append(main_net.end_node)
main_net.start_node.add_successor(place2)
place3 = Node(25, main_net.avail_addr.pop())
place3.outgoing.append(main_net.end_node)
place.add_successor(place3)
place.rem_successor(main_net.end_node)
main_net.solve_net()
print(main_net.PFT)
