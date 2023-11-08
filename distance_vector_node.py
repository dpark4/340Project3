from simulator.node import Node
import time
import copy
#DV STRUCTURE
"""{
    node: 

    timestamp:

    info:
        {


            dest 1: {c: cost, 
                    next_hop: next_hop,
                     path:  set(path)}

            dest 2: {c: cost, 
                    next_hop: next_hop,
                     path:  set(path)}

            .  
            .
            .
            dest n:
        
        }
} 


Outbound Links (only neighbors)
{
    n1: cost,
    n2: cost,
    .
    .
    .
    

}

Neighbor Distance Vectors
{
    n1: DV
    n2: DV
    .
    .
    .

}
"""




class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = Distance_Vector(id)
        

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        self.dv.update_neighbor_cost(neighbor,latency)
        self.dv.display()
        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1
    
    def recompute_dv(self):
        pass


class Distance_Vector():
    def __init__(self, id):
        self.dv = {
            "node": id,
            "time": time.gmtime(),
            "info": {}
        }

        self.dv["info"][id] = self.dv_info(0, None, None)

        self.id = id

        self.neighbor_link_costs = {}
        
        self.neighbor_dist_vecs = {}

        

    
    def update_neighbor_cost(self, neighbor, cost):
        self.neighbor_link_costs[neighbor] = cost
        self.recalculate_dv()
        pass

    def update_neighbor_dv(self, neighbor, dv):
        self.neighbor_dist_vecs[neighbor] = dv
        self.recalculate_dv()
        pass

    def recalculate_dv(self):
        dist = {}
        path = {}

        vertices = set()

        #add every vertex to the set
        for neighbor, dv in self.neighbor_dist_vecs:
            dvInfo = dv["info"]
            for node, destInfo in dvInfo:
                vertices.add(node)
        #incase neighbor hasn't sent dv
        for neighbor in self.neighbor_link_costs.keys():
            vertices.add(neighbor)

        #initialize to infinity
        for v in vertices:
            dist[v] = float('inf')
            path[v] = []
        dist[self.id] = 0

        #incase neighbor hasn't sent dv
        for neighbor, cost in self.neighbor_link_costs.items():
            if cost < dist[neighbor]:
                dist[neighbor] = cost
                path[neighbor] = [neighbor]
        #bellman ford edge relaxing
        for v in vertices:
            for neighbor, cost in self.neighbor_link_costs.items(): 
                if v in self.neighbor_dist_vecs:
                    neighbor_info = self.neighbor_dist_vecs[neighbor]["info"]
                    if v in neighbor_info:
                        total_dist = cost + neighbor_info[v]["cost"]
                        new_path = copy.deepcopy(neighbor_info[v]["path"])
                        #no cycles
                        if neighbor in new_path:
                            continue
                        new_path.append(neighbor)
                        if total_dist < dist[v]:
                            dist[v] = total_dist
                            path[v] = new_path
        #recreate info map
        newInfo = {}
        for v in vertices:
            newInfo[v] = self.dv_info(dist[v], path[v][-1], path[v])
        #update to our dv
        self.dv["info"] = newInfo
        self.dv["time"] = time.gmtime()


    def dv_info(self, cost, next_hop, path):
        return {
            "cost": cost,
            "next_hop": next_hop,
            "path": path
        }
    
    def get_neighbors(self):
        return self.neighbor_link_costs.keys()
    
    def display(self):
        print(self.dv)





