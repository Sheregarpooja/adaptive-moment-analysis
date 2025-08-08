"""
tuner.py - Benchmark-based threshold selector for momentcore.

This module benchmarks the performance of two algorithms:
- Two-pass method
- Pebay's one-pass method

It determines the threshold (input size) where one method becomes faster than the other.
The result is cached in a local config file tied to the current system setup to avoid
re-running benchmarks unnecessarily.

Author: Pooja Sheregar
"""

import json
import os
import time
import hashlib
import platform
import getpass

# Where we cache the benchmark results per system
CONFIG_PATH = os.path.expanduser("~/.momentcore_config.json")


def _system_fingerprint():
    """
    Generates a stable fingerprint for the current system and Python environment.

    This helps us determine if the machine or environment has changed and if we need to rebenchmark.
    """
    identity = {
        "platform": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "user": getpass.getuser(),
    }

    hash_obj = hashlib.sha256()
    hash_obj.update(json.dumps(identity, sort_keys=True).encode())
    return hash_obj.hexdigest()


def _run_benchmark(func, row_lengths, repeat=5):
    """
    Benchmarks a function across various row lengths and returns average timings.

    Args:
        func (callable): The algorithm to test
        row_lengths (list[int]): List of input sizes to test
        repeat (int): How many times to run each input size

    Returns:
        dict: {row_length: avg_time_in_seconds}
    """
    results = {}
    for n in row_lengths:
        row = [i % 128 - 64 for i in range(n)]
        durations = []

        for _ in range(repeat):
            start = time.perf_counter()
            func(row)
            durations.append(time.perf_counter() - start)

        results[n] = sum(durations) / repeat
    return results


def _find_crossover(twopass_times, pebay_times):
    """
    Finds the row length where Pebay becomes faster than two-pass.

    Returns:
        int: The optimal threshold (row length)
    """
    for n in sorted(twopass_times.keys()):
        if pebay_times[n] < twopass_times[n]:
            return n
    return max(twopass_times.keys())  # default to max tested


def get_optimal_threshold(twopass_fn, pebay_fn, force_retune=False):
    """
    Main interface to get the optimal threshold for algorithm switching.

    Returns:
        int: Row length threshold
    """
    system_id = _system_fingerprint()

    # Try loading from cache
    if not force_retune and os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
                if config.get("system_id") == system_id and "threshold" in config:
                    return config["threshold"]
        except Exception:
            pass  # silently ignore bad config

    # If we get here, we need to benchmark
    print("Running algorithm benchmarks (first use or system changed)...")

    row_lengths = list(range(8, 2049, 32))  # from 8 to 2048 in steps of 32
    twopass = _run_benchmark(twopass_fn, row_lengths)
    pebay = _run_benchmark(pebay_fn, row_lengths)
    threshold = _find_crossover(twopass, pebay)

    # Save to config
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "threshold": threshold,
                "system_id": system_id,
                "twopass": twopass,
                "pebay": pebay
            }, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save config file: {e}")

    return threshold