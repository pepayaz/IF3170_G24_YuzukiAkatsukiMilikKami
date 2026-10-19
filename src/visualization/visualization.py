import matplotlib.pyplot as plt

def package_size(package):
    # Ambil dimensi pakets
    orientation = package.orientation
    size = {
        orientation.w.strip("-"): package.dimension.w,
        orientation.l.strip("-"): package.dimension.l,
        orientation.h.strip("-"): package.dimension.h,
    }

    return size["x"], size["y"], size["z"]

def draw_state(ax, state, title, value):
    # Buat truk (Gambarnya sebagai kotak transparan)
    truck = state.truck.dimension
    ax.bar3d(0, 0, 0, truck.w, truck.l, truck.h, color = "lightskyblue", alpha = 0.08, edgecolor = "black")

    outside_x = truck.w + 0.5 # Titik awal kotak diluar
    # Gambar semua paket
    for index, package in enumerate(state.packages):
        width, length, height = package_size(package)
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

    # Gunakan proyeksi ortografis dan sembunyikan grid bawaan
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
    algorithms = [
        "Steepest Ascent",
        "Sideways Move",
        "Random Restart",
        "Stochastic Hill Climbing",
        "Simulated Annealing",
        "Genetic Algorithm",
    ]

    if algorithm not in algorithms:
        raise RuntimeError(f"Invalid algorithm: {algorithm}")

    # States data
    initial_state = result["initial"]
    final_state = result["current"]
    history = result.get("all_states", [])

    # Genetic Algorithm  
    if algorithm == "Genetic Algorithm":
        history = result.get("max_states", [])

    # Bagi window jadi empat area
    figure = plt.figure(figsize=(15, 9), constrained_layout=True)
    initial_ax = figure.add_subplot(221, projection="3d")
    final_ax = figure.add_subplot(222, projection="3d")
    graph_ax = figure.add_subplot(223)
    info_ax = figure.add_subplot(224)

    # Ambil nilai awal dan akhir
    if history:
        initial_value = history[0]
        final_value = history[-1]
    else:
        initial_value = None
        final_value = None
    
    # Gambar kondisi paket sebelum dan sesudah pencarian
    draw_state(initial_ax, initial_state, "Initial State", initial_value)
    draw_state(final_ax, final_state, "Final State", final_value)

    # Random Restart = objective untuk setiap restart
    if algorithm == "Random Restart":
        graph_ax.set_xlabel("Iterasi Total")
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

    # Genetic Algorithm menampilkan nilai maksimum dan rata-rata populasi
    elif algorithm == "Genetic Algorithm": # TODO
        graph_ax.plot(history, label="Maximum")
        graph_ax.plot(result.get("average_states", []), label="Average")
        graph_ax.legend()

    else:
        graph_ax.plot(history, marker="o", label="Objective value")

    # Simulated Annealing 
    if algorithm == "Simulated Annealing": # TODO
        temperature_ax = graph_ax.twinx()
        temperature_ax.plot(result.get("temperature_history", []), color="orange", label="Temperature")
        temperature_ax.set_ylabel("Temperature")

    # Atur judul, nama sumbu, dan grid grafik history.
    graph_ax.set(title="Objective Value terhadap Iterasi", xlabel="Iterasi", ylabel="Objective Value")
    graph_ax.grid(alpha=0.3)

    # Informasi Setiap algoritma
    info = {
        "Algoritma": algorithm,
        "Jumlah iterasi": result.get("iteration", 0),
        "Durasi": f"{result.get('duration', 0):.4f} detik",
        "Nilai awal": initial_value,
        "Nilai akhir": final_value,
    }

    if algorithm == "Sideways Move":
        info["Sideways move"] = result.get("sideways_move", 0)
        info["Maximum sideways"] = result.get("max_sideways", 0)

    elif algorithm == "Random Restart": # TODO
        info["Jumlah restart"] = result.get("restart", 0)
        info["Maximum restart"] = result.get("max_restart", 0)
        info["Iterasi per restart"] = result.get("iteration_per_restart", [])

    elif algorithm == "Simulated Annealing": # TODO
        info["Frekuensi stuck"] = result.get("stuck", 0)

    elif algorithm == "Genetic Algorithm": # TODO
        info["Jumlah populasi"] = result.get("population_size", 0)

    info_ax.axis("off")
    info_ax.set_title("Benchmark Algoritma")

    info_text = ""
    for key, value in info.items():
        if info_text != "":
            info_text += "\n"

        info_text += f"{key}: {value}"

    # Bechmark untuk algoritma
    info_ax.text(0.05, 0.9, info_text, va="top", fontsize=12)

    figure.suptitle("Hasil Algoritma", fontsize=16, fontweight="bold")
    plt.show()