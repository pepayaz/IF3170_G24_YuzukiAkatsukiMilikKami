from pathlib import Path
import matplotlib.pyplot as plt

from src.algorithm.genetic_algorithm import run_ga
from src.algorithm.hillclimbing import run_hillclimbing
from src.algorithm.simulated_annealing import search_simulated_annealing
from src.utils.initial_state import generate_initial_state
from src.utils.input_loader import load_problem
from src.visualization.visualization import visualize_result

def main():
    project_path = Path(__file__).parent
    test_path = project_path / "tests"
    output_path = project_path / "output"

    # Input file name
    file_name = input("Nama file JSON dari folder tests: ").strip()
    if not file_name.lower().endswith(".json"):
        file_name += ".json"

    input_path = test_path / Path(file_name).name
    if not input_path.is_file():
        print(f"File tidak ditemukan: {input_path}")
        return

    # Load file
    try:
        problem = load_problem(input_path)

    except (OSError, ValueError) as error:
        print(f"Gagal membaca input: {error}")
        return

    # Pilih algoritma
    print("\nDaftar algoritma:")
    print("1. Steepest Ascent")
    print("2. Sideways Move")
    print("3. Random Restart")
    print("4. Stochastic")
    print("5. Simulated Annealing")
    print("6. Genetic Algorithm")

    while True:
        pilihan = input("Pilih nomor algoritma: ")

        if pilihan == "1":
            algorithm = "steepest ascent"
            break

        elif pilihan == "2":
            algorithm = "sideways move"
            break

        elif pilihan == "3":
            algorithm = "random restart"
            break

        elif pilihan == "4":
            algorithm = "stochastic"
            break

        elif pilihan == "5":
            algorithm = "simulated annealing"
            break

        elif pilihan == "6":
            algorithm = "genetic algorithm"
            break

        else:
            print("Pilihan algoritma tidak valid.")

    # Pilih penggunaan ETA
    while True:
        eta_input = input("Gunakan ETA dalam objective function? (y/n): ").strip().lower()

        if eta_input == "y":
            consider_eta = True
            break

        elif eta_input == "n":
            consider_eta = False
            break

        else:
            print("Masukkan y untuk ya atau n untuk tidak")

    # Input jumlah iterasi
    while True:
        iteration_input = input("Jumlah iterasi percobaan: ")
        if iteration_input.isdigit() and int(iteration_input) > 0:
            iteration_amount = int(iteration_input)
            break

        print("Jumlah iterasi harus berupa bilangan bulat positif")

    output_path.mkdir(exist_ok=True)
    algorithm_name = algorithm.replace(" ", "_")
    eta_name = "eta" if consider_eta else "tanpa_eta"
    original_show = plt.show
    plt.show = lambda: None

    # Jalanin algoritmanya
    for iteration in range(1, iteration_amount + 1):
        print(f"Menjalankan iterasi {iteration}/{iteration_amount}...")

        if algorithm == "simulated annealing":
            initial_state = generate_initial_state(problem)
            result = search_simulated_annealing(initial_state, consider_eta)
        
        elif algorithm == "genetic algorithm":
            result = run_ga(problem, consider_eta=consider_eta)
        
        else:
            result = run_hillclimbing(problem, algorithm, consider_eta)

        # Output image
        image_name = f"{input_path.stem}_{algorithm_name}_{eta_name}_{iteration}.png"
        image_path = output_path / image_name

        visualize_result(result, algorithm, consider_eta)
        figure = plt.gcf()
        figure.savefig(image_path)
        plt.close(figure)
        print(f"Gambar disimpan: {image_path}")

    plt.show = original_show
    print("Semua iterasi selesai")

if __name__ == "__main__":
    main()