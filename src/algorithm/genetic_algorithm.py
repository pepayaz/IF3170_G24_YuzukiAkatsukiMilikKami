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
