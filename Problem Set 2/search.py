from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

# TODO: Import any modules you want to use

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state)

# All the search functions should return the expected tree value and the best action to take based on the search results


# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(
    game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1
) -> Tuple[float, A]:
    agent = game.get_turn(state)

    terminal, values = game.is_terminal(state)
    if terminal:
        return values[agent], None

    actions_states = [
        (action, game.get_successor(state, action))
        for action in game.get_actions(state)
    ]
    value, _, action = max(
        (heuristic(game, state, agent), -index, action)
        for index, (action, state) in enumerate(actions_states)
    )
    return value, action


# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(
    game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1
) -> Tuple[float, A]:
    terminal, values = game.is_terminal(state)
    if terminal:
        return values[0], None  # rturn player 0's value with no action
    if max_depth != -1 and max_depth == 0:
        return heuristic(game, state, 0), None  # cutoff at max_depth
    turn = game.get_turn(state)
    actions = list(game.get_actions(state))

    best_val = float("inf")
    best_action: A | None = None

    if turn == 0:  # max node (player 0)
        best_val = -best_val
        for action in actions:
            succ = game.get_successor(
                state, action
            )  # get successor state for current action for the next level
            val, _ = minimax(
                game,
                succ,
                heuristic,
                (
                    max_depth - 1 if max_depth != -1 else -1
                ),  # decrease depth for next level
            )
            if (
                val > best_val
            ):  # update best value and action for max node to maximize player 0's value
                best_val = val
                best_action = action
        return best_val, best_action

    # min node (enemies: turn > 0)
    for action in actions:
        succ = game.get_successor(state, action)
        val, _ = minimax(
            game, succ, heuristic, max_depth - 1 if max_depth != -1 else -1
        )
        if (
            val < best_val
        ):  # update best value and action for min node to minimize player 0's value
            best_val = val
            best_action = action
    return best_val, best_action


# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(
    game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1
) -> Tuple[float, A]:
    import math

    # recursive helper: returns (value_for_player0, best_action_from_this_state) through exploring different states
    def helper(s: S, depth: int, alpha: float, beta: float) -> Tuple[float, A]:
        terminal, values = game.is_terminal(s)
        # if terminal state -> return the player(0) value
        if terminal:
            return values[0], None

        # depth cutoff (max_depth == -1 means no cutoff)
        if max_depth != -1 and depth >= max_depth:
            # evaluate from player 0's perspective at cutoff
            return heuristic(game, s, 0), None

        # get turn and actions for current state
        turn = game.get_turn(s)
        actions = list(game.get_actions(s))

        # max node (player 0)
        if turn == 0:
            best_val = -math.inf
            best_action: A | None = None
            for action in actions:
                succ = game.get_successor(s, action)
                val, _ = helper(succ, depth + 1, alpha, beta)
                if val > best_val:
                    best_val = val
                    best_action = action
                alpha = max(alpha, best_val)
                if beta <= alpha:
                    break  # beta cutoff
            return best_val, best_action

        # min node (enemies: turn > 0) - minimize the value for player 0
        else:
            best_val = math.inf
            best_action: A | None = None
            for action in actions:
                succ = game.get_successor(s, action)
                val, _ = helper(succ, depth + 1, alpha, beta)
                if val < best_val:
                    best_val = val
                    best_action = action
                beta = min(beta, best_val)
                if beta <= alpha:
                    break  # alpha cutoff
            return best_val, best_action

    value, action = helper(state, 0, -float("inf"), float("inf"))
    return value, action


# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(
    game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1
) -> Tuple[float, A]:
    import math
    from typing import List, Tuple

    def helper(s: S, depth: int, alpha: float, beta: float) -> Tuple[float, A]:
        terminal, values = game.is_terminal(s)
        if terminal:
            return values[0], None

        if max_depth != -1 and depth >= max_depth:
            return heuristic(game, s, 0), None

        turn = game.get_turn(s)
        actions = list(game.get_actions(s))

        # Prepare move ordering: compute heuristic value for successor states
        # Use enumerate to preserve original order for stable tie-breaking
        ordered: List[Tuple[int, A, S, float]] = []
        for idx, action in enumerate(actions):
            succ = game.get_successor(s, action)
            # use player-0 perspective for ordering heuristic
            hval = heuristic(game, succ, 0)
            ordered.append((idx, action, succ, hval))

        # sort: for max node (player 0) descending heuristic, for min node ascending heuristic
        if turn == 0:
            ordered.sort(key=lambda t: (-t[3], t[0]))  # higher h first, stable by idx
        else:
            ordered.sort(key=lambda t: (t[3], t[0]))  # lower h first, stable by idx

        if turn == 0:
            best_val = -math.inf
            best_action: A | None = None
            for _, action, succ, _ in ordered:
                val, _ = helper(succ, depth + 1, alpha, beta)
                if val > best_val:
                    best_val = val
                    best_action = action
                alpha = max(alpha, best_val)
                if beta <= alpha:
                    break
            return best_val, best_action
        else:
            best_val = math.inf
            best_action: A | None = None
            for _, action, succ, _ in ordered:
                val, _ = helper(succ, depth + 1, alpha, beta)
                if val < best_val:
                    best_val = val
                    best_action = action
                beta = min(beta, best_val)
                if beta <= alpha:
                    break
            return best_val, best_action

    value, action = helper(state, 0, -float("inf"), float("inf"))
    return value, action


# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(
    game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1
) -> Tuple[float, A]:
    terminal, values = game.is_terminal(state)
    if terminal:
        return values[0], None  # return player 0's value with no action

    if max_depth != -1 and max_depth == 0:
        return heuristic(game, state, 0), None  # cutoff at max_depth

    # get turn and actions for current state
    turn = game.get_turn(state)
    actions = list(game.get_actions(state))

    best_val = float("inf")
    best_action: A | None = None
    if turn == 0:  # max node (player 0)
        best_val = -best_val
        for action in actions:
            succ = game.get_successor(
                state, action
            )  # get successor state for current action for the next level
            val, _ = expectimax(
                game,
                succ,
                heuristic,
                (
                    max_depth - 1 if max_depth != -1 else -1
                ),  # decrease depth for next level
            )
            if (
                val > best_val
            ):  # update best value and action for max node to maximize player 0's value
                best_val = val
                best_action = action
        return best_val, best_action

    # chance node (enemies: turn > 0) - average the values for player 0
    total_val = 0.0
    for action in actions:
        succ = game.get_successor(state, action)
        val, _ = expectimax(
            game,
            succ,
            heuristic,
            max_depth - 1 if max_depth != -1 else -1,  # decrease depth for next level
        )
        total_val += val
    average_val = (
        total_val / len(actions) if actions else 0.0
    )  # avoid division by zero otherwise average the values over actions for expectation to player 0
    return average_val, None
