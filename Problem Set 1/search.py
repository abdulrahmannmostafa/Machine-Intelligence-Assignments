from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

# TODO: Import any modules you want to use
from typing import Deque, Set, List, Tuple, Dict
import heapq

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution


def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    # TODO: ADD YOUR CODE HERE

    # Initially, check that if the initial state is the goal state, then why should we do more redundant work to retain it. BE QUICK .. TIME IS AN ASSET
    if problem.is_goal(initial_state):
        return []

    # Define the data structure which we could track the node to be explored, and also store for each node its actions that result to reach it
    # If we don't make this and we have just a global list of actions, then we'd push every possible action to discover our nodes. This is not what we want.
    # What we actually need is when we reach the target we return the path of actions to reach it ONLY.
    frontier: Deque[Tuple[S, List[A]]] = deque([(initial_state, [])])

    # Define a set, which we could have a prior knowledge for which states are visited in the shortest levels, hence any cycle to a previsited node would not be an optimal
    # solution because it would come from a shallower depth, and this is not our aim. We need to reach the nearest goal state optimally with the shprtest possible path
    explored_set: Set[S] = set()

    while True:
        if (
            len(frontier) == 0
        ):  # What if our search space is ended and we still did not return ?! DEAD END -> NO GOAL EXISTS
            return None

        # Pop-out from the frontier the upcoming node, in our level to be expanded
        state, path = frontier.popleft()

        # Push it to the explored set, since it is popped, it is reached from a near level from the initial state, and our search space is a space graph for that
        # we don not revisit our pre visited nodes.
        explored_set.add(state)

        # Based-on the available actions from our current node, we need to expand the corrosponding child node
        for action in problem.get_actions(state):
            # Get the child node from the previous state, with the action required
            child = problem.get_successor(state, action)

            # Check that this child is not visited before, and not in the waiting list (frontier) ... Don't forget -> SPACE GRAPH -> NO REVISIT
            if child not in explored_set and all(child != s for s, _ in frontier):
                new_path = path + [
                    action
                ]  # Add this action to the previoud path of actions reaching this child node

                # Check that this child is the goal, we may make this check just after we retrieve from the successor function the child node, but we could wait
                # more time to return the correct path of actions. Since, we are in a space graph search problem, for that the pre visited node is reached
                # from the shortest path, and because we don't revisit our nodes multiple times, we also could claim that if this node is the goal state
                # that there would not ever be a shorter path to reach it rather than the path I cut to reach it EVER. So, I'd return early and save this extra work
                # and we'd have a worst complexity O(b^d) rather than O(b^ (d+1)) ... Remember? TIME IS AN ASSET
                if problem.is_goal(child):
                    return new_path

                # If the child node is an ordinary node, then discover a path from it to the goal state insha'allah :))
                frontier.append((child, new_path))


def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    # Initially, check that if the initial state is the goal state, then why should we do more redundant work to retain it. BE QUICK .. TIME IS AN ASSET
    if problem.is_goal(initial_state):
        return []

    # Define the data structure which we could track the node to be explored, and also store for each node its actions that result to reach it which is a stack in here
    # and keep track also for each state its action that led to it
    frontier: List[Tuple[S, List[A]]] = list([(initial_state, [])])

    # Define a set, which we could have a prior knowledge for which states are visited in the shortest levels, hence any cycle to a previsited node would not be an optimal
    # solution because it would come from a shallower depth, and this is not our aim. We need to reach the nearest goal state optimally with the shprtest possible path
    explored_set: Set[S] = set()

    while frontier:
        # Pop-out from the frontier the upcoming node, in our level to be expanded
        state, path = frontier.pop()

        # Check that this child is the goal, we may make this check just after we retrieve from the successor function the child node
        if problem.is_goal(state):
            return path

        # Push it to the explored set, since it is popped, it is reached from a near level from the initial state, and our search space is a space graph for that
        # we don not revisit our pre visited nodes.
        explored_set.add(state)

        for action in problem.get_actions(state):
            # Get the child node from the previous state, with the action required
            child = problem.get_successor(state, action)

            # Just get the states in the frontier
            frontier_states = {s for s, _ in frontier}

            # Check that this child is not visited before, and not in the waiting list (frontier) ... Don't forget -> SPACE GRAPH -> NO REVISIT
            if child not in explored_set and child not in frontier_states:
                # Append to the actions of the parent the action led to expand this child
                frontier.append((child, path + [action]))

    # What if our search space is ended and we still did not return ?! DEAD END -> NO GOAL EXISTS
    return None


def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    # TODO: ADD YOUR CODE HERE
    NotImplemented()


def AStarSearch(
    problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction
) -> Solution:
    # TODO: ADD YOUR CODE HERE
    NotImplemented()


def BestFirstSearch(
    problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction
) -> Solution:
    # TODO: ADD YOUR CODE HERE
    NotImplemented()
