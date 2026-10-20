import matplotlib.pyplot as plt

from ..utils.evaluator import evaluate_state
from ..utils.initial_state import dimensions_for_orientation

def draw_state(ax, state, title, value, consider_eta: bool = False):
    # Buat truk (Gambarnya sebagai kotak transparan)
    truck = state.truck.dimension
    ax.bar3d(0, 0, 0, truck.w, truck.l, truck.h, color = "lightskyblue", alpha = 0.08, edgecolor = "black")

    outside_x = truck.w + 0.5 # Titik awal kotak diluar
    min_display_x = 0
    min_display_y = 0
    min_display_z = 0
    max_display_x = truck.w
    max_display_y = truck.l
    max_display_z = truck.h

    # Gambar semua paket
    for index, package in enumerate(state.packages):
        width, length, height = dimensions_for_orientation(package, package.orientation)
        outside = package.position is None

        # Paket luar digambar disamping kanan truk
        if outside:
            x, y, z = outside_x, 0, 0
            outside_x += width + 0.25
            
        else:
            offset_x, offset_y, offset_z = package.oriented_offset
            end_x = package.position.x + offset_x
            end_y = package.position.y + offset_y
            end_z = package.position.z + offset_z

            x = min(package.position.x, end_x)
            y = min(package.position.y, end_y)
            z = min(package.position.z, end_z)

        min_display_x = min(min_display_x, x)
        min_display_y = min(min_display_y, y)
        min_display_z = min(min_display_z, z)
        max_display_x = max(max_display_x, x + width)
        max_display_y = max(max_display_y, y + length)
        max_display_z = max(max_display_z, z + height)

        # Gambar bentuk paket
        ax.bar3d(x, y, z, width, length, height, color = plt.cm.tab20(index), alpha = 0.45 if outside else 0.7, edgecolor="red" if outside else "black")

        # ID packege di tengah kotak yang di gambar
        ax.text(x + width / 2, y + length / 2, z + height / 2, package.id, ha = "center")

    display_width = max_display_x - min_display_x
    display_length = max_display_y - min_display_y
    display_height = max_display_z - min_display_z

    # Atur batas sumbu, nama sumbu, dan judul state
    ax.set(
        xlim=(min_display_x - 0.25, max_display_x + 0.25),
        ylim=(min_display_y - 0.25, max_display_y + 0.25),
        zlim=(min_display_z - 0.25, max_display_z + 0.25),
        xlabel="Width (x)",
        ylabel="Length (y)",
        zlabel="Height (z)",
        title=f"{title}\nObjective value: {value}",
    )

    ax.set_box_aspect((display_width, display_length, display_height))
    ax.set_proj_type("ortho")
    ax.grid(False)

    # Garis koordinat x, y, z di truk
    axes = [
        ((truck.w, 0, 0), "red", "X"),
        ((0, truck.l, 0), "green", "Y"),
        ((0, 0, truck.h), "blue", "Z"),
    ]

    for end, color, label in axes:
        end_x = end[0]
        end_y = end[1]
        end_z = end[2]

        ax.quiver(0, 0, 0, end_x, end_y, end_z, color=color, arrow_length_ratio=0.06)
        ax.text(end_x, end_y, end_z, f" {label}", color=color, weight="bold")

    # Informasi nilai dan pelanggaran pada state
    evaluation = evaluate_state(state, consider_eta)
    valid_text = "Ya"

    if evaluation["is_valid"] == False:
        valid_text = "Tidak"

    state_info = f"Loaded value: {evaluation['value']}"
    state_info += f"\nValid: {valid_text}"
    state_info += f"\nOverload: {evaluation['overload']}"
    state_info += f"\nOverlap: {evaluation['overlap']}"
    state_info += f"\nOut of bounds: {evaluation['out_of_bounds']}"
    state_info += f"\nUnsupported: {evaluation['unsupported']}"
    state_info += f"\nFragile support: {evaluation['fragile_support']}"
    state_info += f"\nETA value: {evaluation['eta_value']}"

    ax.text2D(0.02, 0.98, state_info, transform=ax.transAxes, va="top", fontsize=8, bbox={"facecolor": "white", "alpha": 0.75})

def visualize_result(result: dict, algorithm: str, consider_eta: bool = False):
    if algorithm == "steepest ascent":
        visualize_steepest_ascent(result, consider_eta)

    elif algorithm == "sideways move":
        visualize_sideways_move(result, consider_eta)

    elif algorithm == "random restart":
        visualize_random_restart(result, consider_eta)

    elif algorithm == "stochastic":
        visualize_stochastic(result, consider_eta)

    elif algorithm == "simulated annealing":
        visualize_simulated_annealing(result, consider_eta)

    elif algorithm == "genetic algorithm":
        visualize_genetic_algorithm(result, consider_eta)

    else:
        raise RuntimeError(f"Invalid algorithm: {algorithm}")

def visualize_steepest_ascent(result: dict, consider_eta: bool = False):
    # Get alll the requred data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    # Draw initial state dan final state 
    draw_state(initial_ax, initial_state, "Initial State", initial_value, consider_eta)
    draw_state(final_ax, final_state, "Final State", final_value, consider_eta)

    graph_ax.plot(history, marker="o")

    # Judul dan nama sumbbu x dan y
    graph_ax.set_title("Objective Value terhadap Iterasi")
    graph_ax.set_xlabel("Iterasi")
    graph_ax.set_ylabel("Objective Value")
    graph_ax.grid(alpha=0.3)

    # Informasi benchmark algoritma yang ditampilkan
    info = {
        "Algoritma": "Steepest Ascent",
        "Jumlah iterasi": result.get("iteration", 0),
        "Durasi": f"{result.get('duration', 0):.4f} detik",
        "Nilai awal": initial_value,
        "Nilai akhir": final_value,
    }

    # Hasil
    draw_information(info_ax, info)
    figure.suptitle("Hasil Steepest Ascent", fontsize=16, fontweight="bold")
    plt.show()

def visualize_sideways_move(result: dict, consider_eta: bool = False):
    # Get alll the requred data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    # Draw initial state dan final state 
    draw_state(initial_ax, initial_state, "Initial State", initial_value, consider_eta)
    draw_state(final_ax, final_state, "Final State", final_value, consider_eta)

    graph_ax.plot(history, marker="o")

    # Judul dan nama sumbbu x dan y
    graph_ax.set_title("Objective Value terhadap Iterasi")
    graph_ax.set_xlabel("Iterasi")
    graph_ax.set_ylabel("Objective Value")
    graph_ax.grid(alpha=0.3)

    # Informasi benchmark algoritma yang ditampilka
    info = {
        "Algoritma": "Sideways Move",
        "Jumlah iterasi": result.get("iteration", 0),
        "Durasi": f"{result.get('duration', 0):.4f} detik",
        "Nilai awal": initial_value,
        "Nilai akhir": final_value,
        "Sideways move": result.get("sideways_move", 0),
        "Maximum sideways": result.get("max_sideways", 0),
    }

    # Hasil Algoritma
    draw_information(info_ax, info)
    figure.suptitle("Hasil Sideways Move", fontsize=16, fontweight="bold")
    plt.show()

def visualize_random_restart(result: dict, consider_eta: bool = False):
    # Get alll the requred data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    # Draw initial state dan final state 
    draw_state(initial_ax, initial_state, "Initial State", initial_value, consider_eta)
    draw_state(final_ax, final_state, "Final State", final_value, consider_eta)

    # Nilai Objective untuk setiap restart
    objective_per_restart = result.get("objective_per_restart", [])
    start_iteration = 0
    for index in range(len(objective_per_restart)):
        restart_history = objective_per_restart[index]
        end_iteration = start_iteration + len(restart_history)

        iterations = range(start_iteration, end_iteration)
        graph_ax.plot(iterations, restart_history, marker="o", color="tab:blue")
        
        if index > 0:
            restart_line = start_iteration - 0.5
            graph_ax.axvline(restart_line, color="gray", linestyle="--", alpha=0.6)
            graph_ax.text(restart_line, 0.97, f"Restart {index}", transform=graph_ax.get_xaxis_transform(), ha="right", va="top", rotation=90, fontsize=7, color="gray")
        
        start_iteration = end_iteration

        # Judul dan nama sumbbu x dan y
        graph_ax.set_title("Objective Value terhadap Iterasi")
        graph_ax.set_xlabel("Iterasi Total")
        graph_ax.set_ylabel("Objective Value")
        graph_ax.grid(alpha=0.3)

        # Informasi benchmark algoritma
        info = {
            "Algoritma": "Random Restart",
            "Jumlah iterasi": result.get("iteration", 0),
            "Durasi": f"{result.get('duration', 0):.4f} detik",
            "Nilai awal": initial_value,
            "Nilai akhir": final_value,
            "Jumlah restart": result.get("restart", 0),
            "Maximum restart": result.get("max_restart", 0),
            "Iterasi per restart": result.get("iteration_per_restart", []),
        }

        draw_information(info_ax, info)
        figure.suptitle("Hasil Random Restart", fontsize=16, fontweight="bold")
        plt.show()    

def visualize_stochastic(result: dict, consider_eta: bool = False):
    # Get alll the requred data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    # Draw initial state dan final state 
    draw_state(initial_ax, initial_state, "Initial State", initial_value, consider_eta)
    draw_state(final_ax, final_state, "Final State", final_value, consider_eta)

    graph_ax.plot(history, marker="o")

    # Judul dan nama sumbbu x dan y
    graph_ax.set_title("Objective Value terhadap Iterasi")
    graph_ax.set_xlabel("Iterasi")
    graph_ax.set_ylabel("Objective Value")
    graph_ax.grid(alpha=0.3)

    # Informasi benchmark
    info = {
        "Algoritma": "Stochastic Hill Climbing",
        "Jumlah iterasi": result.get("iteration", 0),
        "Durasi": f"{result.get('duration', 0):.4f} detik",
        "Nilai awal": initial_value,
        "Nilai akhir": final_value,
    }

    # Hasil
    draw_information(info_ax, info)
    figure.suptitle("Hasil Stochastic Hill Climbing", fontsize=16, fontweight="bold")
    plt.show()

def visualize_simulated_annealing(result: dict, consider_eta: bool = False):
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])
    probability_history = result.get("probability_history", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    draw_state(initial_ax, initial_state, "Initial State", initial_value, consider_eta)
    draw_state(final_ax, final_state, "Final State", final_value, consider_eta)

    graph_ax.plot(history, color="tab:blue", label="Objective value")
    graph_ax.set(title="Objective dan Probability terhadap Iterasi", xlabel="Iterasi", ylabel="Objective Value")
    graph_ax.grid(alpha=0.3)

    probability_ax = graph_ax.twinx()
    probability_ax.plot(range(1, len(probability_history) + 1), probability_history, color="orange", label="Probability")
    probability_ax.set_ylabel("Probability")

    graph_lines = graph_ax.get_lines() + probability_ax.get_lines()
    graph_labels = []

    for line in graph_lines:
        graph_labels.append(line.get_label())

    graph_ax.legend(graph_lines, graph_labels)

    info = {
        "Algoritma": "Simulated Annealing",
        "Jumlah iterasi": result.get("iteration", 0),
        "Durasi": f"{result.get('duration', 0):.4f} detik",
        "Nilai awal": initial_value,
        "Nilai akhir": final_value,
        "Frekuensi stuck": result.get("stuck", 0),
    }

    draw_information(info_ax, info)
    figure.suptitle("Hasil Simulated Annealing", fontsize=16, fontweight="bold")
    plt.show()

def visualize_genetic_algorithm(result: dict, consider_eta: bool = False): 
    # Individu terbaik dari populasi awal
    initial_individual = result["initial_population"][0]

    for individual in result["initial_population"]:
        individual_value = individual["evaluation"]["state_value"]
        initial_value = initial_individual["evaluation"]["state_value"]

        if individual_value > initial_value:
            initial_individual = individual

    final_individual = result["best_valid"]

    if final_individual is None:
        final_individual = result["best_individual"]

    # State dan nilai awal serta akhir
    initial_state = initial_individual["state"]
    final_state = final_individual["state"]
    initial_value = initial_individual["evaluation"]["state_value"]
    final_value = final_individual["evaluation"]["state_value"]

    generations = []
    maximum = []
    average = []

    for generation in result["history"]:
        generations.append(generation["generation"])
        maximum.append(generation["max_fitness"])
        average.append(generation["mean_fitness"])

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    draw_state(initial_ax, initial_state, "Best Initial Individual", initial_value, consider_eta)
    draw_state(final_ax, final_state, "Best Final Individual", final_value, consider_eta)

    graph_ax.plot(generations, maximum, label="Maximum")
    graph_ax.plot(generations, average, label="Average")
    graph_ax.set(title="Fitness terhadap Generasi", xlabel="Generasi", ylabel="Fitness")
    graph_ax.legend()
    graph_ax.grid(alpha=0.3)

    # Informasi Benchmark algoritma
    parameters = result["parameters"]
    info = {
        "Algoritma": "Genetic Algorithm",
        "Jumlah generasi": parameters["generation_count"],
        "Jumlah populasi": parameters["population_size"],
        "Mutation rate": parameters["mutation_rate"],
        "Durasi": f"{result['duration_seconds']:.4f} detik",
        "Nilai awal": initial_value,
        "Nilai akhir": final_value,
    }

    # Hasil
    draw_information(info_ax, info)
    figure.suptitle("Hasil Genetic Algorithm", fontsize=16, fontweight="bold")
    plt.show()

def create_figure():
    figure = plt.figure(figsize=(15, 9), constrained_layout=True)
    initial_ax = figure.add_subplot(221, projection="3d")
    final_ax = figure.add_subplot(222, projection="3d")
    graph_ax = figure.add_subplot(223)
    info_ax = figure.add_subplot(224)

    return figure, initial_ax, final_ax, graph_ax, info_ax

def draw_information(info_ax, info):
    info_ax.axis("off")
    info_ax.set_title("Benchmark Algoritma")

    info_text = ""

    for key, value in info.items():
        if info_text != "":
            info_text += "\n"

        info_text += f"{key}: {value}"

    info_ax.text(0.05, 0.9, info_text, va="top", fontsize=12)