from typing import Any, Dict, Set, Tuple, List
from problem import Problem
from mathutils import Direction, Point
from helpers.utils import NotImplemented

# TODO: (Optional) Instead of Any, you can define a type for the parking state
# Define the state of the parking to be a map for each car and its corrosponding location in the parking area, to keep track as we go the location of each car in the map
ParkingState = Dict[int, Point]

# An action of the parking problem is a tuple containing an index 'i' and a direction 'd' where car 'i' should move in the direction 'd'.
ParkingAction = Tuple[int, Direction]


# This is the implementation of the parking problem
class ParkingProblem(Problem[ParkingState, ParkingAction]):
    passages: Set[
        Point
    ]  # A set of points which indicate where a car can be (in other words, every position except walls).
    cars: Tuple[Point]  # A tuple of points where state[i] is the position of car 'i'.
    slots: Dict[
        Point, int
    ]  # A dictionary which indicate the index of the parking slot (if it is 'i' then it is the slot of car 'i') for every position.
    # if a position does not contain a parking slot, it will not be in this dictionary.
    width: int  # The width of the parking slot.
    height: int  # The height of the parking slot.

    # This function should return the initial state
    def get_initial_state(self) -> ParkingState:
        # TODO: ADD YOUR CODE HERE

        # Initially, I would define for each car their location in the parking area (COMMON SENSE ^_^)
        return {i: self.cars[i] for i in range(len(self.cars))}

    # This function should return True if the given state is a goal. Otherwise, it should return False.
    def is_goal(self, state: ParkingState) -> bool:
        # TODO: ADD YOUR CODE HERE

        # Let's loop across each car and check if the position of the car exists in the predefined parking slots, and if so. We want to check that the car is the owner of this slot
        # as if A is at B's slot, so this is not its goal state, so the whole goal state fails :(
        for car, position in state.items():
            slot_owner = self.slots.get(position)
            if slot_owner != car:
                return False
        return True

    # This function returns a list of all the possible actions that can be applied to the given state
    def get_actions(self, state: ParkingState) -> List[ParkingAction]:
        # TODO: ADD YOUR CODE HERE

        # Define our availaible actions' type
        actions: List[ParkingAction] = []

        # Build a set of all occupied positions (to prevent collisions)
        occupied_positions = {pos for pos in state.values()}

        # Try moving each car
        for car, position in state.items():
            for direction in Direction:
                # Compute the next position in that direction
                next_pos = position + direction.to_vector()

                # Check if the move is legal that this move is from one of the defined free slots and not another car to be in the same slot (collision protection)
                if next_pos in self.passages and next_pos not in occupied_positions:
                    actions.append((car, direction))

        return actions

    # This function returns a new state which is the result of applying the given action to the given state
    def get_successor(self, state: ParkingState, action: ParkingAction) -> ParkingState:
        # TODO: ADD YOUR CODE HERE

        # Get rhe direction, and the car to be moved in this direction
        car, direction = action

        # Update our state thus the value of state[car] is the new point the car would be placed in, so we need to move the car from the old point to the point in the direction needed
        state[car] = state[car] + direction.to_vector()

        # Return the new state
        return state

    # This function returns the cost of applying the given action to the given state
    def get_cost(self, state: ParkingState, action: ParkingAction) -> float:
        # TODO: ADD YOUR CODE HERE

        car, _ = action

        # Since, the cars are 0-indexed, so we need to define the costs like this: Car_A -> index=0 -> cost=26, Car_B -> index=1 -> cost=25 and so on ....
        return 26 - car

    # Read a parking problem from text containing a grid of tiles
    @staticmethod
    def from_text(text: str) -> "ParkingProblem":
        passages = set()
        cars, slots = {}, {}
        lines = [line for line in (line.strip() for line in text.splitlines()) if line]
        width, height = max(len(line) for line in lines), len(lines)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != "#":
                    passages.add(Point(x, y))
                    if char == ".":
                        pass
                    elif char in "ABCDEFGHIJ":
                        cars[ord(char) - ord("A")] = Point(x, y)
                    elif char in "0123456789":
                        slots[int(char)] = Point(x, y)
        problem = ParkingProblem()
        problem.passages = passages
        problem.cars = tuple(cars[i] for i in range(len(cars)))
        problem.slots = {position: index for index, position in slots.items()}
        problem.width = width
        problem.height = height
        return problem

    # Read a parking problem from file containing a grid of tiles
    @staticmethod
    def from_file(path: str) -> "ParkingProblem":
        with open(path, "r") as f:
            return ParkingProblem.from_text(f.read())
