from __future__ import annotations
from ..models.problem import Problem, Truck
from ..models.package import Package, Orientation, Position, Axis

#Penalty Constant
OVERLOAD_PENALTY = 10

def evaluate_state(state: Problem):
    penalty_weights = {
        "violation": -100, #per violation
        "overload": -10, #per weight
        "overlap": -10, #per block
        "out_of_bounds": -10, #per block
        "unsupported": -10, #per object
        "fragile_support": -10, #per object
    }

    overload_amount = evaluate_load(state)
    overlap_amount = evaluate_overlap(state)
    out_of_bounds_amount = evaluate_out_of_bounds(state)
    unsupported_amount = evaluate_unsupported(state)
    fragile_support_amount = evaluate_fragile_support(state)

    is_valid = True
    violation_amount = 0
    for _, amount in violations.items():
        if amount > 0:
            violation_amount += 1
            is_valid = False

    violations = {
        "violation": violation_amount,
        "overload": overload_amount,
        "overlap": overlap_amount,
        "out_of_bounds": out_of_bounds_amount,
        "unsupported": unsupported_amount,
        "fragile_support": fragile_support_amount
    }

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


def evaluate_value(state: Problem):
    total_value = 0

    for package in state.packages:
        if package.is_outside():
            continue

        total_value += package.value

    return total_value


def evaluate_load(state: Problem):
    total_weight = 0

    for package in state.packages:
        if package.is_outside():
            continue

        total_weight += package.weight

    max_capacity = state.truck.max_capacity
    overloaded_value = max(0, total_weight - max_capacity)

    return overloaded_value


def evaluate_overlap(state: Problem):
    packages = state.packages
    total_overlap = 0

    for i in range(len(packages)):
        p1 = packages[i]

        if p1.is_outside():
            continue

        p1_size_x, p1_size_y, p1_size_z = oriented_dimension(p1)

        p1_start_x = p1.position.x
        p1_start_y = p1.position.y
        p1_start_z = p1.position.z

        p1_end_x = p1_start_x + p1_size_x
        p1_end_y = p1_start_y + p1_size_y
        p1_end_z = p1_start_z + p1_size_z

        for j in range(i+1, len(packages)):
            p2 = packages[j]

            if p2.is_outside(): 
                continue
                
            p2_size_x, p2_size_y, p2_size_z = oriented_dimension(p2)

            p2_start_x = p2.position.x
            p2_start_y = p2.position.y
            p2_start_z = p2.position.z

            p2_end_x = p2_start_x + p2_size_x
            p2_end_y = p2_start_y + p2_size_y
            p2_end_z = p2_start_z + p2_size_z

            overlap_x = (min(p1_end_x, p2_end_x) - max(p1_start_x, p2_start_x))
            overlap_y = (min(p1_end_y, p2_end_y) - max(p1_start_y, p2_start_y))
            overlap_z = (min(p1_end_z, p2_end_z) - max(p1_start_z, p2_start_z))

            if overlap_x <= 0 or overlap_y <= 0 or overlap_z <= 0:
                continue

            overlap_volume = overlap_x * overlap_y * overlap_z
            total_overlap += overlap_volume

    return total_overlap


def evaluate_out_of_bounds(state: Problem):
    total_outside_volume = 0

    for package_id in state.outside_volume:
        outside_volume = state.outside_volume[package_id]
        total_outside_volume += outside_volume

    return total_outside_volume


def evaluate_unsupported(state: Problem):
    packages = state.packages
    unsupported_count = 0

    for package in packages:
        if package.is_outside():
            continue

        dim_x, dim_y, dim_z = oriented_dimension(package)
        
        support_top_y = max((support.position.y + support_dim_y), (support.position.y - support_dim_y))
        
        bottom_y = min((package.position.y + dim_y), (package.position.y - dim_y))
        
        if bottom_y == 0:
            continue

        start_x = package.position.x
        start_z = package.position.z

        end_x = start_x + dim_x
        end_z = start_z + dim_z

        has_support = False

        for support in packages:
            if support.id == package.id:
                continue

            if support.is_outside():
                continue

            support_dim_x, support_dim_y, support_dim_z = (oriented_dimension(support))
            support_top_y = (support.position.y + support_dim_y)

            if support_top_y != bottom_y - 1:
                continue

            support_start_x = support.position.x
            support_start_z = support.position.z

            support_end_x = support_start_x + support_dim_x
            support_end_z = support_start_z + support_dim_z

            overlap_x = (min(end_x, support_end_x) - max(start_x, support_start_x))
            overlap_y = (min(end_z, support_end_z) - max(start_z, support_start_z))

            if overlap_x > 0 and overlap_y > 0:
                has_support = True
                break

        if not has_support:
            unsupported_count += 1

    return unsupported_count


def evaluate_fragile_support(state: Problem):
    packages = state.packages
    fragile_support_count = 0

    for support in packages:
        if support.is_outside():
            continue

        if not support.is_fragile:
            continue

        support_dim_x, support_dim_y, support_dim_z = (oriented_dimension(support))

        support_start_x = support.position.x
        support_start_z = support.position.z

        support_end_x = support_start_x + support_dim_x
        support_end_z = support_start_z + support_dim_z

        support_top_z = max((support.position.z + support_dim_z), (support.position.z - support_dim_z))

        for package in packages:
            if package.id == support.id:
                continue

            if package.is_outside():
                continue
            
            dim_x, dim_y, dim_z = (oriented_dimension(support))

            bottom_z = min((package.position.y + dim_y), (package.position.y - dim_y))

            if bottom_z != support_top_z:
                continue

            start_x = package.position.x
            start_z = package.position.z

            end_x = start_x + dim_x
            end_z = start_z + dim_z

            overlap_x = (min(support_end_x, end_x) - max(support_start_x, start_x))
            overlap_z = (min(support_end_z, end_z) - max(support_start_z, start_z))

            if overlap_x > 0 and overlap_z > 0:
                fragile_support_count += 1

    return fragile_support_count


def oriented_dimension(package: Package):
    orientations = {
        'w': package.orientation.w,
        'l': package.orientation.l,
        'h': package.orientation.h,
    }
    
    dim = {}
    sizes = {
        'w': package.dimension.w,
        'l': package.dimension.l,
        'h': package.dimension.h,
    }

    for dimension, axis in orientations.items():
        sign = -1 if axis.startswith('-') else 1
        axis = axis.lstrip('-')

        dim[axis] = sizes[dimension] * sign
        
    return dim['x'], dim['y'], dim['z']