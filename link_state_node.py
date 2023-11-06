from simulator.node import Node
from collections import defaultdict
import json

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.graph = Graph()
        self.linkSeq = defaultdict(int)

    # Return a string
    def __str__(self):
        self.graph.display()
        print(self.linkSeq)
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:

            self.neighbors.remove(neighbor)
        else:
            self.neighbors.append(neighbor)

        
        #updating seq number
        self.linkSeq[frozenset([self.id, neighbor])] += 1
        seq = self.linkSeq[frozenset([self.id, neighbor])]

        #putting edge in local graph
        self.graph.update_edge(self.id, neighbor, latency)

        #constructing the message
        msg = {
            "sender": self.id,
            "src": self.id,
            "dst": neighbor,
            "cost": latency,
            "seq": seq
        }

        print("edge between" + str(self.id) + "and" + str(neighbor) + "sent" )
        self.send_to_neighbors(json.dumps(msg))

        



        # latency = -1 if delete a link
        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        msg = json.loads(m)
        #grabbing message data
        sender = msg["sender"]
        src = msg["src"]
        dst = msg["dst"]
        cost = msg["cost"]
        seq = msg["seq"]

        curseq = self.linkSeq[frozenset([src, dst])]
        #now the sender is this node
        msg["sender"] = self.id
        #update, relay to every link except the one it got the message from
        if seq > curseq or curseq == 0:

            print("at node: " + str(self.id) + "found update from" + str(sender))
            self.linkSeq[frozenset([src, dst])] = seq
            self.graph.update_edge(src,dst,cost)
            
            for n in self.neighbors:
                if n != sender:
                    print("sending to neighbor")
                    self.send_to_neighbor(n,json.dumps(msg))
        elif seq < curseq:
            curLatency = self.graph.get_latency(src,dst)
            msg["cost"] = curLatency
            msg[seq] = curseq
            self.send_to_neighbor(sender,json.dumps(msg))


        
        #print(src, dst, cost, seq)
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1
class Graph():
    def __init__(self):
        self.graph = defaultdict(list)
    
    def update_edge(self, source, dest, latency):
    
        in_source = False
        for i in self.graph[source]:
            if i[0] == dest:
                i[1] = latency
                in_source = True
        if not in_source:
            self.graph[source].append([dest,latency])

        in_dest = False
        for i in self.graph[dest]:
            if i[0] == source:
                i[1] = latency
                in_dest = True
        if not in_dest:
            self.graph[dest].append([source,latency])



    def get_neighbors(self, node):
        return self.graph[node]

    def get_neighbors_latencies(self, node):
        latencies = []
        for neighbor in self.graph[node]:
            latencies.append(neighbor[1])
        return latencies

    def get_latency(self, source, dest):
        for node in self.graph[source]:
            if node[0] == dest:
                return node[1]
        return -1
    def display(self):
        print(self.graph)

    