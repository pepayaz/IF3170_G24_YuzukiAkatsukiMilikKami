from __future__ import annotations
import random
import math

from ..models.problem import ProblemState, Problem
from ..utils.action import generate_random_successor
from ..utils.evaluator import evaluate_state

TEMPERATURE_INITIAL = 1000
TEMPERATURE_DECREASE = 1

def run_simulated_annealing(problem: Problem, iteration_amount: int):
    results = []

    for i in range(iteration_amount):
        init_state: ProblemState
        #build init state

        results.append(search_simulated_annealing(init_state))

    #output


def search_simulated_annealing(state: ProblemState):
    plot_objective: dict[int, int] = {} # [iteration, state_value]
    plot_probability: dict[int, float] = {} # [iteration, probability]
    iteration = 0
    t = TEMPERATURE_INITIAL

    while (t > 0):
        successor = generate_random_successor(state)

        state_value = evaluate_state(state)["state_value"]
        successor_value = evaluate_state(successor)["state_value"]

        # Tentukan apakah successor akan dipilih
        choose_successor: bool = False
        if successor_value > state_value:
            choose_successor = True
        else:
            probability = _count_probability(state_value, successor_value, t)
            random_value = random.random()
            if probability > random_value:
                choose_successor = True

        if choose_successor:
            state = successor

        iteration += 1
        t -= TEMPERATURE_DECREASE


    result = {
        'iteration': iteration,
        #etc
    }

    return result

def _count_probability(state_value: ProblemState, successor_value: ProblemState, t: int) -> float:
    d_e = successor_value - state_value

    return math.exp(d_e/t)