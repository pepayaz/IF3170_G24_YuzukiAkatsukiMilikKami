from ...utils.action import generate_all_successor, generate_random_successor
from ...models.problem import Problem, ProblemState
from ...utils.evaluator import evaluate_state

MAX_SIDEWAYS_MOVE = 10
MAX_RESTART = 10
MAX_ITERATION = 10

def run_hillclimbing(problem: Problem, variant: str): 
    # TODO: Inital state
    if variant == "steepest ascent":
        pass
    elif variant == "sideways move":
        pass
    elif variant == "random restart":
        pass
    elif variant == "stochastic":
        pass
    else:
        pass

def steepest_ascent(state: ProblemState):
    current: ProblemState = state

    while True:
        all_successor = generate_all_successor(current)

        if len(all_successor) == 0:
            return current
        
        best_neighbour: ProblemState = all_successor[0]
        best_value: int = evaluate_state(best_neighbour)["state_value"]

        for successor in all_successor:
            successor_value = evaluate_state(successor)["state_value"]

            if best_value < successor_value:
                best_neighbour = successor
                best_value = successor_value

        current_value = evaluate_state(current)["state_value"]

        if best_value <= current_value:
            return current
        
        current = best_neighbour

def sideways_move(state: ProblemState, max_sideways_move):
    current: ProblemState = state
    count_moves = 0

    while True:
        all_successor = generate_all_successor(current)
        current_value = evaluate_state(current)["state_value"]

        if len(all_successor) == 0:
            return current
        
        best_neighbour: ProblemState = all_successor[0]
        best_value: int = evaluate_state(best_neighbour)["state_value"]

        for successor in all_successor:
            successor_value = evaluate_state(successor)["state_value"]

            if best_value < successor_value:
                best_neighbour = successor
                best_value = successor_value

        if best_value < current_value:
            return current

        if best_value == current_value:
            if count_moves >= max_sideways_move:
                return current

            count_moves += 1

        current = best_neighbour

def random_restart(state: ProblemState, max_restart): 
    # TODO: Random initial state
    current: ProblemState = state

    for _ in range(max_restart):
        final_state = steepest_ascent(state)

        final_state__value = evaluate_state(final_state)["state_value"]
        current_value = evaluate_state(current)["state_value"]

        if current_value < final_state:
            current = final_state

def stochastic(state: ProblemState, max_iteration):
    current: ProblemState = state
    count_iteration = 0

    while count_iteration < max_iteration:
        successor = generate_random_successor(current)
        
        successor_value = evaluate_state(successor)["state_value"]
        current_value = evaluate_state(current)["state_value"]

        if current_value < successor_value:
            current = successor

        count_iteration += 1

    return current