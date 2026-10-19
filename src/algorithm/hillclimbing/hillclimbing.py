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
        raise RuntimeError(f"Invalid Hill Climbing Variant: {variant}")

def steepest_ascent(state: ProblemState) -> dict: 
    current: ProblemState = state
    all_states = [evaluate_state(current)["state_value"]]
    iteration = 0
    result = {}
    
    while True:
        all_successor = generate_all_successor(current)

        if len(all_successor) == 0:
            result["current"] = current
            result["all_states"] = all_states
            result["iteration"] = iteration
            return result
        
        best_neighbour: ProblemState = all_successor[0]
        best_value: int = evaluate_state(best_neighbour)["state_value"]

        for successor in all_successor:
            successor_value = evaluate_state(successor)["state_value"]

            if best_value < successor_value:
                best_neighbour = successor
                best_value = successor_value

        current_value = evaluate_state(current)["state_value"]

        if best_value <= current_value:
            result["current"] = current
            result["all_states"] = all_states
            result["iteration"] = iteration
            return result
        
        current = best_neighbour
        all_states.append(best_value)
        iteration += 1

def sideways_move(state: ProblemState, max_sideways_move):
    current: ProblemState = state
    count_sideways = 0
    iteration = 0
    all_states = [evaluate_state(current)["state_value"]]
    result = {}

    while True:
        all_successor = generate_all_successor(current)
        current_value = evaluate_state(current)["state_value"]

        if len(all_successor) == 0:
            result["current"] = current
            result["all_states"] = all_states
            result["iteration"] = iteration
            result["sideways_move"] = count_sideways
            result["max_sideways"] = max_sideways_move
            return result
        
        best_neighbour: ProblemState = all_successor[0]
        best_value: int = evaluate_state(best_neighbour)["state_value"]

        for successor in all_successor:
            successor_value = evaluate_state(successor)["state_value"]

            if best_value < successor_value:
                best_neighbour = successor
                best_value = successor_value

        if best_value < current_value:
            result["current"] = current
            result["all_states"] = all_states
            result["iteration"] = iteration
            result["sideways_move"] = count_sideways
            result["max_sideways"] = max_sideways_move
            return result

        if best_value == current_value:
            if count_sideways >= max_sideways_move:
                result["current"] = current
                result["all_states"] = all_states
                result["iteration"] = iteration
                result["sideways_move"] = count_sideways
                result["max_sideways"] = max_sideways_move
                return result

            count_sideways += 1

        current = best_neighbour
        all_states.append(best_value)
        iteration += 1

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
    all_states = [evaluate_state(current)["state_value"]]
    result = {}

    while count_iteration < max_iteration:
        successor = generate_random_successor(current)
        
        successor_value = evaluate_state(successor)["state_value"]
        current_value = evaluate_state(current)["state_value"]

        if current_value < successor_value:
            current = successor

        all_states.append(successor)
        count_iteration += 1

    result["current"] = current
    result["all_states"] = all_states
    result["iteration"] = count_iteration
    return current