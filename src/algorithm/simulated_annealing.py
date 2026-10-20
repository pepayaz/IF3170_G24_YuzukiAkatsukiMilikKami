from __future__ import annotations
import random
import math
from time import perf_counter

from ..models.problem import ProblemState, Problem
from ..utils.action import generate_random_successor
from ..utils.evaluator import evaluate_state
from ..utils.initial_state import generate_initial_state

TEMPERATURE_INITIAL = 100
TEMPERATURE_MINIMUM = 0.1
COOLING_RATE = 0.99

def run_simulated_annealing(problem: Problem, iteration_amount: int, consider_eta: bool = False):
    results = []

    for i in range(iteration_amount):
        init_state = generate_initial_state(problem)
        results.append(search_simulated_annealing(init_state, consider_eta))

    return results


def search_simulated_annealing(state: ProblemState, consider_eta: bool = False):
    start_time = perf_counter()
    initial_state = state
    plot_objective: dict[int, int] = {} # [iteration, state_value]
    plot_probability: dict[int, float] = {} # [iteration, probability]
    state_value = evaluate_state(state, consider_eta)["state_value"]
    best_state = state
    best_value = state_value
    plot_objective[0] = state_value
    stuck = 0
    iteration = 0
    t = TEMPERATURE_INITIAL

    while t > TEMPERATURE_MINIMUM:
        successor = generate_random_successor(state)

        successor_value = evaluate_state(successor, consider_eta)["state_value"]

        # Tentukan apakah successor akan dipilih
        choose_successor: bool = False
        probability = 1.0

        if successor_value > state_value:
            choose_successor = True
        else:
            probability = _count_probability(state_value, successor_value, t)
            random_value = random.random()
            if probability > random_value:
                choose_successor = True

        if choose_successor:
            state = successor
            state_value = successor_value

            if state_value > best_value:
                best_state = state
                best_value = state_value
        else:
            stuck += 1

        iteration += 1
        plot_objective[iteration] = state_value
        if probability == 1:
            plot_probability[iteration] = 0
        else:
            plot_probability[iteration] = probability
        t *= COOLING_RATE


    result = {
        "initial": initial_state,
        "current": best_state,
        "best_value": best_value,
        "all_states": list(plot_objective.values()),
        "probability_history": list(plot_probability.values()),
        "iteration": iteration,
        "duration": perf_counter() - start_time,
        "stuck": stuck,
    }

    return result

def _count_probability(state_value: int, successor_value: int, t: float) -> float:
    d_e = successor_value - state_value

    return math.exp(d_e/t)