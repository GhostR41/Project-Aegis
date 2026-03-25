"""
Unit 1 & 2: Search Algorithms & Problem Formulation
This module demonstrates finding the best mitigation strategy using various search techniques.
"""
import heapq
from collections import deque

# --- State Space Formulation ---
class AsteroidState:
    def __init__(self, name, risk, time_window, strategy=None, cost=0):
        self.name = name
        self.risk = risk
        self.time_window = time_window
        self.strategy = strategy
        self.g_cost = cost # Path cost
        self.h_cost = self._calculate_heuristic() # Heuristic cost
        
    def _calculate_heuristic(self):
        # h(n) heuristic: Estimated risk failure cost based on strategy
        if self.strategy is None:
            return 100
        risk_penalties = {
            'Kinetic Impactor': 20 if self.risk == 'Critical' else 5,
            'Gravity Tractor': 50 if self.time_window < 30 else 10,
            'Nuclear Deflection': 5 if self.risk == 'Critical' else 40,
            'Solar Sail': 80 if self.time_window < 100 else 20
        }
        return risk_penalties.get(self.strategy, 100)

    def f_cost(self):
        return self.g_cost + self.h_cost

    def __lt__(self, other):
        return self.f_cost() < other.f_cost()

class ProblemSolvingAgent:
    def __init__(self, initial_state):
        self.initial_state = initial_state
        # Actions: Available Strategies and their path costs
        self.actions = {
            'Kinetic Impactor': 15,
            'Gravity Tractor': 30,
            'Nuclear Deflection': 50,
            'Solar Sail': 10
        }
        
    def expand(self, state):
        children = []
        for action, cost in self.actions.items():
            child = AsteroidState(
                state.name, state.risk, state.time_window, 
                strategy=action, cost=state.g_cost + cost
            )
            children.append(child)
        return children

# --- Search Algorithms ---
def breadth_first_search(problem):
    """BFS: Expands shallowest unexpanded node."""
    queue = deque([problem.initial_state])
    explored = []
    while queue:
        node = queue.popleft()
        explored.append(node.strategy)
        # Goal check omitted for simplicity, returns list of expanded nodes
        if node.strategy and len(explored) == len(problem.actions):
            break
        queue.extend(problem.expand(node))
    return explored

def a_star_search(problem):
    """A* Search: Minimizes f(n) = g(n) + h(n)."""
    frontier = []
    heapq.heappush(frontier, problem.initial_state)
    best_strategy = None
    
    while frontier:
        current = heapq.heappop(frontier)
        if current.strategy:
            best_strategy = current
            break # Goal reached with lowest f(n)
            
        for child in problem.expand(current):
            heapq.heappush(frontier, child)
            
    return best_strategy

if __name__ == "__main__":
    initial_state = AsteroidState("Apophis", risk="Critical", time_window=10)
    agent = ProblemSolvingAgent(initial_state)
    
    print("--- Running BFS ---")
    print("Expanded:", breadth_first_search(agent))
    
    print("\n--- Running A* Search ---")
    best = a_star_search(agent)
    print(f"Optimal Strategy: {best.strategy} (Total Cost: {best.f_cost()})")

# Example of TSP (Travelling Salesman) Sub-problem
def tsp_satellite_visit_order(satellites, distances):
    """
    Finds the shortest path to visit all monitoring satellites.
    A classic NP-Complete problem.
    """
    pass # Implementation of permutation search or DP goes here
