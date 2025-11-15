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
    int* p = nullptr;
    
    // We pass the null pointer to a function.
    // The function correctly checks for null.
    // This is safe, well-defined code.
    do_something(p);
    
    // --- UNDEFINED BEHAVIOR ---
    // The C++ standard says that if a program
    // *ever* dereferences a null pointer, the
    // *entire program* has Undefined Behavior,
    // even if that line of code is never reached!
    
    if (false) {
        // This code is "dead" and will never run.
        // BUT, the compiler is allowed to see this
        // and assume 'p' can *never* be null.
        std::cout << *p << std::endl; 
    }
    
    // --- The Divergence ---
    // An -O0 compiler will run the code line-by-line,
    // skip the 'if (false)' block, and print "p is null".
    
    // An -O2 compiler is allowed to assume 'p' is NOT null
    // (because of the *p in the dead code). It might
    // "optimize away" the 'if (ptr)' check in do_something()
    // and cause the program to crash.
    
    if (p == nullptr) {
        std::cout << "Result: p is null" << std.endl;
    } else {
        std::cout << "Result: p is not null" << std::endl;
    }
    
    return 0;
}