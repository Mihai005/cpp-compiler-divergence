#include <iostream>
#include <numeric>
#include <vector>
#include <limits>

/**
 * @brief This program tests for divergent behavior on signed integer overflow.
 *
 * It uses std::accumulate to sum INT_MAX and 1. The C++ standard
 * defines signed integer overflow as Undefined Behavior.
 *
 * We will compile and run this program with different compilers and
 * optimization levels to observe if their behavior diverges.
 */
int main() {
    // Create a vector containing INT_MAX and 1
    std::vector<int> values;
    values.push_back(std::numeric_limits<int>::max());
    values.push_back(1);

    // Use std::accumulate to sum the values.
    // This operation invokes Undefined Behavior.
    int result = std::accumulate(values.begin(), values.end(), 0);

    // Print the result to standard output.
    // The differential testing tool will capture this output.
    std::cout << "Result: " << result << std::endl;

    return 0;
}