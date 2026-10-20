from __future__ import annotations
from ..models.problem import ProblemState, Truck
from ..models.package import Package, Orientation, Position, Axis

def evaluate_state(state: ProblemState):
    penalty_weights = {
        "violation": 100, #per violation
        "overload": 10, #per weight
        "overlap": 10, #per block
        "out_of_bounds": 10, #per block
        "unsupported": 10, #per object
        "fragile_support": 10, #per object
    }

    overload_amount = evaluate_load(state)
    overlap_amount = evaluate_overlap(state)
    out_of_bounds_amount = evaluate_out_of_bounds(state)
    unsupported_amount = evaluate_unsupported(state)
    fragile_support_amount = evaluate_fragile_support(state)

    violations = {
        "violation": 0,
        "overload": overload_amount,
        "overlap": overlap_amount,
        "out_of_bounds": out_of_bounds_amount,
        "unsupported": unsupported_amount,
        "fragile_support": fragile_support_amount
    }

    is_valid = True
    violation_amount = 0
    for _, amount in violations.items():
        if amount > 0:
            violation_amount += 1
            is_valid = False
            
    violations["violation"] = violation_amount

    total_penalty = 0

    for violation_name in violations:
        amount = violations[violation_name]
        weight = penalty_weights[violation_name]

        total_penalty += amount * weight

    loaded_value = evaluate_value(state)
    state_value = loaded_value - total_penalty

    result = {
        "is_valid": is_valid,
        "value": loaded_value,
        "penalty": total_penalty,
        "state_value": state_value,
        "violations": violations,
    }

    return result


def evaluate_value(state: ProblemState):
    total_value = 0

    for package in state.packages:
        if package.is_outside():
            continue

        total_value += package.value

    return total_value


def evaluate_load(state: ProblemState):
    overloaded_value = 0
    truck_weights = [0] * len(state.trucks)

    for package in state.packages:
        if package.is_outside():
            continue

        truck_weights[package.truck_idx] += package.weight

    for index in range(len(state.trucks)):
        max_capacity = state.trucks[index].max_capacity
        overloaded_value += max(0, truck_weights[index] - max_capacity)

    return overloaded_value


def evaluate_overlap(state: ProblemState):
    packages = state.packages
    total_overlap = 0

    for i in range(len(packages)):
        p1 = packages[i]

        if p1.is_outside():
            continue

        p1_size_x, p1_size_y, p1_size_z = p1.oriented_offset

        p1_end_x = p1.position.x + p1_size_x
        p1_end_y = p1.position.y + p1_size_y
        p1_end_z = p1.position.z + p1_size_z

        p1_min_x, p1_max_x = min(p1.position.x, p1_end_x), max(p1.position.x, p1_end_x)
        p1_min_y, p1_max_y = min(p1.position.y, p1_end_y), max(p1.position.y, p1_end_y)
        p1_min_z, p1_max_z = min(p1.position.z, p1_end_z), max(p1.position.z, p1_end_z)

        for j in range(i+1, len(packages)):
            p2 = packages[j]

            if p2.is_outside(): 
                continue

            if p2.truck_idx != p1.truck_idx:
                continue
                
            p2_size_x, p2_size_y, p2_size_z = p2.oriented_offset

            p2_end_x = p2.position.x + p2_size_x
            p2_end_y = p2.position.y + p2_size_y
            p2_end_z = p2.position.z + p2_size_z

            p2_min_x, p2_max_x = min(p2.position.x, p2_end_x), max(p2.position.x, p2_end_x)
            p2_min_y, p2_max_y = min(p2.position.y, p2_end_y), max(p2.position.y, p2_end_y)
            p2_min_z, p2_max_z = min(p2.position.z, p2_end_z), max(p2.position.z, p2_end_z)

            overlap_x = min(p1_max_x, p2_max_x) - max(p1_min_x, p2_min_x) + 1
            overlap_y = min(p1_max_y, p2_max_y) - max(p1_min_y, p2_min_y) + 1
            overlap_z = min(p1_max_z, p2_max_z) - max(p1_min_z, p2_min_z) + 1

            if overlap_x <= 0 or overlap_y <= 0 or overlap_z <= 0:
                continue

            overlap_volume = overlap_x * overlap_y * overlap_z
            total_overlap += overlap_volume

    return total_overlap


def evaluate_out_of_bounds(state: ProblemState):
    total_outside_volume = 0

    for package_id in state.outside_volume:
        outside_volume = state.outside_volume[package_id]
        total_outside_volume += outside_volume

    return total_outside_volume


def evaluate_unsupported(state: ProblemState):
    packages = state.packages
    unsupported_count = 0

    for package in packages:
        if package.is_outside():
            continue

        dim_x, dim_y, dim_z = package.oriented_offset
                
        bottom_z = min((package.position.z + dim_z), package.position.z)
        
        if bottom_z == 0:
            continue

        end_x = package.position.x + dim_x
        end_y = package.position.y + dim_y
        min_x, max_x = min(package.position.x, end_x), max(package.position.x, end_x)
        min_y, max_y = min(package.position.y, end_y), max(package.position.y, end_y)

        has_support = False

        for support in packages:
            if support.id == package.id:
                continue

            if support.is_outside():
                continue

            if support.truck_idx != package.truck_idx:
                continue

            support_dim_x, support_dim_y, support_dim_z = (support.oriented_offset)
            support_top_z = max((support.position.z + support_dim_z), support.position.z)

            if support_top_z != bottom_z - 1:
                continue

            support_end_x = support.position.x + support_dim_x
            support_end_y = support.position.y + support_dim_y
            support_min_x, support_max_x = min(support.position.x, support_end_x), max(support.position.x, support_end_x)
            support_min_y, support_max_y = min(support.position.y, support_end_y), max(support.position.y, support_end_y)

            overlap_x = min(max_x, support_max_x) - max(min_x, support_min_x) + 1
            overlap_y = min(max_y, support_max_y) - max(min_y, support_min_y) + 1

            if overlap_x > 0 and overlap_y > 0:
                has_support = True
                break

        if not has_support:
            unsupported_count += 1

    return unsupported_count


def evaluate_fragile_support(state: ProblemState):
    packages = state.packages
    fragile_support_count = 0

    for support in packages:
        if support.is_outside():
            continue

        if not support.is_fragile:
            continue

        support_dim_x, support_dim_y, support_dim_z = (support.oriented_offset)

        support_end_x = support.position.x + support_dim_x
        support_end_y = support.position.y + support_dim_y
        support_min_x, support_max_x = min(support.position.x, support_end_x), max(support.position.x, support_end_x)
        support_min_y, support_max_y = min(support.position.y, support_end_y), max(support.position.y, support_end_y)

        support_top_z = max((support.position.z + support_dim_z), support.position.z)

        for package in packages:
            if package.id == support.id:
                continue

            if package.is_outside():
                continue

            if package.truck_idx != support.truck_idx:
                continue
            
            dim_x, dim_y, dim_z = (package.oriented_offset)

            bottom_z = min((package.position.z + dim_z), package.position.z)

            if bottom_z != support_top_z + 1:
                continue

            end_x = package.position.x + dim_x
            end_y = package.position.y + dim_y
            min_x, max_x = min(package.position.x, end_x), max(package.position.x, end_x)
            min_y, max_y = min(package.position.y, end_y), max(package.position.y, end_y)

            overlap_x = min(support_max_x, max_x) - max(support_min_x, min_x) + 1
            overlap_y = min(support_max_y, max_y) - max(support_min_y, min_y) + 1

            if overlap_x > 0 and overlap_y > 0:
                fragile_support_count += 1

    return fragile_support_count