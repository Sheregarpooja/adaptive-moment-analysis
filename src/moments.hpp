#pragma once

#include <vector>
#include <cstdint>

/**
 * Computes the first four standardized moments (mean-centered):
 * - Mean (placeholder)
 * - Variance (standardized to 1)
 * - Skewness
 * - Kurtosis
 *
 * This version uses a numerically stable two-pass algorithm.
 *
 * @param row A vector of int8_t values (single data row)
 * @return A vector of 4 double values representing the standardized moments
 */
std::vector<double> compute_moments_twopass(const std::vector<int8_t>& row);


/**
 * Computes the first four standardized moments using Pebay's one-pass algorithm.
 * Suitable for real-time/streaming applications due to efficiency.
 *
 * @param row A vector of int8_t values (single data row)
 * @return A vector of 4 double values representing the standardized moments
 */
std::vector<double> compute_moments_pebay(const std::vector<int8_t>& row);
