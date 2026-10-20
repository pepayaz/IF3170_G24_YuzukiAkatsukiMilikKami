import matplotlib.pyplot as plt

from ..utils.initial_state import dimensions_for_orientation

def draw_state(ax, state, title, value):
    # Buat truk (Gambarnya sebagai kotak transparan)
    truck = state.truck.dimension
    ax.bar3d(0, 0, 0, truck.w, truck.l, truck.h, color = "lightskyblue", alpha = 0.08, edgecolor = "black")

    outside_x = truck.w + 0.5 # Titik awal kotak diluar
    # Gambar semua paket
    for index, package in enumerate(state.packages):
        width, length, height = dimensions_for_orientation(package, package.orientation)
        outside = package.position is None

        # Paket luar digambar disamping kanan truk
        if outside:
            x, y, z = outside_x, 0, 0
            outside_x += width + 0.25
            
        else:
            x = package.position.x
            y = package.position.y
            z = package.position.z

        # Gambar bentuk paket
        ax.bar3d(x, y, z, width, length, height, color = plt.cm.tab20(index), alpha = 0.45 if outside else 0.7, edgecolor="red" if outside else "black")

        # ID packege di tengah kotak yang di gambar
        ax.text(x + width / 2, y + length / 2, z + height / 2, package.id, ha = "center")

    display_width = max(truck.w, outside_x - 0.25)

    # Atur batas sumbu, nama sumbu, dan judul state
    ax.set(
        xlim=(-0.25, display_width + 0.25),
        ylim=(-0.25, truck.l + 0.25),
        zlim=(-0.25, truck.h + 0.25),
        xlabel="Width (x)",
        ylabel="Length (y)",
        zlabel="Height (z)",
        title=f"{title}\nObjective value: {value}",
    )

    ax.set_box_aspect((display_width, truck.l, truck.h))
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

def visualize_result(result: dict, algorithm: str):
    if algorithm == "steepest ascent":
        visualize_steepest_ascent(result)

    elif algorithm == "sideways move":
        visualize_sideways_move(result)

    elif algorithm == "random restart":
        visualize_random_restart(result)

    elif algorithm == "stochastic":
        visualize_stochastic(result)

    elif algorithm == "simulated annealing":
        visualize_simulated_annealing(result)

    elif algorithm == "genetic algorithm":
        visualize_genetic_algorithm(result) # TODO

    else:
        raise RuntimeError(f"Invalid algorithm: {algorithm}")

def visualize_steepest_ascent(result: dict):
    # Get alll the requred data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    # Draw initial state dan final state 
    draw_state(initial_ax, initial_state, "Initial State", initial_value)
    draw_state(final_ax, final_state, "Final State", final_value)

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

def visualize_sideways_move(result: dict):
    # Get alll the requred data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    # Draw initial state dan final state 
    draw_state(initial_ax, initial_state, "Initial State", initial_value)
    draw_state(final_ax, final_state, "Final State", final_value)

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

def visualize_random_restart(result: dict):
    # Get alll the requred data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    # Draw initial state dan final state 
    draw_state(initial_ax, initial_state, "Initial State", initial_value)
    draw_state(final_ax, final_state, "Final State", final_value)

    # Nilai Objective untuk setiap restart
    objective_per_restart = result.get("objective_per_restart", [])
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

def visualize_stochastic(result: dict):
    # Get alll the requred data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    # Draw initial state dan final state 
    draw_state(initial_ax, initial_state, "Initial State", initial_value)
    draw_state(final_ax, final_state, "Final State", final_value)

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

def visualize_simulated_annealing(result: dict):
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])
    probability_history = result.get("probability_history", [])

    initial_value = history[0]
    final_value = history[-1]

    figure, initial_ax, final_ax, graph_ax, info_ax = create_figure()

    draw_state(initial_ax, initial_state, "Initial State", initial_value)
    draw_state(final_ax, final_state, "Final State", final_value)

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

def visualize_genetic_algorithm(result: dict): # TODO
    pass

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