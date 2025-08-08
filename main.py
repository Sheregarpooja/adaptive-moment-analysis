#!/usr/bin/env python3

"""
main.py - CLI entry point for standardized moment computation.

This script reads a binary matrix file, computes the first four
standardized moments for each row, and optionally compares the
results with a provided expected output file.

Author: Pooja Sheregar
"""

import struct
import argparse
import numpy as np
import sys
from momentcore import compute_moments_twopass, compute_moments_pebay
from tuner import get_optimal_threshold


def read_binary_matrix(file_path):
    """
    Reads a binary file with format:
    [int32 M][int32 N][int8 x M*N matrix]

    Returns:
        np.ndarray: shape (M, N)
    """
    with open(file_path, "rb") as f:
        header = f.read(8)
        if len(header) < 8:
            raise ValueError("File too small to contain header.")

        M, N = struct.unpack("<ii", header)
        if M <= 0 or N <= 0:
            raise ValueError(f"Invalid matrix shape: ({M}, {N})")

        matrix = np.frombuffer(f.read(), dtype=np.int8)
        if matrix.size != M * N:
            raise ValueError("Mismatch between header shape and data length.")

        return matrix.reshape((M, N))


def read_expected_output(file_path):
    """
    Parses a plain text result file in format:
    Row 1: [x, x, x, x]
    ...
    Returns:
        List[List[float]]
    """
    expected = []
    with open(file_path, "r") as f:
        for line in f:
            if '[' in line and ']' in line:
                segment = line[line.find('[') + 1:line.find(']')]
                expected.append([round(float(v.strip()), 2) for v in segment.split(',') if v.strip()])
    return expected


def round_half_up(value):
    """Rounds float to 2 decimal places."""
    return float(f"{value:.2f}")


def compute_moment_rows(data, threshold):
    """
    Computes row-wise moments using adaptive algorithm.

    Returns:
        List[List[float]] with 4 rows (μ1-μ4)
    """
    results = [[] for _ in range(4)]
    for row in data:
        row_list = row.tolist()
        algo = compute_moments_twopass if len(row_list) < threshold else compute_moments_pebay
        row_moments = algo(row_list)

        for i in range(4):
            results[i].append(round_half_up(row_moments[i]))

    return results


def compare_outputs(computed, expected):
    """
    Compares computed output with expected and logs mismatches.

    Returns:
        bool: True if all values match, False otherwise
    """
    if len(computed) != len(expected):
        print("Row count mismatch between computed and expected.")
        return False

    matched = True
    for i in range(4):
        if len(computed[i]) != len(expected[i]):
            print(f"Row length mismatch at moment μ{i+1}.")
            matched = False
            continue

        mismatches = [
            (j, c, e) for j, (c, e) in enumerate(zip(computed[i], expected[i])) if abs(c - e) > 0.01
        ]
        if mismatches:
            print(f"Moment μ{i+1}: {len(mismatches)} mismatches")
            for j, c, e in mismatches[:5]:
                print(f"   Index {j}: computed={c:.2f}, expected={e:.2f}")
            matched = False
        else:
            print(f"Moment μ{i+1} matched.")

    return matched


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute standardized moments per row from a binary file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Path to input .bin file (required)")
    parser.add_argument("-o", "--output", type=str,
                        help="Optional expected result .txt file to compare")
    parser.add_argument("--retune", action="store_true",
                        help="Force benchmark threshold retuning")
    return parser.parse_args()


def main():
    try:
        args = parse_args()

        print(f"Reading binary input: {args.input}")
        data = read_binary_matrix(args.input)
        print(f" Loaded matrix of shape {data.shape}")

        threshold = get_optimal_threshold(
            compute_moments_twopass,
            compute_moments_pebay,
            force_retune=args.retune
        )
        print(f" Using threshold: {threshold}")

        results = compute_moment_rows(data, threshold)

        if args.output:
            print(f"Comparing with expected output: {args.output}")
            expected = read_expected_output(args.output)
            success = compare_outputs(results, expected)
            print("\n All rows matched!" if success else "\n Some mismatches found.")
        else:
            print("Computed standardized moments (μ1 to μ4):")
            for i, row in enumerate(results):
                print(f"μ{i+1}: {row}")

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()