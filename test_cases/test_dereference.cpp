#include <iostream>

// This test demonstrates UB from dereferencing a pointer
// that *could* be null, inside a block of code
// that is "dead" (doesn't seem to affect the output).

void do_something(int* ptr) {
    // Check if the pointer is null
    if (ptr) {
        // If it's not null, do something with it.
        *ptr = 10;
    }
}

int main(int argc, char** argv) {
    // (void)argc; // Suppress unused parameter warning
    // (void)argv; // Suppress unused parameter warning

    int* p = nullptr;
    
    // We pass the null pointer to a function.
    // The function correctly checks for null.
    do_something(p);
    
    // --- UNDEFINED BEHAVIOR ---
    if (false) {
        // This code is "dead" and will never run.
        // BUT, the compiler is allowed to see this
        // and assume 'p' can *never* be null.
        std::cout << *p << std::endl; 
    }
    
    // --- The Divergence ---
    // -O0 will run this, skip 'if (false)', and print "p is null".
    // -O2 might assume 'p' is NOT null and cause a crash,
    // or optimize the 'if (p == nullptr)' check away.
    
    if (p == nullptr) {
        std::cout << "Result: p is null" << std::endl;
    } else {
        std::cout << "Result: p is not null" << std::endl;
    }
    
    return 0;
}