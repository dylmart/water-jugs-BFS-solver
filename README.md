# Water Jug Problem Solver (Python)

A Python program that finds **all shortest solutions** to classic water jug puzzles using **Breadth-First Search (BFS)**.

Given any set of jug capacities, starting amounts, and a goal condition, the program explores every valid pour operation and outputs all minimal sequences of steps that reach the target state.

---
## Features
- Finds all shortest pour sequences (not just one)
- Works with any number of jugs
- Command line interface
- Detects unsolvable puzzles
---
## Usage
### Command Line
```python
python3 water_jugs.py --caps <capacities> --start <start_amounts> --goal-jug <index> --goal-amount <liters> [--names <labels>]
```
### As a Python Library
```python
from water_jugs import solve_water_jugs, goal_exact_amount_in_jug

caps = (10, 7, 4)
start = (0, 7, 4)
goal = goal_exact_amount_in_jug(2, 2)

paths = solve_water_jugs(caps, start, goal)
print(f"{len(paths)} shortest solutions found!")
```
---
## Requirements
- Python 3.6+
- No external dependencies
---
## Example Problem
> You have a 10L, 7L, and 4L jug.  
> The 7L and 4L jugs start full, and the 10L jug is empty.  
> Can you leave **exactly 2 liters** in the 4L jug?  

Run it like this:
```python
python3 water_jugs.py --caps 10,7,4 --start 0,7,4 --goal-jug 2 --goal-amount 2 --names 10L,7L,4L
```
Output:
```
Shortest solution length: 6 pour(s)
Number of distinct shortest solutions: 1

Solution 1:
  pour 4L → 10L (4): (10:0, 7:7, 4:4) → (10:4, 7:7, 4:0)
  pour 7L → 10L (6): (10:4, 7:7, 4:0) → (10:10, 7:1, 4:0)
  pour 10L → 4L (4): (10:10, 7:1, 4:0) → (10:6, 7:1, 4:4)
  pour 4L → 7L (4): (10:6, 7:1, 4:4) → (10:6, 7:5, 4:0)
  pour 10L → 4L (4): (10:6, 7:5, 4:0) → (10:2, 7:5, 4:4)
  pour 4L → 7L (2): (10:2, 7:5, 4:4) → (10:2, 7:7, 4:2)
```
