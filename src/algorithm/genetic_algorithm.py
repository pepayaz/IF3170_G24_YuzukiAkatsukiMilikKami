from copy import deepcopy
from random import Random
from time import perf_counter

from ..models.package import Position, RotationDirection
from ..utils.initial_state import ROTATIONS, generate_population
from ..utils.evaluator import evaluate_state

def evaluate_population(population, consider_eta: bool = False):
    evaluated_population = []

    for state in population:
        individual = {
            "state": state,
            "evaluation": evaluate_state(state, consider_eta)
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


def create_next_generation(evaluated_population, mutation_rate, rng, consider_eta: bool = False):
    if not evaluated_population:
        raise ValueError("Populasi tidak boleh kosong")

    next_population = []
    population_size = len(evaluated_population)

    while len(next_population) < population_size:
        parent_1 = roulette_selection(evaluated_population, rng)
        parent_2 = roulette_selection(evaluated_population, rng)
        child = crossover(parent_1, parent_2, rng)
        child = mutate(child, mutation_rate, rng)
        next_population.append({
            "state": child,
            "evaluation": evaluate_state(child, consider_eta)
        })

    return next_population


def update_best_valid(best_valid, evaluated_population):
    for individual in evaluated_population:
        evaluation = individual["evaluation"]
        if not evaluation["is_valid"]:
            continue
        if best_valid is None or evaluation["value"] > best_valid["evaluation"]["value"]:
            best_valid = deepcopy(individual)

    return best_valid


def summarize_generation(evaluated_population, generation, best_valid):
    if not evaluated_population:
        raise ValueError("Populasi tidak boleh kosong")

    first = evaluated_population[0]["evaluation"]
    max_fitness = first["state_value"]
    max_value = first["value"]
    total_fitness = 0
    total_value = 0
    valid_count = 0

    for individual in evaluated_population:
        evaluation = individual["evaluation"]
        fitness = evaluation["state_value"]
        value = evaluation["value"]
        total_fitness += fitness
        total_value += value

        if fitness > max_fitness:
            max_fitness = fitness
        if value > max_value:
            max_value = value
        if evaluation["is_valid"]:
            valid_count += 1

    best_valid_value = None

    if best_valid is not None:
        best_valid_value = best_valid["evaluation"]["value"]

    population_size = len(evaluated_population)

    return {
        "generation": generation,
        "max_fitness": max_fitness,
        "mean_fitness": total_fitness / population_size,
        "max_value": max_value,
        "mean_value": total_value / population_size,
        "valid_count": valid_count,
        "best_valid_value": best_valid_value
    }


def run_ga(problem, population_size=20, generation_count=100, mutation_rate=0.2, seed=None, load_probability=0.5, consider_eta=False):
    if type(generation_count) is not int or generation_count < 0:
        raise ValueError("Generation count harus berupa bilangan bulat nonnegatif")
    
    if type(mutation_rate) not in (int, float):
        raise ValueError("Mutation rate harus berupa angka antara 0 dan 1")
    
    if not 0 <= mutation_rate <= 1:
        raise ValueError("Mutation rate harus berada antara 0 dan 1")

    started = perf_counter()
    population = generate_population(problem, population_size=population_size, seed=seed, load_probability=load_probability)

    evaluated = evaluate_population(population, consider_eta)
    initial_population = deepcopy(evaluated)
    best_valid = update_best_valid(None, evaluated)
    history = [summarize_generation(evaluated, 0, best_valid)]

    evolution_seed = None

    if seed is not None:
        evolution_seed = seed + 1
        
    rng = Random(evolution_seed)

    for generation in range(1, generation_count + 1):
        evaluated = create_next_generation(evaluated, mutation_rate, rng, consider_eta)
        best_valid = update_best_valid(best_valid, evaluated)
        history.append(summarize_generation(evaluated, generation, best_valid))

    best_individual = deepcopy(find_best_individual(evaluated))
    duration = perf_counter() - started

    return {
        "initial_population": initial_population,
        "final_population": evaluated,
        "best_individual": best_individual,
        "best_valid": best_valid,
        "history": history,
        "duration_seconds": duration,
        "parameters": {
            "population_size": population_size,
            "generation_count": generation_count,
            "mutation_rate": mutation_rate,
            "seed": seed,
            "evolution_seed": evolution_seed,
            "load_probability": load_probability,
            "consider_eta": consider_eta,
            "selection": "roulette",
            "crossover": "one_point",
            "elitism": False,
            "negative_fitness_weights": "fitness - minimum + 1 when minimum < 0"
        }
    }
