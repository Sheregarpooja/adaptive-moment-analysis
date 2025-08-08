import os
import struct
import tempfile
import numpy as np

from main import compute_moment_rows, read_binary_matrix
from momentcore import compute_moments_twopass, compute_moments_pebay
from tuner import get_optimal_threshold

# Force benchmarking at the start to get a reliable threshold
threshold = get_optimal_threshold(compute_moments_twopass,compute_moments_pebay,force_retune=True)


def write_bin_file(path, matrix):
    """
    Write a binary matrix to file in the expected format:
    [int32 M][int32 N][int8 * M*N matrix]

    Args:
        path (str): Output file path
        matrix (np.ndarray): Matrix of shape (M, N)
    """
    rows, cols = matrix.shape
    with open(path, "wb") as f:
        f.write(struct.pack("<ii", rows, cols))
        f.write(matrix.astype(np.int8).tobytes())


def test_large_tall_matrix():
    """
    Test moment computation on a very tall matrix (many rows, few columns).
    """
    mat = np.random.randint(-128, 127, size=(50000, 10), dtype=np.int8)
    with tempfile.NamedTemporaryFile(delete=False) as f:
        write_bin_file(f.name, mat)
        data = read_binary_matrix(f.name)
        result = compute_moment_rows(data, threshold)
        assert len(result) == 4  # Four standardized moments
        assert all(len(row) == 50000 for row in result)


def test_large_wide_matrix():
    """
    Test moment computation on a very wide matrix (few rows, many columns).
    """
    mat = np.random.randint(-128, 127, size=(10, 50000), dtype=np.int8)
    with tempfile.NamedTemporaryFile(delete=False) as f:
        write_bin_file(f.name, mat)
        data = read_binary_matrix(f.name)
        result = compute_moment_rows(data, threshold)
        assert len(result) == 4
        assert all(len(row) == 10 for row in result)


def test_large_square_matrix():
    """
    Test moment computation on a large square matrix (2000 x 2000).
    """
    mat = np.random.randint(-128, 127, size=(2000, 2000), dtype=np.int8)
    with tempfile.NamedTemporaryFile(delete=False) as f:
        write_bin_file(f.name, mat)
        data = read_binary_matrix(f.name)
        result = compute_moment_rows(data, threshold)
        assert len(result) == 4
        assert all(len(row) == 2000 for row in result)
