from copy import deepcopy

from ..models.package import Position, RotationDirection
from ..utils.initial_state import ROTATIONS
from ..utils.evaluator import evaluate_state

def evaluate_population(population):
    evaluated_population = []

    for state in population:
        individual = {
            "state": state,
            "evaluation": evaluate_state(state)
        }
        evaluated_population.append(individual)

    return evaluated_population


def find_best_individual(evaluated_population):
    if not evaluated_population:
        raise ValueError("Populasi tidak boleh kosong")

    best = evaluated_population[0]

    for individual in evaluated_population:
        fitness = individual["evaluation"]["state_value"]
        best_fitness = best["evaluation"]["state_value"]
        if fitness > best_fitness:
            best = individual

    return best


def selection_weights(evaluated_population):
    if not evaluated_population:
        raise ValueError("Populasi tidak boleh kosong")

    minimum = evaluated_population[0]["evaluation"]["state_value"]

    for individual in evaluated_population:
        fitness = individual["evaluation"]["state_value"]
        if fitness < minimum:
            minimum = fitness

    weights = []

    for individual in evaluated_population:
        fitness = individual["evaluation"]["state_value"]
        if minimum < 0:
            weight = fitness - minimum + 1
        else:
            weight = fitness
        weights.append(weight)

    return weights


def roulette_selection(evaluated_population, rng):
    weights = selection_weights(evaluated_population)
    total_weight = sum(weights)

    if total_weight == 0:
        return rng.choice(evaluated_population)

    target = rng.random() * total_weight
    cumulative = 0

    for index in range(len(evaluated_population)):
        cumulative += weights[index]
        if target < cumulative:
            return evaluated_population[index]

    for index in range(len(weights) - 1, -1, -1):
        if weights[index] > 0:
            return evaluated_population[index]


def check_parents(state_1, state_2):
    if state_1.truck != state_2.truck:
        raise ValueError("Truk kedua induk harus sama")
    
    if len(state_1.packages) != len(state_2.packages):
        raise ValueError("Jumlah paket kedua induk harus sama")

    for index in range(len(state_1.packages)):
        first = state_1.packages[index]
        second = state_2.packages[index]

        first_data = (first.id, first.dimension, first.value, first.weight, first.is_fragile, first.eta)

        second_data = (second.id, second.dimension, second.value, second.weight, second.is_fragile, second.eta)

        if first_data != second_data:
            raise ValueError("Data dan urutan paket kedua induk harus sama")


def crossover(parent_1, parent_2, rng):
    state_1 = parent_1["state"]
    state_2 = parent_2["state"]

    check_parents(state_1, state_2)
    package_count = len(state_1.packages)

    if package_count < 2:
        return rng.choice([state_1, state_2]).clone()

    cut = rng.randint(1, package_count - 1)
    child = state_1.clone()

    for index in range(package_count):
        if index < cut:
            source = state_1.packages[index]

        else:
            source = state_2.packages[index]

        child.packages[index].position = deepcopy(source.position)
        child.packages[index].orientation = deepcopy(source.orientation)

    child.rebuild()

    return child


def mutate(child_state, mutation_rate, rng):
    if type(mutation_rate) not in (int, float):
        raise ValueError("Mutation rate harus berupa angka antara 0 dan 1")
    
    if not 0 <= mutation_rate <= 1:
        raise ValueError("Mutation rate harus berada antara 0 dan 1")

    mutated = child_state.clone()

    if not mutated.packages:
        return mutated
    
    if rng.random() >= mutation_rate:
        return mutated

    package = rng.choice(mutated.packages)

    if package.position is None:
        package.orientation = deepcopy(rng.choice(ROTATIONS))
        dimension = mutated.truck.dimension
        package.position = Position(rng.randint(0, dimension.w - 1), rng.randint(0, dimension.l - 1), rng.randint(0, dimension.h - 1))
    
    else:
        operation = rng.choice(["move", "rotate", "remove"])

        if operation == "move":
            axis = rng.choice(["x", "y", "z"])
            distance = rng.choice([-1, 1])
            if axis == "x":
                package.position.x += distance
            elif axis == "y":
                package.position.y += distance
            else:
                package.position.z += distance

        elif operation == "rotate":
            axis = rng.choice(["x", "y", "z"])
            direction = rng.choice([RotationDirection.POSITIVE, RotationDirection.NEGATIVE])
            if axis == "x":
                package.rotate_x(direction)
            elif axis == "y":
                package.rotate_y(direction)
            else:
                package.rotate_z(direction)

        else:
            package.move(None)

    mutated.rebuild()

    return mutated
