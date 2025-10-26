from __future__ import annotations
from collections import deque, defaultdict
from itertools import product
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Any
import argparse
import sys

State = Tuple[int, ...]
Move = Tuple[int, int, int]
Step = Tuple[State, State, Move]

def validate_inputs(caps: Sequence[int], start: Sequence[int]) -> None:
	if len(caps) != len(start):
		raise ValueError("capacitites and start must have same amount of jugs")
	if any(c <= 0 for c in caps):
		raise ValueError("capacities must be positive integers.")
	if any(a < 0 for a in start):
		raise ValueError("start amounts must be positive integers")
	if any(a > c for a,c in zip(start, caps)):
		raise ValueError("start amount cant exceed jug capacity")

def pour(state: State, caps: Sequence[int], i: int, j: int) -> Optional[Tuple[State,int]]:
	if i == j:
		return None
	amounts = list(state)
	if amounts[i] == 0 or amounts[j] == caps[j]:
		return None
	space = caps[j] - amounts[j]
	moved = min(amounts[i], space)
	amounts[i] -= moved
	amounts[j] += moved
	return tuple(amounts), moved

def all_shortest_paths(
	caps: Sequence[int],
	start: Sequence[int],
	goal_fn: Callable[[State], bool],
) -> Tuple[List[List[Step]], Dict[State, int], Dict[State, List[Tuple[State, Move]]]]:

	# BFS to find all shortest pour sequences

	validate_inputs(caps, start)
	start_state: State = tuple(int(x) for x in start)

	q = deque([start_state])
	dist: Dict[State, int] = {start_state: 0}
	parents: Dict[State, List[Tuple[State, Move]]] = defaultdict(list)

	found_goal_dist: Optional[int] = None
	goals: set[State] = set()

	n = len(caps)
	while q:
		s = q.popleft()
		d = dist[s]

		# stop expanding once we found a goal level
		# this isnt minecraft, we dont need to go deeper
		if found_goal_dist is not None and d >= found_goal_dist:
			continue

		# generate all single pours
		for i, j in product(range(n), range(n)):
			res = pour(s, caps, i, j)
			if res is None:
				continue
			ns, moved = res
			mv: Move = (i, j, moved)

			if ns not in dist:
				dist[ns] = d + 1
				parents[ns].append((s, mv))
				q.append(ns)
			else:
				# if theres another way to reach ns, keep it
				if dist[ns] == d + 1:
					parents[ns].append((s, mv))

		# check wtf we're trying to accomplish (for capturing dist level correctly)
		if goal_fn(s):
			found_goal_dist = dist[s]
			goals.add(s)
	# lol
	if not goals:
		return [], dist, parents

	# reconstruct shortest paths
	all_paths: List[List[Step]] = []

	def backtrack(s: State, path: List[Step]) -> None:
		if s == start_state:
			all_paths.append(list(reversed(path)))
			return
		for p, mv in parents[s]:
			backtrack(p, path + [(p, s, mv)])

	for g in goals:
		backtrack(g, [])

	all_paths.sort(key=lambda steps: [mv for (_, _, mv) in steps])
	return all_paths, dist, parents

def default_jug_names(n: int) -> List[str]:
	return [f"J{i}" for i in range(n)]

def pretty_state(state: State, names: Optional[Sequence[str]] = None, caps: Optional[Sequence[int]] = None) -> str:
	parts = []
	for idx, amt in enumerate(state):
		label = (names[idx] if names else f"J{idx}")
		if caps:
			parts.append(f"{label}:{amt}/{caps[idx]}")
		else:
			parts.append(f"{label}:{amt}")
	return "(" + ", ".join(parts) + ")"

def pretty_move(step: Step, names: Optional[Sequence[str]] = None) -> str:
	s, ns, (i, j, moved) = step
	ni = (names[i] if names else f"J{i}")
	nj = (names[j] if names else f"J{j}")
	return f"pour {ni} -> {nj} ({moved}): {s} -> {ns}"

# ---------- CLI stuff ----------
def parse_csv_ints(s: str) -> List[int]:
	try:
		return [int(x.strip()) for x in s.split(",") if x.strip() != ""]
	except ValueError:
		raise argparse.ArgumentTypeError("Expected comma-separated integers.")

def goal_exact_amount_in_jug(jug_index: int, amount: int) -> Callable[[State], bool]:
	return lambda st: st[jug_index] == amount

# ---------- main ----------
def main(argv: Optional[List[str]] = None) -> int:
	p = argparse.ArgumentParser(description="Find all shortest pour sequnces for water jug puzzles.")
	p.add_argument("--caps", required=True, type=parse_csv_ints, help="Comma-separated capacities, e.g., 10,7,4")
	p.add_argument("--start", required=True, type=parse_csv_ints, help="Comma-separated start amounts, e.g., 0,7,4")
	p.add_argument("--goal-jug", type=int, default=None, help="Index (0-based) of the jug to target for amount goal.")
	p.add_argument("--goal-amount", type=int, default=None, help="Exact amount required in --goal-jug.")
	p.add_argument("--names", type=str, default=None, help="Optional comma-separated jug names (for pretty prints), e.g., 10L,7L,4L")
	args = p.parse_args(argv)

	# now the real fun
	caps = args.caps
	start = args.start
	names = args.names.split(",") if args.names else None
	if names and len(names) != len(caps):
		p.error("If --names is provided, it must have the same length as --caps.")

	# build goal func
	if args.goal_jug is not None and args.goal_amount is not None:
		gj = args.goal_jug
		ga = args.goal_amount
		if gj < 0 or gj >= len(caps):
			p.error("--goal-jug out of range.")
		if ga < 0 or ga > caps[gj]:
			p.errpr("--goal-amount must be between 0 and the capacity of target jug.")
		goal_fn = goal_exact_amount_in_jug(gj, ga)
		goal_desc = f"{names[gj] if names else f'J{gj}'} == {ga}"
	else:
		p.error("Must provide both --goal-jug and --goal-amount for the CLI.")

	# drive
	paths, dist, parents = all_shortest_paths(caps, start, goal_fn)

	# pretty print
	label_names = names if names else default_jug_names(len(caps))
	start_state = tuple(start)
	print(f"Capacities:\t{caps}")
	print(f"Start:\t\t{pretty_state(start_state, label_names, caps)}")
	print(f"Goal:\t\t{goal_desc}\n")

	if not paths:
		print("No solution found that satisfies the goal.")
		return 0

	shortest_len = len(paths[0])
	print(f"Shortest solution length: {shortest_len} pour(s)")
	print(f"Number of distinct shortest solutions: {len(paths)}\n")

	for k, steps in enumerate(paths, 1):
		print(f"Solution {k}:")
		# format states inside steps into pretty strings
		for s, ns, mv in steps:
			s_str = pretty_state(s, label_names, caps)
			ns_str = pretty_state(ns, label_names, caps)
			i, j, moved = mv
			print(f"  pour {label_names[i]} -> {label_names[j]} ({moved}): {s_str} -> {ns_str}")
		final_state = steps[-1][1]
		print(f"  Reached goal state: {pretty_state(final_state, label_names, caps)}\n")
	return 0

# ---------- Library-style entry point ----------

def solve_water_jugs(
	capacities: Sequence[int],
	start_amounts: Sequence[int],
	goal_fn: Callable[[State], bool],
	jug_names: Optional[Sequence[str]] = None,
) -> List[List[Step]]:
	paths, _, _ = all_shortest_paths(capacities, start_amounts, goal_fn)
	return paths

if __name__ == "__main__":
	sys.exit(main())
