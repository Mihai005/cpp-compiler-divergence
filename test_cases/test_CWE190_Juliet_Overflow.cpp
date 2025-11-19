#include <iostream>
#include <limits.h>

// ADAPTED FROM: NIST Juliet Test Suite v1.3
// CWE-190: Integer Overflow or Wraparound
// Source: CWE190_Integer_Overflow__int_fscanf_add_01.c

void printLine(const char * line) {
    std::cout << line << std::endl;
}

void bad() {
    int data;
    // Initialize data
    data = 0;
    
    // POTENTIAL FLAW: This value is very close to INT_MAX
    // In a real Juliet test, this might come from 'fscanf'
    data = INT_MAX - 5;

    // POTENTIAL FLAW: Adding a value that causes overflow
    // The C++ standard says this is Undefined Behavior.
    int result = data + 10;

    std::cout << "Result: " << result << std::endl;
}

int main() {
    printLine("Calling bad()...");
    bad();
    printLine("Finished bad()");
    return 0;
}