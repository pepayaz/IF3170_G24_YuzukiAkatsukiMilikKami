import json
import unittest
from pathlib import Path

from src.utils.input_loader import load_problem
from src.utils.state_builder import build_state
from src.utils.action import get_occupied_cells
from src.utils.evaluator import evaluate_state

ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases"
DATASET_DIR = ROOT / "data" / "experiments"


def load_expectations():
    with (CASE_DIR / "expected.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def case_state(name):
    return build_state(load_problem(CASE_DIR / (name + ".json")))


class CaseTests(unittest.TestCase):
    def test_every_case_has_expected_result(self):
        names = set()
        for path in CASE_DIR.glob("*.json"):
            if path.name != "expected.json":
                names.add(path.stem)
        self.assertEqual(names, set(load_expectations()))
        self.assertEqual(len(names), 10)

    def test_known_evaluations(self):
        expectations = load_expectations()
        for name in expectations:
            with self.subTest(case=name):
                state = case_state(name)
                result = evaluate_state(state)
                target = expectations[name]
                for field in ("value", "penalty", "state_value", "is_valid", "violations"):
                    self.assertEqual(result[field], target[field])
                weight = 0
                for package in state.packages:
                    if package.position is not None:
                        weight += package.weight
                self.assertEqual(weight, target["total_weight"])

    def test_grid_and_outside_volume_match_repo_cells(self):
        for name in load_expectations():
            with self.subTest(case=name):
                state = case_state(name)
                dim = state.trucks[0].dimension
                expected_grid = []
                for z in range(dim.h):
                    layer = []
                    for y in range(dim.l):
                        row = []
                        for x in range(dim.w):
                            row.append(set())
                        layer.append(row)
                    expected_grid.append(layer)
                for package in state.packages:
                    cells = get_occupied_cells(package)
                    inside = 0
                    for x, y, z in cells:
                        if 0 <= x < dim.w and 0 <= y < dim.l and 0 <= z < dim.h:
                            expected_grid[z][y][x].add(package.id)
                            inside += 1
                    if package.position is not None:
                        size = package.dimension
                        self.assertEqual(len(cells), size.w * size.l * size.h)
                        self.assertEqual(state.outside_volume[package.id], len(cells) - inside)
                self.assertEqual(len(state.grid), 1)
                self.assertEqual(state.grid[0], expected_grid)

    def test_support_cases_have_distinct_meanings(self):
        partial = evaluate_state(case_state("partial_support"))
        fragile = evaluate_state(case_state("fragile_support"))
        edge = evaluate_state(case_state("edge_only_support"))
        self.assertTrue(partial["is_valid"])
        self.assertEqual(fragile["violations"]["unsupported"], 0)
        self.assertEqual(fragile["violations"]["fragile_support"], 1)
        self.assertEqual(edge["violations"]["unsupported"], 1)

    def test_valid_pair_optimum_is_110(self):
        state = case_state("valid_pair")
        subsets = [[]]
        for package in state.packages:
            additions = []
            for subset in subsets:
                additions.append(subset + [package])
            subsets.extend(additions)
        best_weight_feasible_value = 0
        for subset in subsets:
            weight = 0
            value = 0
            for package in subset:
                weight += package.weight
                value += package.value
            if weight <= state.trucks[0].max_capacity:
                best_weight_feasible_value = max(best_weight_feasible_value, value)
        self.assertEqual(best_weight_feasible_value, 110)
        result = evaluate_state(state)
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["value"], 110)


class DatasetTests(unittest.TestCase):
    def test_dataset_sizes_and_trucks(self):
        configurations = [
            ("small", 10, (6, 6, 6), 30),
            ("medium", 30, (10, 10, 8), 90),
            ("large", 60, (14, 12, 10), 180)
        ]
        for name, count, dimensions, capacity in configurations:
            with self.subTest(dataset=name):
                problem = load_problem(DATASET_DIR / (name + ".json"))
                self.assertEqual(len(problem.packages), count)
                self.assertEqual(len(problem.trucks), 1)
                dim = problem.trucks[0].dimension
                self.assertEqual((dim.w, dim.l, dim.h), dimensions)
                self.assertEqual(problem.trucks[0].max_capacity, capacity)

    def test_dataset_starts_without_loaded_packages(self):
        for name in ("small", "medium", "large"):
            with self.subTest(dataset=name):
                problem = load_problem(DATASET_DIR / (name + ".json"))
                state = build_state(problem)
                self.assertEqual(state.loaded_list, set())
                self.assertEqual(len(state.unloaded_list), len(problem.packages))
                result = evaluate_state(state)
                self.assertTrue(result["is_valid"])
                self.assertEqual(result["state_value"], 0)

    def test_each_dataset_package_can_fit_individually(self):
        for name in ("small", "medium", "large"):
            problem = load_problem(DATASET_DIR / (name + ".json"))
            truck = problem.trucks[0].dimension
            truck_sides = sorted((truck.w, truck.l, truck.h))
            for package in problem.packages:
                with self.subTest(dataset=name, package=package.id):
                    dim = package.dimension
                    sides = sorted((dim.w, dim.l, dim.h))
                    for i in range(3):
                        self.assertLessEqual(sides[i], truck_sides[i])
                    self.assertLessEqual(package.weight, problem.trucks[0].max_capacity)


if __name__ == "__main__":
    unittest.main()
