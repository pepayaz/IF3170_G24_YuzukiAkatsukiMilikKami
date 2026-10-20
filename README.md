# IF3170_G24_YuzukiAkatsukiMilikKami

Tugas Besar 1 IF3170 Inteligensi Artifisial 2026/2027.

Program untuk mencari susunan paket di dalam peti kemas truk (Mejiro Express) dengan local search. Tujuannya memaksimalkan total value paket yang dimuat tanpa melanggar constraint. Algoritma yang diimplementasikan:

- Hill-Climbing: Steepest Ascent, Sideways Move, Random Restart, dan Stochastic
- Simulated Annealing
- Genetic Algorithm

Program juga mendukung lebih dari satu truk dengan ukuran dan kapasitas yang berbeda-beda (bonus multi-truk), serta objective function alternatif yang memperhitungkan ETA (bonus objective function).

## Requirement

- Python 3.10 atau lebih baru
- matplotlib

```bash
pip install matplotlib
```

Selain matplotlib, program hanya memakai library bawaan Python.

## Cara menjalankan

Jalankan dari folder utama repository:

```bash
python main.py
```

Program akan menanyakan beberapa hal secara berurutan:

1. Nama file JSON di folder `tests`, misalnya `small` atau `multi_truck.json`
2. Nomor algoritma (1 Steepest Ascent, 2 Sideways Move, 3 Random Restart, 4 Stochastic, 5 Simulated Annealing, 6 Genetic Algorithm)
3. Apakah ETA ikut dihitung dalam objective function (`y`/`n`)
4. Berapa kali algoritma dijalankan

Setiap run menghasilkan satu gambar di folder `output` dengan nama `<file>_<algoritma>_<eta|tanpa_eta>_<run>.png`. Gambar berisi state awal, state akhir, grafik objective function terhadap iterasi, dan ringkasan hasil (durasi, jumlah iterasi, dan informasi khusus tiap algoritma).

Contoh:

```text
Nama file JSON dari folder tests: small
Pilih nomor algoritma: 5
Gunakan ETA dalam objective function? (y/n): n
Jumlah iterasi percobaan: 3
```

Perintah di atas menjalankan Simulated Annealing tiga kali pada `tests/small.json` dan menyimpan `small_simulated_annealing_tanpa_eta_1.png` sampai `_3.png`.

### Parameter algoritma

| Algoritma | Parameter | Nilai default | Lokasi |
| --- | --- | --- | --- |
| Sideways Move | maksimum sideways move | 10 | `MAX_SIDEWAYS_MOVE` di `src/algorithm/hillclimbing.py` |
| Random Restart | maksimum restart | 10 | `MAX_RESTART` di `src/algorithm/hillclimbing.py` |
| Stochastic | maksimum iterasi | 100 | `MAX_ITERATION` di `src/algorithm/hillclimbing.py` |
| Simulated Annealing | suhu awal, penurunan suhu per iterasi | 1000, 1 | `src/algorithm/simulated_annealing.py` |
| Genetic Algorithm | jumlah populasi, banyak generasi, mutation rate | 20, 100, 0.2 | argumen `run_ga` (dipanggil di `main.py`) |

Untuk eksperimen GA dengan variasi populasi dan iterasi, ubah argumen pemanggilan `run_ga` di `main.py`, misalnya:

```python
result = run_ga(problem, population_size=40, generation_count=200, consider_eta=consider_eta)
```

### Menjalankan test

```bash
python -m unittest tests.test_cases
```

## Representasi

- Koordinat berupa bilangan bulat dengan `x` = lebar, `y` = panjang, `z` = tinggi. Lantai truk berada di `z = 0`.
- Posisi paket adalah sel jangkar. Orientasi menyatakan sumbu tujuan tiap sisi paket (`w`, `l`, `h`) beserta arahnya, misalnya `{"w": "y", "l": "-x", "h": "z"}` untuk rotasi 90° terhadap sumbu z. Tanda minus berarti paket memanjang ke arah negatif sumbu tersebut dari sel jangkar. Orientasi yang merupakan pencerminan (misalnya `{"w": "y", "l": "x", "h": "z"}`) ditolak karena tidak bisa dicapai dengan rotasi.
- Paket yang tidak dimuat memiliki posisi `null`.
- Setiap paket yang dimuat menyimpan indeks truk tempat paket berada.

Neighbor yang dipakai sesuai spesifikasi:

1. Menukar dua paket, baik yang di dalam maupun di luar truk (termasuk antar truk)
2. Memindahkan paket ke koordinat lain, bisa ke truk lain
3. Merotasi paket 90° terhadap sumbu x, y, atau z

Initial state dibangkitkan secara acak. Setiap paket dimuat dengan peluang 0,5 ke truk yang muat, dengan orientasi dan posisi acak di dalam batas truk.

## Objective function

```
state_value = total value paket yang dimuat - penalti
```

Penalti dihitung dari pelanggaran constraint:

| Pelanggaran | Penalti |
| --- | --- |
| Setiap jenis pelanggaran yang terjadi | 100 |
| Kelebihan berat dari kapasitas truk | 10 per unit berat |
| Paket saling beririsan | 10 per sel yang beririsan |
| Bagian paket menembus dinding truk | 10 per sel di luar truk |
| Paket melayang | 10 per paket |
| Paket fragile menyangga paket lain | 10 per pasangan |

Definisi constraint mengikuti spesifikasi:

- Paket dianggap tidak melayang jika berada di lantai atau minimal satu titik alasnya ditopang bagian atas paket lain. Kontak di tepi saja tanpa luas bidang tidak dihitung sebagai topangan.
- Paket fragile tidak boleh berada di bawah paket lain.
- Kapasitas berat diperiksa untuk setiap truk.

Jika ETA diaktifkan, setiap paket yang dimuat menambah nilai sebesar `100 // eta²`. Paket yang lebih cepat harus sampai mendapat bobot lebih besar, sehingga pencarian cenderung memprioritaskan paket dengan ETA kecil.

## Format input

Input berupa file JSON. Format satu truk:

```json
{
  "schema_version": 1,
  "truck": {
    "dimension": { "w": 4, "l": 3, "h": 2 },
    "max_capacity": 7
  },
  "packages": [
    {
      "id": "A",
      "dimension": { "w": 2, "l": 2, "h": 1 },
      "value": 60,
      "weight": 4,
      "is_fragile": false,
      "eta": 1
    }
  ]
}
```

Untuk lebih dari satu truk, ganti `truck` dengan `trucks` berisi array truk:

```json
"trucks": [
  { "dimension": { "w": 4, "l": 3, "h": 2 }, "max_capacity": 7 },
  { "dimension": { "w": 3, "l": 3, "h": 3 }, "max_capacity": 10 }
]
```

`initial_state` bersifat opsional dan dipakai jika ingin memberi susunan awal sendiri. Semua id paket harus ada, dengan nilai `null` untuk paket yang tidak dimuat:

```json
"initial_state": {
  "A": {
    "truck": 0,
    "position": { "x": 0, "y": 0, "z": 0 },
    "orientation": { "w": "x", "l": "y", "h": "z" }
  },
  "B": null
}
```

Field `truck` wajib diisi jika truk lebih dari satu. Untuk satu truk, field ini boleh dihilangkan.

Syarat validitas input:

- `schema_version` bernilai 1, dan hanya salah satu dari `truck` atau `trucks` yang boleh ada
- Dimensi truk dan paket berupa bilangan bulat positif
- `max_capacity` dan `value` bilangan bulat nonnegatif, `weight` bilangan bulat positif, `eta` bilangan bulat
- `id` paket unik dan tidak kosong, `is_fragile` bernilai boolean
- Field yang tidak dikenal dan key JSON duplikat ditolak

Loader hanya memeriksa format. Pelanggaran constraint pada susunan awal (misalnya overlap) tetap diterima dan dihitung oleh evaluator.

Contoh input tersedia di folder `tests`:

| File | Isi |
| --- | --- |
| `small.json`, `medium.json`, `large.json` | 10, 30, dan 60 paket untuk eksperimen, semua paket awalnya di luar truk |
| `multi_truck.json`, `multi_truck_small.json` | contoh 2 truk dan 3 truk |
| `valid_pair.json`, `overload.json`, `overlap.json`, `floating.json`, dll. | kasus kecil untuk menguji tiap constraint, hasil yang diharapkan ada di `expected.json` |

## Struktur repository

```text
.
├── main.py                 program utama
├── src
│   ├── algorithm           hill-climbing, simulated annealing, genetic algorithm
│   ├── models              Package, Truck, Problem, ProblemState
│   ├── utils               pembaca input, initial state, neighbor, evaluator
│   └── visualization       visualisasi state dan hasil eksperimen
├── tests                   file input JSON dan unit test
├── data                    salinan data kasus dan dataset eksperimen
├── docs                    laporan
└── output                  hasil run algoritma
```

## Pembagian tugas

| NIM | Nama | Tugas |
| --- | --- | --- |
| 13524076 | Fayyaz Akmal Lauda | Pembaca input, test case, initial state, Genetic Algorithm |
| 13524097 | Muhammad Faiz Alfada Dharma | Hill-Climbing, program utama, output, visualisasi |
| 13524007 | Muhammad Ashkar | Simulated Annealing, objective function ETA, multi-truk |
