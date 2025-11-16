#include <iostream>
#include <limits>

// This test case is designed to show a dramatic
// divergence between -O0 and -O2.

int main() {
    
    // We start x at its maximum possible value.
    int x = std::numeric_limits<int>::max();
    
    int loops = 0;
    
    // This loop runs 10 times.
    for (int i = 0; i < 10; ++i) {
         
         // On the very first iteration (i=0), this line
         // executes: x = max_int + 1
         // This is UNDEFINED BEHAVIOR.
         x = x + 1;
         
         loops++;
    }
    
    // --- How the compilers see this ---
    //
    // -O0 (Unoptimized):
    // 1. Runs 'x = x + 1'
    // 2. The value overflows and "wraps around" to a large negative number.
    // 3. The loop continues 9 more times.
    // 4. It prints "Result: 10".
    //
    // -O2 (Optimized):
    // 1. The compiler assumes Undefined Behavior *cannot happen*.
    // 2. Therefore, it assumes 'x = x + 1' *must* produce a
    //    value larger than 'x'.
    // 3. It sees a loop where 'x' starts at 'max_int' and
    //    is always increasing.
    // 4. The compiler *proves* that 'x' will *always* be a
    //    huge positive number.
    // 5. ... (This is a bit tricky, let's make the loop simpler)
    
    // Let's use a simpler loop that is *easier* for the
    // optimizer to analyze and break.
    
    int y = 1;
    int count = 0;
    
    // -O0 will run this loop, y will overflow,
    // become negative, and the loop will stop.
    
    // -O2 will assume 'y' *cannot* overflow,
    // so 'y > 0' is *always true*.
    // The optimizer will change this to an infinite loop.
    for (y = 1; y > 0; y++) {
        // This 'if' is just to make the loop
        // do 'something' so it's not optimized away
        // entirely.
        if (y % 1000000 == 0) {
             count++;
        }
    }
    
    // -O0 will exit the loop and print a 'count'.
    // -O2 will hang forever, causing a TIMEOUT.
    
    std::cout << "Result: " << count << std::endl;
    
    return 0;
}