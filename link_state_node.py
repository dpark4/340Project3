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
        #print(self.djikstra(4))
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        
        newNode = False
        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
        elif neighbor not in self.neighbors:
            self.neighbors.append(neighbor)

        if not self.graph.in_graph(neighbor):
            newNode = True
        
        #updating seq number
        self.linkSeq[frozenset([self.id, neighbor])] += 1
        seq = self.linkSeq[frozenset([self.id, neighbor])]

        #putting edge in local graph
        self.graph.update_edge(self.id, neighbor, latency)

        #constructing the message
        edges = [[self.id,neighbor,latency,seq]]
        msg = self.construct_message(self.id, edges)

        #print("edge between" + str(self.id) + "and" + str(neighbor) + "sent" )
        self.send_to_neighbors(json.dumps(msg))

        #new node case, send info of the entire graph
        if newNode:
            edges = []
            for e in self.graph.all_edges():
                src = e[0]
                dst = e[1]
                cost = e[2]
                eSeq = self.linkSeq[frozenset([src, dst])]
                edges.append([src,dst,cost,eSeq])
            msg = self.construct_message(self.id, edges)
            
            self.send_to_neighbors(json.dumps(msg))
            



        # latency = -1 if delete a link
        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        msg = json.loads(m)
        #print(msg)
        #grabbing message data
        sender = msg["sender"]
        edges = msg["edges"]

        retransmitEdges = []
        for e in edges:
            src = e[0]
            dst = e[1]
            cost = e[2]
            seq = e[3]
            curSeq = self.linkSeq[frozenset([src, dst])]
           
            #update, relay to every link except the one it got the message from
            if seq > curSeq or curSeq == 0:

                #print("at node: " + str(self.id) + "found update from" + str(sender))
                self.linkSeq[frozenset([src, dst])] = seq
                self.graph.update_edge(src,dst,cost)
                retransmitEdges.append(e)
                
            elif seq < curSeq:
                curLatency = self.graph.get_latency(src,dst)
                edges = []
                edges.append([src,dst,curLatency,curSeq])
                retransmitEdges.append([src,dst,curLatency,curSeq])
                newMsg = self.construct_message(self.id, edges)
                self.send_to_neighbor(sender,json.dumps(newMsg)) 



        
            nextMsg = self.construct_message(self.id,retransmitEdges)


            #for n in self.neighbors:
                #if n != sender:
            self.send_to_neighbors(json.dumps(nextMsg))


        
        #print(src, dst, cost, seq)
        pass

    def construct_message(self, sender, edges):
        msg = {
        "sender": sender,
        "edges" : edges
        }

        return msg

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        path = self.djikstra(destination)
        print(path)
        next_hop = path[len(path) - 1]
        return next_hop
    
    def djikstra(self, destination):
        verticies = set()
        dist = {}
        prev = {}
        for v in self.graph.get_verticies():
            dist[v] = float('inf')
            prev[v] = None
            verticies.add(v)
        dist[self.id] = 0

        #print(verticies)
        while verticies:

            #find unvisited node with lowest distance
            minDist = float('inf')
            minV = -100
            for v in verticies:
                if dist[v] < minDist:
                    minDist  = dist[v]
                    minV = v
            verticies.remove(minV)

            for v, c in self.graph.get_neighbors(minV):
                #has to be in the set
                if v in verticies:
                    alt = dist[minV] + c
                    if alt < dist[v]:
                        dist[v] = alt
                        prev[v] = minV

        #return the shortest path:
        path = []
        t = destination
        #print(prev)
        #print(dist)
        while t != None and t != self.id:
            path.append(t)
            t = prev[t]

        return path




class Graph():
    def __init__(self):
        self.graph = defaultdict(list)
    
    def update_edge(self, source, dest, latency):
    
        if latency == -1:
            print("deleting a node")
        in_source = False
        remove = False
        srcEleToRemove = []
        dstEleToRemove = []
        for i in self.graph[source]:
            if i[0] == dest:
                if latency == -1:
                    srcEleToRemove = i
                    in_source = True
                    remove = True
                    break
                i[1] = latency
                in_source = True
        if not in_source:
            self.graph[source].append([dest,latency])

        in_dest = False
        for i in self.graph[dest]:
            if i[0] == source:
                if latency == -1:
                    dstEleToRemove = i
                    in_dest = True
                    remove = True
                    break
                i[1] = latency
                in_dest = True
        if not in_dest:
            self.graph[dest].append([source,latency])

        if remove:
            print(dstEleToRemove, srcEleToRemove)
            self.graph[dest].remove(dstEleToRemove)
            self.graph[source].remove(srcEleToRemove)


    def get_verticies(self):
        return self.graph.keys()

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
    #returns 3 tuple of src, dst, cost of every edge present in node's graph
    def all_edges(self):
        edges = []
        for k in self.graph.keys():
            for e in self.graph[k]:
                edges.append((k,e[0],e[1]))
        return edges

    def display(self):
        print(self.graph)
    
    def in_graph(self, n):
        return n in self.graph.keys()