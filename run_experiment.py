import subprocess
import os
import json

# --- Configuration ---

# Define the C++ test case to run
CPP_TEST_FILE = "test_accumulate.cpp"

# Define the matrix of compilers and flags to test
# This maps to the "Experimental Matrix" in the report
CONFIGURATIONS = {
    "gcc_o0":,
    "gcc_o2":,
    "gcc_o3":,
    "clang_o0":,
    "clang_o2":,
    "clang_o3":,
    "clang_ubsan":,
}

# --- Helper Functions ---

def compile_test(config_name, compile_command):
    """
    Runs the compilation command for a given configuration.
    Returns True on success, False on failure.
    """
    print(f"--- Compiling: {config_name} ---")
    try:
        # Run the compile command (e.g., "g++ -O2 test.cpp -o test")
        subprocess.run(
            compile_command,
            check=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        print("Compile SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print("Compile FAILED")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred during compilation: {e}")
        return False

def run_test(executable_path):
    """
    Runs a compiled executable and captures its output.
    Returns a dictionary with stdout, stderr, and exit_code.
    """
    print(f"--- Running: {executable_path} ---")
    try:
        # Run the executable (e.g., "./test_gcc_o2")
        # Note: We add "./" to run the local executable
        result = subprocess.run(
            ["./" + executable_path],
            check=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        print("Run SUCCESS")
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except subprocess.CalledProcessError as e:
        # Program crashed or returned a non-zero exit code
        print("Run FAILED (non-zero exit or crash)")
        return {
            "stdout": e.stdout.strip(),
            "stderr": e.stderr.strip(),
            "exit_code": e.returncode
        }
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1
        }

def analyze_results(all_results):
    """
    Compares all results and prints a report.
    This is the core of the differential testing.
    """
    print("\n" + "="*30)
    print("  FINAL ANALYSIS & REPORT  ")
    print("="*30)

    # Use the first result as the "baseline" to compare against
    baseline_name, baseline_result = next(iter(all_results.items()))
    
    print(f"Baseline for comparison: {baseline_name}")
    print(json.dumps(baseline_result, indent=2))
    print("\n--- Checking for divergence ---")

    divergence_found = False
    for config_name, result in all_results.items():
        if config_name == baseline_name:
            continue
        
        # A divergence is any difference in stdout, stderr, or exit_code
        if result!= baseline_result:
            divergence_found = True
            print(f"\n[!!!] DIVERGENCE DETECTED: {config_name}")
            print(json.dumps(result, indent=2))

    if not divergence_found:
        print("\nAll configurations produced identical results.")

    # Specifically check the UBSan ("ground truth") run
    if "clang_ubsan" in all_results and all_results["clang_ubsan"]["stderr"]:
        print("\n--- UBSan (Ground Truth) Report ---")
        print("UBSan detected Undefined Behavior:")
        print(all_results["clang_ubsan"]["stderr"])

# --- Main Execution ---

def main():
    """
    Main function to orchestrate the entire experiment.
    """
    all_results = {}
    executables_to_clean =

    for config_name, compile_command in CONFIGURATIONS.items():
        print("\n" + "="*30)
        executable_path = compile_command[-1]
        executables_to_clean.append(executable_path)
        
        if compile_test(config_name, compile_command):
            # If compile succeeded, run the test
            result = run_test(executable_path)
            all_results[config_name] = result
        else:
            # If compile failed, log it
            all_results[config_name] = {"stdout": "COMPILE_ERROR", "stderr": "", "exit_code": -1}

    # Analyze the final results
    analyze_results(all_results)

    # Clean up compiled binaries
    print("\n--- Cleaning up ---")
    for exe in executables_to_clean:
        if os.path.exists(exe):
            os.remove(exe)
    print("Cleanup complete.")

if __name__ == "__main__":
    main()
