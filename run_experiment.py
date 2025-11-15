import subprocess
import os
import json
import glob

# --- Helper Functions ---

def get_configurations(cpp_file_path):
    """
    Generates the configuration matrix for a specific C++ test file.
    This function is generic and works for any file passed to it.
    """
    
    # Get the base name, e.g., "test_accumulate" from "test_cases/test_accumulate.cpp"
    base_name = os.path.basename(cpp_file_path).replace(".cpp", "")
    
    # Create a unique path for executables in the 'build' directory
    # e.g., "build/test_accumulate_gcc_o0"
    build_dir = "build"
    executable_path_prefix = os.path.join(build_dir, base_name)

    # Return the dictionary of all 7 compile commands for THIS file
    return {
        # --- GCC Configurations ---
        "gcc_o0":    ["g++", "-std=c++17", "-O0", "-Wall", "-Wextra", "-o", f"{executable_path_prefix}_gcc_o0", cpp_file_path],
        "gcc_o2":    ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-o", f"{executable_path_prefix}_gcc_o2", cpp_file_path],
        "gcc_o3":    ["g++", "-std=c++17", "-O3", "-Wall", "-Wextra", "-o", f"{executable_path_prefix}_gcc_o3", cpp_file_path],

        # --- Clang Configurations ---
        "clang_o0":  ["clang++", "-std=c++17", "-O0", "-Wall", "-Wextra", "-o", f"{executable_path_prefix}_clang_o0", cpp_file_path],
        "clang_o2":  ["clang++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-o", f"{executable_path_prefix}_clang_o2", cpp_file_path],
        "clang_o3":  ["clang++", "-std=c++17", "-O3", "-Wall", "-Wextra", "-o", f"{executable_path_prefix}_clang_o3", cpp_file_path],
        
        # --- Ground Truth Configuration (UBSan) ---
        "clang_ubsan": ["clang++", "-std=c++17", "-O0", "-fsanitize=undefined", "-o", f"{executable_path_prefix}_clang_ubsan", cpp_file_path],
    }

def compile_test(config_name, compile_command):
    """
    Runs the compilation command for a given configuration.
    Returns True on success, False on failure.
    """
    print(f"  --- Compiling: {config_name} ---")
    try:
        subprocess.run(
            compile_command,
            check=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        print("  Compile SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print("  Compile FAILED")
        print("  STDOUT:", e.stdout)
        print("  STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"  An unexpected error occurred during compilation: {e}")
        return False

def run_test(executable_path):
    """
    Runs a compiled executable and captures its output.
    Returns a dictionary with stdout, stderr, and exit_code.
    """
    print(f"  --- Running: {executable_path} ---")
    try:
        # Run the executable using its full path
        result = subprocess.run(
            [executable_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("  Run FINISHED")
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except Exception as e:
        print(f"  An unexpected error occurred during execution: {e}")
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1
        }

def analyze_results(test_file, all_results):
    """
    Compares all results for a single test file and prints a report.
    """
    print("\n" + "="*30)
    print(f"   FINAL ANALYSIS: {test_file}   ")
    print("="*30)

    if not all_results:
        print("No results to analyze.")
        return

    baseline_name, baseline_result = next(iter(all_results.items()))
    
    print(f"Baseline for comparison: {baseline_name}")
    print(json.dumps(baseline_result, indent=2))
    print("\n  --- Checking for divergence ---")

    divergence_found = False
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    NC = '\033[0m' # No Color

    for config_name, result in all_results.items():
        if config_name == baseline_name:
            continue
        
        # A divergence is any difference in stdout, stderr, or exit_code
        if result != baseline_result:
            divergence_found = True
            print(f"\n{RED}[!!!] DIVERGENCE DETECTED: {config_name}{NC}")
            print(json.dumps(result, indent=2))

    if not divergence_found:
        print(f"\n{GREEN}All configurations (excluding UBSan) produced identical results.{NC}")

    # Specifically check the UBSan ("ground truth") run
    if "clang_ubsan" in all_results and all_results["clang_ubsan"]["stderr"]:
        print(f"\n  --- UBSan (Ground Truth) Report ---")
        print(f"{RED}UBSan detected Undefined Behavior:{NC}")
        print(all_results["clang_ubsan"]["stderr"])
    elif "clang_ubsan" in all_results:
        print(f"\n  --- UBSan (Ground Truth) Report ---")
        print(f"{GREEN}UBSan did not detect UndDeltaBehavior.{NC}")
    
    print("="*30 + "\n")

def cleanup_files(executables_to_clean):
    """
    Removes all generated executables.
    """
    print("  --- Cleaning up ---")
    for exe in executables_to_clean:
        if os.path.exists(exe):
            try:
                os.remove(exe)
                # print(f"  Removed {exe}") # Keep this quiet
            except OSError as e:
                print(f"  Error removing {exe}: {e}")
    # print("  Cleanup complete.")

# --- Main Execution ---

def main():
    """
    Main function to find all test cases and orchestrate the experiments.
    """
    test_dir = "test_cases"
    build_dir = "build"

    # Find all .cpp files in the 'test_cases' directory
    test_files_pattern = os.path.join(test_dir, "*.cpp")
    test_files = glob.glob(test_files_pattern)
    
    if not test_files:
        print(f"Error: No test cases found in '{test_dir}/' directory.")
        print(f"Please create a '{test_dir}' folder and add your .cpp test files.")
        return

    # Create a 'build' directory to store executables
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
        print(f"Created directory: {build_dir}")

    print(f"Found {len(test_files)} test case(s). Starting experiments...")
    
    all_executables = []

    for test_file in test_files:
        print("\n" + "#"*40)
        print(f"STARTING EXPERIMENT FOR: {test_file}")
        print("#"*40)

        all_results = {}
        
        # Get the 7 compiler configurations FOR THIS SPECIFIC FILE
        configurations = get_configurations(test_file)
        
        # Collect all executable names for final cleanup
        file_executables = [cmd[-2] for cmd in configurations.values()]
        all_executables.extend(file_executables)

        for config_name, compile_command in configurations.items():
            executable_path = compile_command[-2] # e.g., "build/test_accumulate_gcc_o0"
            
            if compile_test(config_name, compile_command):
                result = run_test(executable_path)
                all_results[config_name] = result
            else:
                all_results[config_name] = {"stdout": "COMPILE_ERROR", "stderr": "", "exit_code": -1}

        analyze_results(test_file, all_results)

    # Clean up all generated executables at the very end
    cleanup_files(all_executables)
    print("\nAll experiments complete.")

if __name__ == "__main__":
    main()
