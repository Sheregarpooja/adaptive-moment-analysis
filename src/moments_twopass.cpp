/**
 * Computes standardized moments using the two-pass algorithm:
 *   - First pass: compute mean
 *   - Second pass: compute variance, skewness, kurtosis
 *
 * Args:
 *   row: vector of int8_t values representing a single data row
 *
 * Returns:
 *   A vector<double> with 4 elements:
 *     [0]: Placeholder for mean (assumed zero-centered)
 *     [1]: Variance normalized to 1
 *     [2]: Skewness
 *     [3]: Kurtosis
 */
#include "moments.hpp"
#include <cmath>

std::vector<double> compute_moments_twopass(const std::vector<int8_t>& row) {
    size_t N = row.size();
    std::vector<double> result(4, 0.0);

    if (N == 0) return result;  // Handle empty input

    // First pass: compute mean
    double mean = 0.0;
    for (auto x : row) mean += x;
    mean /= N;

    // Second pass: compute variance
    double var_sum = 0.0;
    for (auto x : row)
        var_sum += (x - mean) * (x - mean);

    double std_dev = std::sqrt(var_sum / N);
    if (std_dev == 0.0)
        return result;  // Avoid division by zero

    // Compute third and fourth central moments
    double m3 = 0.0, m4 = 0.0;
    for (auto x : row) {
        double d = x - mean;
        m3 += d * d * d;
        m4 += d * d * d * d;
    }

    result[0] = 0.0;  // mean (unused)
    result[1] = 1.0;  // variance (standardized)
    result[2] = m3 / (N * std::pow(std_dev, 3));  // skewness
    result[3] = m4 / (N * std::pow(std_dev, 4));  // kurtosis

    return result;
}
