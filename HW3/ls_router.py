# Base router class
from router import Router

# This is long enough so that broadcasts complete even on large topologies
BROADCAST_INTERVAL = 1000


# Class representing link state routers
class LSRouter(Router):
    def __init__(self, router_id):
        # Common initialization routines
        Router.__init__(self, router_id)

        # Is the broadcast complete? => Can we run Dijkstra's algorithm?
        # For now, we'll use a simple heuristic for this:
        # If BROADCAST_INTERVAL since the first link state advertisement (LSA) at time 0,
        # we'll declare the broadcast complete
        self.broadcast_complete = False

        # Have you run Dijkstra's algorithm? This is to ensure you don't repeatedly run it.
        self.routes_computed = False

        # LSA dictionary mapping from a router ID to the links for that router.
        # We'll initialize lsa_dict to  this router's own links.
        self.lsa_dict = dict()

        # For each LSA received from a distinct router,
        # maintain if it has been broadcasted or not.
        # This is to avoid repeated broadcasts of the same LSA
        # We'll initialize self.broadcasted to reflect the fact that this router's own links
        # have not yet been broadcasted as of time 0.
        self.broadcasted = {self.router_id: False}

    # Initialize link state to this router's own links alone
    def initialize_algorithm(self):
        self.lsa_dict = {self.router_id: self.links}

    def tick(self, tick):
        if tick >= BROADCAST_INTERVAL and not self.routes_computed:
            # If broadcast phase is over, compute routes and return
            self.broadcast_complete = True
            self.dijkstras_algorithm()
            self.routes_computed = True
            return
        elif tick < BROADCAST_INTERVAL:
            for lsa in self.lsa_dict:
                if lsa not in self.broadcasted or self.broadcasted[lsa] == False:
                    for neighbor in self.neighbors:
                        self.send(neighbor, self.lsa_dict[lsa], lsa)
                    self.broadcasted[lsa] = True
            # TODO: Go through the LSAs received so far.

            # broadcast each LSA to this router's neighbors if the LSA has not been broadcasted yet
        else:
            return

    # Note that adv_router is the router that generated this advertisment,
    # which may be different from "self",
    # the router that is broadcasting this advertisement by sending it to a neighbor of self.
    def send(self, neighbor, ls_adv, adv_router):
        neighbor.lsa_dict[adv_router] = ls_adv
        # It's OK to reinitialize this even if adv_router even if adv_router is in lsa_dict

    def dijkstras_algorithm(self):
        # TODO:
        # (1) Implement Dijkstra's single-source shortest path algorithm
        # to find the shortest paths from this router to all other destinations in the network.
        # Feel free to use a different shortest path algo. if you're more comfortable with it.
        # (2) Remember to populate self.fwd_table with the next hop for every destination
        # because simulator.py uses this to check your LS implementation.
        # (3) If it helps, you can use the helper function next_hop below to compute the next hop once you
        # have populated the prev dictionary which maps a destination to the penultimate hop
        # on the shortest path to this destination from this router.

        prev = dict()
        Q = []
        for i in self.neighbors:
            Q.append(i.router_id)
        distances = dict()
        for q in Q:
            prev[q] = self.router_id
            distances[q] = self.links[q]
        while len(Q) != 0:
            min = distances[Q[0]]
            u = Q[0]
            for q in Q:
                if distances[q] < min:
                    min = distances[q]
                    u = q
            Q.remove(u)
            for i in self.lsa_dict[u]:
                if i == prev[u]:
                    continue
                if i in distances:
                    if distances[u] + self.lsa_dict[u][i] < distances[i]:
                        prev[i] = u
                        distances[i] = distances[u] + self.lsa_dict[u][i]
                else:
                    distances[i] = distances[u] + self.lsa_dict[u][i]
                    prev[i] = u
                    Q.append(i)

        for d in self.lsa_dict:
            if d != self.router_id:
                self.fwd_table[d] = self.next_hop(d, prev)

    # Recursive function for computing next hops using the prev dictionary
    def next_hop(self, dst, prev):
        assert (
            prev[dst] != -1
        )  # Can't find next_hop if dst is disconnected from self.router_id
        assert self.router_id != dst  # Nor if dst and self.router_id are the same
        if prev[dst] == self.router_id:
            return dst  # base case, src and dst are directly connected
        else:
            return self.next_hop(prev[dst], prev)
