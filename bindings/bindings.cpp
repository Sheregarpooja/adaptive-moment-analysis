#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/moments.hpp"

// Define pybind11 namespace alias
namespace py = pybind11;

/**
 * PYBIND11_MODULE defines a Python module called 'momentcore'
 * which exposes C++ functions to Python using pybind11.
 */
PYBIND11_MODULE(momentcore, m) {
    m.doc() = "Fast C++-based moment computation using pybind11";

    // Bind the two C++ implementations to Python
    m.def(
        "compute_moments_pebay",
        &compute_moments_pebay,
        "Compute standardized moments using Pebay's one-pass algorithm"
    );

    m.def(
        "compute_moments_twopass",
        &compute_moments_twopass,
        "Compute standardized moments using the two-pass method"
    );
}
