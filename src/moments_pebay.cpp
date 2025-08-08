/**
 * Computes the first four standardized moments (mean-centered variance,
 * skewness, kurtosis) using Pebay's one-pass algorithm.
 *
 * This approach allows efficient computation without multiple passes over data.
 *
 * Args:
 *   row: a vector of int8_t values representing a data row
 *
 * Returns:
 *   A vector<double> with 4 elements:
 *     [0]: Placeholder (mean assumed zero)
 *     [1]: Normalized variance (standardized to 1)
 *     [2]: Skewness
 *     [3]: Kurtosis
 */
#include "moments.hpp"
#include <cmath>

std::vector<double> compute_moments_pebay(const std::vector<int8_t>& row) {
    std::vector<double> result(4, 0.0);

    size_t N = 0;
    double M1 = 0.0, M2 = 0.0, M3 = 0.0, M4 = 0.0;

    for (double x : row) {
        N++;

        double delta = x - M1;
        double delta_n = delta / N;
        double delta_n2 = delta_n * delta_n;
        double term1 = delta * delta_n * (N - 1);

        // Recursive one-pass updates for moments
        M4 += term1 * delta_n2 * (N * N - 3 * N + 3) + 6 * delta_n2 * M2 - 4 * delta_n * M3;
        M3 += term1 * delta_n * (N - 2) - 3 * delta_n * M2;
        M2 += term1;
        M1 += delta_n;
    }

    if (N == 0 || M2 == 0.0)
        return result;  // Avoid division by zero

    // Normalize and return skewness and kurtosis
    result[0] = 0.0;  // mean placeholder
    result[1] = 1.0;  // variance standardized
    result[2] = std::sqrt(N) * M3 / std::pow(M2, 1.5);  // skewness
    result[3] = (N * M4) / (M2 * M2);                  // kurtosis

    return result;
}
