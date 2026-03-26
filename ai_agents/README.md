# AI Agents — Project Aegis

This folder contains the core AI logic for **Project Aegis**, an asteroid threat mitigation system. Each file corresponds to a distinct AI curriculum unit, all written in **Python**.

---

## Language

**Python 3** — all files are pure Python. No external runtime or build step is required.

---

## Files at a Glance

| File | Unit | Core Topic |
|---|---|---|
| `unit1_2_search.py` | 1 & 2 | Search algorithms & problem formulation |
| `unit3_adversarial_csp.py` | 3 | Adversarial search & constraint satisfaction |
| `unit4_knowledge.py` | 4 | Knowledge representation & inference |

---

## `unit1_2_search.py` — Search Algorithms

### Libraries / Frameworks
| Import | Purpose |
|---|---|
| `heapq` (stdlib) | Min-heap / priority queue for A* frontier |
| `collections.deque` (stdlib) | FIFO queue for BFS frontier |

### Algorithms
| Algorithm | Description |
|---|---|
| **Breadth-First Search (BFS)** | Uninformed search; expands the shallowest unexplored node first using a FIFO queue. |
| **A\* Search** | Informed search; selects the node with the lowest `f(n) = g(n) + h(n)`. Optimal when the heuristic is admissible. |
| **Custom Heuristic (`h(n)`)** | Strategy-specific penalty function estimating remaining cost based on risk level and time window. |
| **TSP Stub** | Placeholder for a Travelling Salesman Problem permutation/DP solution (NP-Complete). |

### Key Concepts
- **State-space formulation** — each state encodes an asteroid + a chosen mitigation strategy.
- **Path cost (`g_cost`)** vs **heuristic (`h_cost`)** decomposition.
- **Node expansion** — `ProblemSolvingAgent.expand()` generates all successor states.
- **Problem-solving agent** architecture.

### Classes & Functions
| Name | Role |
|---|---|
| `AsteroidState` | State node: stores name, risk, time window, chosen strategy, g-cost, h-cost. |
| `ProblemSolvingAgent` | Holds actions + costs; generates children via `expand()`. |
| `breadth_first_search()` | BFS implementation returning the order of explored nodes. |
| `a_star_search()` | A* implementation returning the strategy with the lowest f-cost. |
| `tsp_satellite_visit_order()` | Stub for satellite visit-order optimisation. |

---

## `unit3_adversarial_csp.py` — Adversarial Search & CSP

### Libraries / Frameworks
None — pure Python.

### Algorithms
| Algorithm | Description |
|---|---|
| **Minimax** | Game-tree search for two-player zero-sum games; one player maximises, the other minimises. |
| **Alpha-Beta Pruning** | Minimax optimisation; prunes branches where `β ≤ α`, eliminating nodes that cannot affect the final decision. |
| **CSP Consistency Check** | Validates variable assignments against a list of constraint objects; returns `False` on the first violated constraint. |
| **Budget Constraint Check** | Concrete constraint: `strategy_cost ≤ max_budget`. |

### Key Concepts
- **Adversarial / game-tree search** — planner (MAX) vs. nature/uncertainty (MIN).
- **Alpha (α)** — best guaranteed value for the maximiser so far (lower bound).
- **Beta (β)** — best guaranteed value for the minimiser so far (upper bound).
- **Constraint Satisfaction Problem (CSP)** — variables, domains, and constraints framework.
- **Depth-limited search** — tree traversal respects a configurable depth limit.

### Classes & Functions
| Name | Role |
|---|---|
| `StrategyCSP` | CSP container: variables, domains, constraint list; exposes `is_consistent()`. |
| `BudgetConstraint` | Constraint that checks whether a strategy's cost is within the allowed budget. |
| `GameNode` | Node in the game tree: label, MAX/MIN flag, children list, leaf value. |
| `alphabeta()` | Recursive Minimax + Alpha-Beta pruning; returns the minimax value from a given node. |

---

## `unit4_knowledge.py` — Knowledge Representation & Reasoning

### Libraries / Frameworks
None — pure Python.

### Algorithms
| Algorithm | Description |
|---|---|
| **Forward Chaining** | Data-driven inference; starts from known facts and repeatedly fires IF-THEN rules until no new conclusions can be drawn. |
| **Expected Utility (EU)** | `EU(a) = Σ P(outcome) × U(outcome)` — probabilistic decision-making under uncertainty. |

### Key Concepts
- **Propositional logic** — facts as strings; rules as `(conditions_set → conclusion)` pairs.
- **Predicate logic matching** — subset check (`conditions ⊆ facts`) triggers rule firing.
- **Semantic networks** — object-attribute knowledge encoded as named frames with typed slots.
- **Frame representation** — `Frame` stores slot/value pairs (e.g., `is_a`, `diameter`, `risk_level`).
- **Uncertain reasoning** — outcomes assigned probabilities; agent selects action with highest EU.
- **Knowledge-based agent** architecture (`tell` / `infer` API).

### Classes & Functions
| Name | Role |
|---|---|
| `Frame` | Knowledge frame with a name and a dictionary of slots (attribute → value). |
| `KnowledgeBase` | Manages facts (set) and rules (list of tuples); provides `tell()`, `add_rule()`, and `infer()`. |
| `KnowledgeBase.tell()` | Asserts a new propositional fact. |
| `KnowledgeBase.add_rule()` | Registers an IF-THEN rule. |
| `KnowledgeBase.infer()` | Forward chaining engine; iterates until no new facts are derived. |
| `UtilityBasedAgent` | Computes expected utility for actions given outcome probabilities and utility values. |

#### Forward Chaining Example (from `__main__`)
```
Facts added : Risk_Critical, Time_Short
Rule 1 fires: {Risk_Critical, Time_Short} → Require_High_Yield
Rule 2 fires: {Require_High_Yield}        → Dispatch_Nuclear_Missile
```

---

## Data Structures Used (across all files)

| Structure | Where used |
|---|---|
| `deque` | BFS frontier (unit1_2) |
| Min-heap (`heapq`) | A* frontier (unit1_2) |
| `list` | Children nodes, rules, explored sequences |
| `dict` | Action costs, domains, frame slots, utility values |
| `set` | KB facts, rule condition sets |
| Tree (via object refs) | Game tree (unit3) |
| Tuple | Rules stored as `(conditions_set, conclusion)` pairs (unit4) |

---

## Unifying Theme

All three files model the same real-world problem — **choosing an asteroid mitigation strategy** — at increasing levels of intelligence:

1. **Unit 1-2** searches for the strategy with the lowest combined path + heuristic cost.  
2. **Unit 3** models the selection as a game against an adversarial nature and enforces budget constraints.  
3. **Unit 4** encodes domain knowledge as logic rules and computes the statistically best action under uncertainty.
