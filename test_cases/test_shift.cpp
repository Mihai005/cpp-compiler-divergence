#include <iostream>

// This test case checks for Undefined Behavior from
// left-shifting a negative number.

int main() {
    int negative_value = -100;
    
    // <-- UNDEFINED BEHAVIOR HERE
    // The C++ standard says left-shifting a negative
    // number is Undefined Behavior.
    int result = negative_value << 2;
    
    // Unoptimized compilers might output -400.
    // Optimized compilers might output something else entirely.
    // UBSan will report an error.
    
    std::cout << "Result: " << result << std::endl;
    
    return 0;
}