import pytest
import tempfile
import struct
import numpy as np

from main import (
    read_binary_matrix,
    read_expected_output,
    compare_outputs,
    compute_moment_rows
)
from momentcore import compute_moments_twopass, compute_moments_pebay


def create_test_bin_file(M, N, fill_func):
    """
    Create a temporary binary file representing a matrix of shape (M, N)
    where values are populated using the provided fill_func(i, j).

    Returns:
        str: Path to the temporary binary file.
    """
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(struct.pack("<ii", M, N))  # Write header
        for i in range(M):
            for j in range(N):
                val = fill_func(i, j)
                f.write(struct.pack("b", val))  # Write int8 value
        return f.name


def create_test_output_file(data):
    """
    Create a temporary plain-text file with given expected output.

    Returns:
        str: Path to the temporary .txt file.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        for row in data:
            f.write(str(row) + "\n")
        return f.name


# ---------- Unit Tests ----------

def test_read_binary_matrix_valid():
    """Test reading a valid binary matrix."""
    bin_file = create_test_bin_file(3, 4, lambda i, j: (i + j) % 128 - 64)
    matrix = read_binary_matrix(bin_file)
    assert matrix.shape == (3, 4)
    assert matrix.dtype == np.int8


def test_read_binary_matrix_invalid_header():
    """Test behavior when binary header is too short."""
    with tempfile.NamedTemporaryFile("wb", delete=False) as f:
        f.write(b"1234")  # 4 bytes instead of 8
    with pytest.raises(ValueError):
        read_binary_matrix(f.name)


def test_read_binary_matrix_mismatch_data():
    """Test when binary data doesn't match shape declared in header."""
    with tempfile.NamedTemporaryFile("wb", delete=False) as f:
        f.write(struct.pack("<ii", 2, 2))  # M=2, N=2
        f.write(b"\x01\x02")  # Only 2 bytes instead of 4
    with pytest.raises(ValueError):
        read_binary_matrix(f.name)


def test_compute_moments_manual():
    """
    Manually test moment calculation logic.
    Should dispatch to two-pass because threshold = 10.
    """
    matrix = np.array([
        [1, 2, 3],
        [4, 5, 6]
    ], dtype=np.int8)
    threshold = 10  # Force use of two-pass method
    result = compute_moment_rows(matrix, threshold)
    assert len(result) == 4  # Should return 4 moments
    assert all(len(r) == 2 for r in result)  # Each row should have 2 values


def test_compare_outputs_matching():
    """Test comparison utility when outputs match."""
    computed = [[1.0, 2.0], [1.1, 2.2], [1.2, 2.2], [1.3, 2.3]]
    expected = [[1.0, 2.0], [1.1, 2.2], [1.2, 2.2], [1.3, 2.3]]
    assert compare_outputs(computed, expected) is True


def test_compare_outputs_mismatch():
    """Test comparison utility when outputs mismatch."""
    computed = [[1.0, 2.0], [1.1, 2.2], [1.2, 2.2], [1.3, 2.3]]
    expected = [[1.0, 9.9], [1.1, 2.2], [1.2, 2.2], [1.3, 2.3]]
    assert compare_outputs(computed, expected) is False


def test_read_expected_output():
    """Test parsing of expected output from plain-text format."""
    data = [[1.23, 2.34], [3.45, 4.56], [5.67, 6.78], [7.89, 8.90]]
    txt_path = create_test_output_file(data)
    output = read_expected_output(txt_path)
    assert output == data
