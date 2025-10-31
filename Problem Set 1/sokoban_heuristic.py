import copy
import math
from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1


# TODO: Import any modules and write any functions you want to use


def precompute_goals_distances(problem: SokobanProblem):
    dict = {}
    for goal in problem.layout.goals:
        visited = set()
        queue = [(goal, 0)]
        distances = {}
        while queue:
            cur, dist = queue.pop(0)
            if cur in visited:
                continue
            visited.add(cur)
            distances[cur] = dist
            for direction in Direction:
                neighbor = cur + direction.to_vector()
                play = neighbor + direction.to_vector()

                if (play in problem.layout.walkable and neighbor in problem.layout.walkable and neighbor not in visited):
                    queue.append((neighbor, dist + 1))
        dict[goal] = distances
    return dict


def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    crates = list(state.crates)
    n = len(crates)
    goals = list(problem.layout.goals)

    cache = problem.cache()

    if "precompute" not in cache:
        cache["precompute"] = precompute_goals_distances(problem)

    dict = cache["precompute"]

    
    dp = [math.inf] * (1 << n)
    dp[0] = 0

    for mask in range(1 << n):
        i = bin(mask).count("1")  
        if i == n:
            continue

        for j in range(n):
            if crates[j] not in dict[goals[i]]:
                continue
            if not (mask & (1 << j)):
                new_mask = mask | (1 << j)
                dp[new_mask] = min(dp[new_mask], dp[mask] + dict[goals[i]][crates[j]])

    return float(dp[(1 << n) - 1])