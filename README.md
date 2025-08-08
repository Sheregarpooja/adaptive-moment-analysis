# Adaptive Moment Analysis Engine

A high-performance hybrid C++/Python tool to compute the **first four standardized moments** (mean, variance, skewness, kurtosis) per row from a binary file containing matrix data.

It uses:
- **C++ (via pybind11)** for fast algorithmic computation
- **Python** for I/O, CLI, and logic orchestration
- **Smart benchmark tuning** to adaptively choose the best algorithm per machine

---

## Key Features

- Automatically selects between two-pass and one-pass (Pebay) algorithms
- Benchmarks execution speed for adaptive tuning
- Retunes automatically on new systems or on-demand
- Human-readable CLI with optional comparison
- Cross-platform via Python `venv` and `setuptools`
- Full test coverage with `pytest`

---

## Project Structure

```bash
.
├── main.py                      # Main CLI interface for execution
├── tuner.py                     # Benchmarking logic for threshold tuning
├── setup.py                     # Pybind11 extension builder with rebuild caching
├── setup.sh                     # One-step setup script: venv, deps, build, test
├── Makefile                     # Developer-friendly command shortcuts
├── requirements.txt             # Python dependencies
├── bindings/     
│   └── bindings.cpp             # Pybind11 binding code (C++ to Python)
├── src/    
│   ├── moments_pebay.cpp        # One-pass (Pebay) implementation
│   ├── moments_twopass.cpp      # Two-pass implementation
│   └── moments.hpp              # Shared header file
├── tests/     
│   ├── test_main.py             # Unit tests for CLI/data logic
│   └── test_tuner.py            # Unit tests for tuning/benchmark logic
```

---

## How It Works

1. **Input**: A `.bin` file with header `[int32 M][int32 N]` and `M×N` `int8` matrix data.
2. **Tuner**:
   - Benchmarks both algorithms on your system.
   - Determines a row length `threshold` where Pebay becomes faster than two-pass.
   - Caches this value per system (in `~/.momentcore_config.json`).
3. **Computation**:
   - Each row is passed through either algorithm based on its length.
   - Results are rounded and returned as 4 rows (μ1 to μ4).
4. **Optional**: Compare the output with an expected `.txt` file for verification.

---

## Why This Design?

| Design Choice | Reason |
|---------------|--------|
| **Hybrid C++ + Python** | C++ is faster for numeric processing; Python simplifies I/O and control. |
| **Pybind11 over Ctypes or Cython** | Cleaner, header-only, and integrates with `setuptools`. |
| **setup.py build** | Works across OSes without platform-specific compilers. |
| **Auto-tuning** | Adapts performance dynamically for any system. |
| **No GUI** | Pure CLI keeps the tool lightweight and scriptable. |
| **Optional testing** | Doesn't force slow test runs on first use, but supports them. |

---

## Validation

Each part of the system is tested and verified:

| Component           | Validated via     |
|---------------------|------------------|
| Binary parsing      | `test_main.py` with malformed/correct headers |
| Algorithm accuracy  | Known output tests with rounding |
| Threshold tuning    | Mocked benchmark logic in `test_tuner.py` |
| C++ logic           | Compared against NumPy equivalents |
| CLI resilience      | Interrupt, help screen, invalid args |

---

## Setup Instructions

> All you need is Python 3.8+

### 1. Run setup

```bash
make setup
```

This will:
- Create a virtual environment in `./venv`
- Install required packages
- Compile the C++ extension
- Link `.so` file to `momentcore.so`

---

### 2. (Optional) Run all tests

```bash
make test
```

---

### . Run the program

```bash
python main.py --input your_matrix.bin
```

Optional: compare against expected output

```bash
python main.py --input your_matrix.bin --output expected.txt
```

Optional: retune threshold (e.g., on new system)

```bash
python main.py --input your_matrix.bin --retune
```

---

## Cleanup

```bash
make clean
```

Removes `.so`, cache files, build folders, etc.

---

## Binary File Format

- First 8 bytes: 2 signed 32-bit integers (`M`, `N`)
- Followed by `M * N` signed 8-bit integers (`int8`)
- All little-endian

---

## Acknowledgements

- Pybind11 for seamless C++/Python bridging
- Pebay's one-pass statistics algorithm
- Your CPU for crunching lots of numbers

---

## Tip

To activate your environment later:

```bash
source venv/bin/activate
```

## Future Improvements

- **Matrix-shape-aware parallelization**:  
  Depending on the matrix shape, introduce:
  - **Batch parallelization** in Python (e.g., multiprocessing for row-wise computation)
  - **C++ thread-level parallelism** using OpenMP or `std::thread` for inner-loop acceleration

- **Binary format optimization**:  
  Consider using memory-mapped files (`mmap`) or a compressed format for very large datasets.

- **Visualization CLI tool**:  
  Add an optional module to plot distributions or moment trends across the matrix.