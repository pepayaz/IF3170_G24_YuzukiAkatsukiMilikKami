from ..utils.action import generate_all_successor, generate_random_successor
from ..models.problem import Problem, ProblemState
from ..utils.evaluator import evaluate_state
from ..utils.initial_state import generate_initial_state

from time import perf_counter

MAX_SIDEWAYS_MOVE = 10
MAX_RESTART = 10
MAX_ITERATION = 10

def run_hillclimbing(problem: Problem, variant: str, consider_eta: bool = False):
    start_time = perf_counter() 
    initial_state = generate_initial_state(problem)
    result = {}

    if variant == "steepest ascent":
        result = steepest_ascent(initial_state, consider_eta)

    elif variant == "sideways move":
        result = sideways_move(initial_state, MAX_SIDEWAYS_MOVE, consider_eta)

    elif variant == "random restart":
        result = random_restart(initial_state, MAX_RESTART, consider_eta)

    elif variant == "stochastic":
        result = stochastic(initial_state, MAX_ITERATION, consider_eta)
    
    else:
        raise RuntimeError(f"Invalid Hill Climbing Variant: {variant}")

    result["duration"] = perf_counter() - start_time
    return result

def steepest_ascent(state: ProblemState, consider_eta: bool = False) -> dict: 
    current: ProblemState = state
    all_states = [evaluate_state(current, consider_eta)["state_value"]]
    iteration = 0

    result = {}
    result["initial"] = current
    
    while True:
        all_successor = generate_all_successor(current)

        if len(all_successor) == 0:
            result["current"] = current
            result["all_states"] = all_states
            result["iteration"] = iteration
            return result
        
        best_neighbour: ProblemState = all_successor[0]
        best_value: int = evaluate_state(best_neighbour, consider_eta)["state_value"]

        for successor in all_successor:
            successor_value = evaluate_state(successor, consider_eta)["state_value"]

            if best_value < successor_value:
                best_neighbour = successor
                best_value = successor_value

        current_value = evaluate_state(current, consider_eta)["state_value"]

        if best_value <= current_value:
            result["current"] = current
            result["all_states"] = all_states
            result["iteration"] = iteration
            return result
        
        current = best_neighbour
        all_states.append(best_value)
        iteration += 1

def sideways_move(state: ProblemState, max_sideways_move, consider_eta: bool = False):
    current: ProblemState = state
    count_sideways = 0
    iteration = 0
    all_states = [evaluate_state(current, consider_eta)["state_value"]]
    
    result = {}
    result["initial"] = current

    while True:
        all_successor = generate_all_successor(current)
        current_value = evaluate_state(current, consider_eta)["state_value"]

        if len(all_successor) == 0:
            result["current"] = current
            result["all_states"] = all_states
            result["iteration"] = iteration
            result["sideways_move"] = count_sideways
            result["max_sideways"] = max_sideways_move
            return result
        
        best_neighbour: ProblemState = all_successor[0]
        best_value: int = evaluate_state(best_neighbour, consider_eta)["state_value"]

        for successor in all_successor:
            successor_value = evaluate_state(successor, consider_eta)["state_value"]

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

def random_restart(state: ProblemState, max_restart, consider_eta: bool = False): 
    best_initial = state
    best_result = steepest_ascent(best_initial, consider_eta)
    best_value = evaluate_state(best_result["current"], consider_eta)["state_value"]

    total_iteration = best_result["iteration"]
    iteration_per_restart = [best_result["iteration"]]
    objective_per_restart = [best_result["all_states"]]

    for _ in range(max_restart):
        restart_state = generate_initial_state(state.problem)
        restart_result = steepest_ascent(restart_state, consider_eta)

        restart_final = restart_result["current"]
        restart_value = evaluate_state(restart_final, consider_eta)["state_value"]

        total_iteration += restart_result["iteration"]
        iteration_per_restart.append(restart_result["iteration"])
        objective_per_restart.append(restart_result["all_states"])

        if restart_value > best_value:
            best_initial = restart_state
            best_result = restart_result
            best_value = restart_value

    best_result["initial"] = best_initial
    best_result["restart"] = max_restart
    best_result["max_restart"] = max_restart
    best_result["iteration"] = total_iteration
    best_result["iteration_per_restart"] = iteration_per_restart
    best_result["objective_per_restart"] = objective_per_restart

    return best_result

def stochastic(state: ProblemState, max_iteration, consider_eta: bool = False):
    current: ProblemState = state
    current_value = evaluate_state(current, consider_eta)["state_value"]

    count_iteration = 0
    all_states = [evaluate_state(current, consider_eta)["state_value"]]
    
    result = {}
    result["initial"] = current

    while count_iteration < max_iteration:
        successor = generate_random_successor(current)
        
        successor_value = evaluate_state(successor, consider_eta)["state_value"]

        if current_value < successor_value:
            current = successor
            current_value = successor_value

        all_states.append(current_value)
        
        count_iteration += 1

    result["current"] = current
    result["all_states"] = all_states
    result["iteration"] = count_iteration
    return result