from simulator.node import Node
import time
import copy
import json
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
        self.dv.display()
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
        elif neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
        # latency = -1 if delete a link

        self.dv.update_neighbor_cost(neighbor,latency)
        #print("neigbor cost", self.id, neighbor, self.dv.make_json())
        #self.dv.display()
        updated_dv = self.dv.get_dv()
        self.send_to_neighbors(json.dumps(updated_dv))
        
        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        new_dv = json.loads(m)
        self.reconstruct_json(new_dv)
        same = self.dv.update_neighbor_dv(new_dv)
        updated_dv = self.dv.get_dv()
        if not same:
            self.send_to_neighbors(json.dumps(updated_dv))
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        dv = self.dv.get_dv()
        return dv["info"][destination]["next_hop"]
        

    def reconstruct_json(self, msg):
        msgInfo = msg["info"]
        newInfo = {}
        for k,v in msgInfo.items():
            newInfo[int(k)] = v

        msg["info"] = newInfo
        return msg





class Distance_Vector():
    def __init__(self, id):
        #print(type(id))
        self.dv = {
            "node": id,
            "seq": 0,
            "info": {}
        }

        self.dv["info"][id] = self.dv_info(0, [], [])

        self.id = id

        self.neighbor_link_costs = {}
        
        self.neighbor_dist_vecs = {}

        

    
    def update_neighbor_cost(self, neighbor, cost):
        self.neighbor_link_costs[neighbor] = cost
        if cost == -1:
            self.neighbor_link_costs.pop(neighbor)
            self.neighbor_dist_vecs.pop(neighbor)
        return self.recalculate_dv()


    def update_neighbor_dv(self, dv):
        #TODO: time checking
        neighbor = dv["node"]
        
        if neighbor in self.neighbor_dist_vecs:
            cur_dv_seq = self.neighbor_dist_vecs[neighbor]["seq"]
            if dv["seq"] < cur_dv_seq:
                return True

        
        #print(1,type(neighbor))
        self.neighbor_dist_vecs[neighbor] = dv
        return self.recalculate_dv()
        

    def recalculate_dv(self):
        dist = {}
        path = {}

        vertices = set()

        #add every vertex to the set
        for neighbor, dv in self.neighbor_dist_vecs.items():
            dvInfo = dv["info"]
            for node, destInfo in dvInfo.items():
                #print(2, type(node))
                
                vertices.add(node)
        #incase neighbor hasn't sent dv
        for neighbor in self.neighbor_link_costs.keys():
            #print(3, type(neighbor))
            vertices.add(neighbor)

        
        #initialize to infinity
        for v in vertices:
            dist[v] = float('inf')
            path[v] = []
        dist[self.id] = 0

        #incase neighbor hasn't sent dv
        for neighbor, cost in self.neighbor_link_costs.items():
            if cost < dist[neighbor]:
                #print(4, type(neighbor))
                dist[neighbor] = cost
                path[neighbor] = [neighbor]
        #bellman ford edge relaxing

        #for i in range(len(vertices)):
        for v in vertices:
            for neighbor, cost in self.neighbor_link_costs.items(): 
                #print(5, type(neighbor))
                if neighbor in self.neighbor_dist_vecs:
                    neighbor_info = self.neighbor_dist_vecs[neighbor]["info"]
                    if v in neighbor_info:
                        total_dist = dist[neighbor] + neighbor_info[v]["cost"]
                        #if total_dist == float('inf'):
                            #print("infinity hit")
                        if total_dist < dist[v]:
                            new_path = copy.deepcopy(neighbor_info[v]["path"])
                        #no cycles
                            neighbor_path = path[neighbor]
                            repeat = False
                            for n in neighbor_path:
                                if n in new_path:
                                    repeat = True
                                new_path.append(n)
                            if repeat:
                                continue
                            dist[v] = total_dist
                            path[v] = new_path
        #recreate info map
        newInfo = {}

        #print(self.id,path)
        for v in vertices:
            #print(v)
            if path[v]:
                newInfo[v] = self.dv_info(dist[v], path[v][-1], path[v])
            else:
                newInfo[v] = self.dv_info(dist[v], path[v], path[v])

        oldInfo = self.dv["info"]
        
        eq = oldInfo == newInfo
        #print(eq)
        #update to our dv
        if not eq:
            self.dv["info"] = newInfo
            self.dv["seq"] = self.dv["seq"] + 1
            #print(newInfo == self.dv["info"])
        return eq

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

    def get_dv(self):
        return self.dv
    
    def equals(self, info1, info2):
        info1_keys = list(info1.keys()).sort()
        info2_keys = list(info2.keys()).sort()
        if not info1_keys or not info2_keys:
            return False
        if len(info1_keys) != len(info2_keys):
            return False
        for i in len(info1_keys):
            if info1_keys[i] != info2_keys[i]:
                return False
            i1 = info1[i]
            i2 = info2[i]
            ci1 = i1["cost"]
            ci2 = i2["cost"]
            nh1 = i1["next_hop"]
            nh2 = i2["next_hop"]
            if ci1 != ci2 or nh1 != nh2:
                return False
        return True
            

            

        
        pass





