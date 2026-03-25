"""
Unit 3: Adversarial Search (Minimax, Alpha-Beta) & CSP
"""

# --- Constraint Satisfaction Problem (CSP) ---
class StrategyCSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables      # e.g., ['Selected_Mitigation']
        self.domains = domains          # e.g., {'Selected_Mitigation': ['Kinetic', 'Nuclear', 'Tractor']}
        self.constraints = constraints  # Budget, Time, Risk rules

    def is_consistent(self, assignment):
        strategy = assignment.get('Selected_Mitigation')
        if not strategy: return True
        
        # Check against constraints
        for constraint in self.constraints:
            if not constraint.check(strategy):
                return False
        return True

class BudgetConstraint:
    def __init__(self, max_budget):
        self.max_budget = max_budget
        self.costs = {'Kinetic': 1.2, 'Nuclear': 3.5, 'Tractor': 0.8}
        
    def check(self, strategy):
        return self.costs.get(strategy, 999) <= self.max_budget

# --- Minimax with Alpha-Beta Pruning ---
class GameNode:
    def __init__(self, name, is_max, values=None):
        self.name = name
        self.is_max = is_max
        self.children = []
        self.value = None
        self.is_leaf = False
        
        if values is not None:
            self.is_leaf = True
            self.value = values

def alphabeta(node, depth, alpha, beta, is_maximizing_player):
    if node.is_leaf or depth == 0:
        return node.value
        
    if is_maximizing_player:
        value = float('-inf')
        for child in node.children:
            value = max(value, alphabeta(child, depth - 1, alpha, beta, False))
            alpha = max(alpha, value)
            if beta <= alpha:
                print(f"Pruning at {node.name} (Beta cutoff)")
                break # Beta cutoff
        return value
    else:
        value = float('inf')
        for child in node.children:
            value = min(value, alphabeta(child, depth - 1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:
                print(f"Pruning at {node.name} (Alpha cutoff)")
                break # Alpha cutoff
        return value

if __name__ == "__main__":
    # Test CSP
    csp = StrategyCSP(
        variables=['Selected_Mitigation'],
        domains={'Selected_Mitigation': ['Kinetic', 'Nuclear', 'Tractor']},
        constraints=[BudgetConstraint(max_budget=2.0)]
    )
    print("Nuclear passes budget?", csp.is_consistent({'Selected_Mitigation': 'Nuclear'}))
    print("Kinetic passes budget?", csp.is_consistent({'Selected_Mitigation': 'Kinetic'}))
    
    # Test Alpha-Beta
    root = GameNode("Planner (Max)", True)
    nature1 = GameNode("Nature Outcome 1 (Min)", False)
    nature2 = GameNode("Nature Outcome 2 (Min)", False)
    root.children = [nature1, nature2]
    
    nature1.children = [GameNode("L1", True, 50), GameNode("L2", True, -10)]
    nature2.children = [GameNode("L3", True, 20), GameNode("L4", True, -30)]
    
    print("\nRunning Minimax with Alpha-Beta pruning:")
    best_val = alphabeta(root, 2, float('-inf'), float('inf'), True)
    print("Optimal guaranteed payoff:", best_val)
