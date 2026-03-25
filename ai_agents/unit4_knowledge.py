"""
Unit 4: Knowledge Representation
Demonstrating Propositional Logic, Predicate logic matching, Semantic Nets, and Frames.
"""

# --- Frames & Semantic Nets Representation ---
class Frame:
    def __init__(self, name, slots):
        self.name = name
        self.slots = slots
        
asteroid_frame = Frame("Asteroid_Instance", {
    "is_a": "Near_Earth_Object",
    "diameter": 130,
    "composition": "Rocky",
    "risk_level": "High"
})

# --- Knowledge Based Agent ---
class KnowledgeBase:
    def __init__(self):
        self.facts = set()
        self.rules = []
        
    def tell(self, fact):
        """Add a propositional fact to the knowledge base."""
        self.facts.add(fact)
        print(f"[KB TELL] Fact recorded: {fact}")
        
    def add_rule(self, conditions, conclusion):
        """Add an IF-THEN implication rule."""
        self.rules.append((set(conditions), conclusion))
        
    def infer(self):
        """Forward chaining algorithm to derive new knowledge."""
        inferred_new = True
        conclusions = set()
        
        while inferred_new:
            inferred_new = False
            for conditions, conclusion in self.rules:
                if conclusion not in self.facts and conclusion not in conclusions:
                    if conditions.issubset(self.facts):
                        conclusions.add(conclusion)
                        self.facts.add(conclusion)
                        print(f"[KB INFER] Rule fired! Derived: {conclusion}")
                        inferred_new = True
                        
        return conclusions

# --- Uncertain Reasoning (Probabilities) ---
class UtilityBasedAgent:
    """
    A utility-based agent calculates Expected Utility considering uncertainty.
    EU(a) = Sum [ P(Result(a) = s') * U(s') ]
    """
    def __init__(self):
        self.utilities = {
            'Success': 100,
            'Partial': 40,
            'Failure': -1000
        }
        
    def expected_utility(self, action_probs):
        eu = 0
        for outcome, prob in action_probs.items():
            eu += prob * self.utilities.get(outcome, 0)
        return eu

if __name__ == "__main__":
    print("--- Propositional Logic KB ---")
    kb = KnowledgeBase()
    kb.add_rule(["Risk_Critical", "Time_Short"], "Require_High_Yield")
    kb.add_rule(["Require_High_Yield"], "Dispatch_Nuclear_Missile")
    
    kb.tell("Risk_Critical")
    kb.tell("Time_Short")
    
    print("\nRunning inference engine:")
    kb.infer()
    
    print("\n--- Semantic Frame Example ---")
    print(f"Asteroid Frame properties: {asteroid_frame.slots}")
    
    print("\n--- Utility-Based Agent ---")
    agent = UtilityBasedAgent()
    kinetic_eu = agent.expected_utility({'Success': 0.8, 'Failure': 0.2})
    print(f"Kinetic Impactor Expected Utility: {kinetic_eu}")
