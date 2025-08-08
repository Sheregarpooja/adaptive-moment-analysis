import json
import pytest
import os
import builtins
from unittest import mock
from tuner import (
    _system_fingerprint,
    get_optimal_threshold,
    _run_benchmark,
    _find_crossover
)
from momentcore import compute_moments_twopass, compute_moments_pebay

def test_system_fingerprint_is_stable():
    """
    The system fingerprint should remain the same across calls
    if the system environment has not changed.
    """
    fp1 = _system_fingerprint()
    fp2 = _system_fingerprint()
    assert isinstance(fp1, str)
    assert fp1 == fp2


def test_find_crossover_logic():
    """
    Test that crossover is found where two-pass becomes slower than Pebay.

    - Case 1: Pebay wins at length 16 - threshold = 16
    - Case 2: Pebay never wins - return largest length
    """
    two_pass = {8: 0.5, 16: 0.6, 32: 0.8}
    pebay = {8: 0.7, 16: 0.5, 32: 0.3}
    threshold = _find_crossover(two_pass, pebay)
    assert threshold == 16

    pebay2 = {8: 0.9, 16: 0.8, 32: 0.9}  # always slower
    threshold2 = _find_crossover(two_pass, pebay2)
    assert threshold2 == 32


def test_run_benchmark_returns_timings():
    """
    Run benchmark on dummy function and ensure correct timing dictionary is returned.
    """
    def dummy_algo(row):
        sum(row)  # Simulates minimal computation
        return [1, 2, 3, 4]

    lengths = [8, 64, 128]
    results = _run_benchmark(dummy_algo, lengths, repeat=2)
    assert all(n in results for n in lengths)
    assert all(isinstance(t, float) for t in results.values())


def test_threshold_caching(tmp_path):
    """
    Test caching logic:
    - Save threshold after tuning
    - Reuse it on next call without re-benchmarking
    """
    from tuner import CONFIG_PATH

    test_config = tmp_path / "config.json"

    with mock.patch("tuner.CONFIG_PATH", str(test_config)):
        with mock.patch("tuner._system_fingerprint", return_value="TEST123"):
            with mock.patch("tuner._run_benchmark", return_value={32: 1.0, 64: 0.5}), \
                 mock.patch("tuner._find_crossover", return_value=64):

                # First call saves to file
                th = get_optimal_threshold(compute_moments_twopass,compute_moments_pebay,force_retune=True)
                assert th == 64
                assert test_config.exists()

                # Second call should reuse cache
                th2 = get_optimal_threshold(compute_moments_twopass,compute_moments_pebay,force_retune=False)
                assert th2 == 64


def test_threshold_bad_config(tmp_path):
    """
    Handle corrupted config file gracefully and re-run benchmark instead of crashing.
    """
    from tuner import CONFIG_PATH

    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{broken json")  # Invalid JSON

    with mock.patch("tuner.CONFIG_PATH", str(bad_file)), \
         mock.patch("tuner._system_fingerprint", return_value="X"), \
         mock.patch("tuner._run_benchmark", return_value={8: 1.0, 16: 0.5}), \
         mock.patch("tuner._find_crossover", return_value=16):

        threshold = get_optimal_threshold(compute_moments_twopass,compute_moments_pebay,force_retune=False)
        assert threshold == 16
