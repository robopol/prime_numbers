import tkinter as tk
from tkinter import messagebox
import sympy
import math
import multiprocessing
import gmpy2
from gmpy2 import mpz, powmod, log2, is_prime
from concurrent.futures import ProcessPoolExecutor
import random
import time
import concurrent.futures
from tkinter import ttk

# Initialize gmpy2 random state for better randomness across runs
gmpy2.random_state(int(time.time()))

# List of known exponents p for Mersenne primes (M_p = 2^p - 1)
# Source: https://www.mersenne.org/primes/ (GIMPS) - as of October 2024
KNOWN_MERSENNE_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281, 3217, 4253, 4423,
    9689, 9941, 11213, 19937, 21701, 23209, 44497, 86243, 110503, 132049, 216091, 756839,
    859433, 1257787, 1398269, 2976221, 3021377, 6972593, 13466917, 20996011, 24036583,
    25964951, 30402457, 32582657, 37156667, 42643801, 43112609, 57885161, 74207281,
    77232917, 82589933, 136279841
}

PROGRESS_BAR_MAX = 100 # Define a global variable for the progress bar maximum

# Helper function to update the result_text_area (defined later, but declared here for clarity if needed or move definition up)
# This will be defined near the GUI section later.
# def update_result_text(new_text): pass 

# -------------------  LOGIC  -------------------

# New function to check for a direct text expression of a Mersenne prime
def check_direct_mersenne_expression(input_str_raw, start_time_check, root_widget, progress_bar_widget):
    cleaned_input_str = input_str_raw.replace(" ", "").lower() # Remove spaces and convert to lowercase
    P_EXPONENT_THRESHOLD_FOR_DISPLAY = 127 # Threshold for p above which we don't print the full M_p value

    for p_exponent in KNOWN_MERSENNE_EXPONENTS:
        expected_forms = [
            f"2**{p_exponent}-1",
            f"pow(2,{p_exponent})-1"
        ]
        if cleaned_input_str in expected_forms:
            end_time_check = time.time()
            if p_exponent > P_EXPONENT_THRESHOLD_FOR_DISPLAY:
                result_text_direct = f"Input expression '{input_str_raw}' corresponds to M_{p_exponent}.\nThis is a known Mersenne Prime."
            else:
                try:
                    mersenne_value_mpz = mpz(2)**p_exponent - 1
                    result_text_direct = f"Input expression '{input_str_raw}' corresponds to M_{p_exponent} = {mersenne_value_mpz}.\nThis is a known Mersenne Prime."
                except OverflowError:
                    result_text_direct = f"Input expression '{input_str_raw}' corresponds to M_{p_exponent}.\nThis is a known Mersenne Prime (value calculation issue)."
            
            update_result_text(f"{result_text_direct}\n(Verified by direct expression match in {end_time_check - start_time_check:.4f} seconds)") # MODIFIED: Use helper
            if progress_bar_widget:
                progress_bar_widget['value'] = PROGRESS_BAR_MAX
            root_widget.update_idletasks()
            return True
    return False

big_num = 10**20
basic_field = [2, 3, 5, 7, 11, 13]
big_num2 = 10**12

def check_known_mersenne_primes(n_mpz, start_time_check, root_widget, progress_bar_widget):
    """
    Checks if the given number n_mpz is a known Mersenne prime
    by direct comparison with M_p = 2^p - 1 for known exponents p.
    If yes, updates the GUI and returns True. Otherwise returns False.
    n_mpz is expected to be gmpy2.mpz.
    root_widget is the main window for update_idletasks.
    progress_bar_widget is the progress bar widget.
    """
    if n_mpz <= 7: 
        return False

    for p_exponent in KNOWN_MERSENNE_EXPONENTS: 
        try:
            power_of_2 = mpz(2)**p_exponent
            mersenne_candidate = power_of_2 - 1
        except OverflowError: 
            continue 

        if n_mpz == mersenne_candidate:
            end_time_check = time.time()
            update_result_text(f"{n_mpz} is a known Mersenne Prime (M{p_exponent}).\n(Verified in {end_time_check - start_time_check:.4f} seconds)") # MODIFIED: Use helper
            if progress_bar_widget: 
                progress_bar_widget['value'] = PROGRESS_BAR_MAX
            root_widget.update_idletasks()
            return True
    return False

def classical_filter(n):
    """
    A simple filtering function: checks divisibility by the small primes
    in basic_field and looks for divisors of the form 6k±1 up to sqrt(big_num2).
    If a divisor is found, returns a string indicating the divisor.
    Otherwise, returns None.
    """
    for divisor in basic_field:
        if n % divisor == 0 and n != divisor:
            return f"Number is composite, divisible by {divisor}"
    k = 1
    end = round(math.sqrt(big_num2)) + 1
    while True:
        divisor1 = 6 * k - 1
        divisor2 = 6 * k + 1
        if divisor1 > end:
            break
        if n % divisor1 == 0 and n != divisor1:
            return f"Number is composite, divisible by {divisor1}"
        if n % divisor2 == 0 and n != divisor2:
            return f"Number is composite, divisible by {divisor2}"
        k += 1
    return None

def euler_test_single_base(args):
    """
    Performs an Euler-based primality test for a given number n and base a.
    Checks if a^((n-1)/2) % n is 1 or n-1 (Euler's criterion).
    Returns (base, True) if the condition holds, (base, False) otherwise.
    n_mpz and a_mpz are expected to be gmpy2.mpz objects.
    """
    n_mpz, a_mpz = args

    # Euler's criterion applies to odd n. n=2 is prime and handled earlier.
    # Base a must be > 1 and < n, and gcd(a,n) must be 1.
    if n_mpz <= 2 or n_mpz % 2 == 0:
        return (int(a_mpz), False) 
    if not (1 < a_mpz < n_mpz):
        return (int(a_mpz), False) 
    if gmpy2.gcd(a_mpz, n_mpz) != 1:
        return (int(a_mpz), False) # n is composite if a shares a factor (and a < n)

    exponent = (n_mpz - 1) // 2
    try:
        x = powmod(a_mpz, exponent, n_mpz)
    except ValueError: # Should be very rare given the checks above
        return (int(a_mpz), False)

    # Check if x is 1 or n-1 (which is congruent to -1 mod n_mpz)
    if x == 1 or x == (n_mpz - 1):
        return (int(a_mpz), True)
    else:
        return (int(a_mpz), False)

def run_euler_tests_parallel(n_mpz, bases_int_list, progress_bar_widget, root_widget, start_percentage):
    """
    Runs the Euler-based primality test in parallel for multiple bases.
    n_mpz: The number to test (gmpy2.mpz).
    bases_int_list: A list of integer bases to test.
    Updates a progress bar during execution.
    Returns a list of (base, pass/fail) tuples.
    """
    # Prepare arguments for the pool, ensuring bases are valid for the test with n_mpz
    args_for_pool = []
    for b_int in bases_int_list:
        if 1 < b_int < n_mpz: # Base must be > 1 and < n
            # Further check: gcd(b_int, n_mpz) == 1 for Euler's criterion
            # This is handled inside euler_test_single_base now, so we can pass it.
            args_for_pool.append((n_mpz, mpz(b_int)))
    
    results_from_pool = []
    if not args_for_pool: 
        # This can happen if n_mpz is very small (e.g., 3) and all default_bases are >= n_mpz
        # Or if the user_provided base is also unsuitable.
        # The check_prime function should handle very small n before calling this.
        return results_from_pool 
        
    num_bases = len(args_for_pool)
    bases_processed = 0
    progress_range = PROGRESS_BAR_MAX - start_percentage

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        future_to_base_arg = {executor.submit(euler_test_single_base, arg_pair): arg_pair for arg_pair in args_for_pool}
        
        for future in concurrent.futures.as_completed(future_to_base_arg):
            original_arg_pair = future_to_base_arg[future]
            # base_tested_mpz = original_arg_pair[1] # This is the mpz version of the base
            try:
                result_tuple = future.result() # (int_base, bool_passed)
                results_from_pool.append(result_tuple) 
            except Exception as exc:
                # print(f"Error in Euler test worker for base {int(base_tested_mpz)}: {exc}")
                # If a worker process dies or has an unhandled error, record failure for that base.
                results_from_pool.append((int(original_arg_pair[1]), False)) # Use the original base for reporting
            
            bases_processed += 1
            if num_bases > 0:
                 current_progress = start_percentage + int((bases_processed / num_bases) * progress_range)
                 if progress_bar_widget:
                     progress_bar_widget['value'] = current_progress
            if root_widget:
                 root_widget.update_idletasks()

    return sorted(results_from_pool, key=lambda x: x[0])

def parse_input_to_int(input_str):
    """
    Parses an input string (number or mathematical expression) using sympy.
    Returns an integer or None on error (and shows a messagebox).
    """
    try:
        number_expr = sympy.sympify(input_str)
        if not number_expr.is_number:
            messagebox.showerror("Input Error", f"Expression '{input_str}' did not evaluate to a number.")
            return None
        number_int = int(number_expr) 
    except Exception as e:
        messagebox.showerror("Input Error", f"Could not parse '{input_str}'. Please insert a valid integer or mathematical expression.\nDetails: {e}")
        return None
    return number_int

def get_input(): 
    """
    Reads a number (or mathematical expression) from the text field
    and attempts to parse it with sympy. Returns an integer or None on error.
    """
    input_string = text_number.get("1.0", tk.END).strip()
    return parse_input_to_int(input_string)

def parse_bases_input(bases_input_str, n_mpz_for_random_generation):
    """
    Parses the bases input string.
    Returns a list of integer bases or None on error.
    If bases_input_str is empty, returns a list of DEFAULT_NUM_RANDOM_BASES random bases.
    If bases_input_str is a single number, it's treated as the count of random bases.
    If bases_input_str is a comma-separated list, it's treated as a list of specific bases.
    n_mpz_for_random_generation is used to determine the range for random bases.
    """
    DEFAULT_NUM_RANDOM_BASES = 7
    bases_to_test = []

    if not bases_input_str: # Empty input, use default number of random bases
        num_random_bases_to_generate = DEFAULT_NUM_RANDOM_BASES
    elif ',' in bases_input_str: # Comma-separated list of specific bases
        try:
            bases_to_test = [int(b.strip()) for b in bases_input_str.split(',') if b.strip()]
            if not bases_to_test: # e.g. input was just "," or ",,"
                messagebox.showerror("Input Error", "Invalid list of bases provided.")
                return None
            for b in bases_to_test:
                if b <= 1: # Bases must be > 1
                    messagebox.showerror("Input Error", f"Invalid base: {b}. Bases must be greater than 1.")
                    return None
                # We don't check b < n_mpz here, as n_mpz might not be fully determined when this is first called for GUI update
                # This check (b < n) is done before adding to args_for_pool in run_euler_tests_parallel
            return bases_to_test
        except ValueError:
            messagebox.showerror("Input Error", "Invalid format for bases. Please use comma-separated integers (e.g., 2,3,5) or a single number for random bases count.")
            return None
    else: # Single number, treat as count of random bases
        try:
            num_random_bases_to_generate = int(bases_input_str)
            if num_random_bases_to_generate <= 0:
                messagebox.showerror("Input Error", "Number of random bases must be a positive integer.")
                return None
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input for bases. Please enter a number (for random bases count) or a comma-separated list of bases.")
            return None

    # Generate random bases if num_random_bases_to_generate is set
    if num_random_bases_to_generate > 0:
        if n_mpz_for_random_generation is None or n_mpz_for_random_generation <= 3:
            # Not enough range for random bases or n is too small for meaningful test with random bases
            # Fallback to a sensible default if possible, or indicate an issue.
            # If n is 2 or 3, it's usually handled before this point (is_prime check).
            # For n=3, only base 2 is possible for Euler if we strictly follow a < n-1 for random.
            # Let's rely on the checks in run_euler_tests_parallel to filter unsuitable bases later.
            # Here, we'll just try to generate if the count is positive.
            # If n is very small, the set of unique random bases might be small.
            pass # No specific error here, let later stages handle small n.

        # Max possible unique bases are (n-2) - 2 + 1 = n-3, for bases in [2, n-2]
        # (n_mpz - 1) is upper bound for random_state, n_mpz-3 is the count of numbers in [2, n-2]
        # Range for random bases: [2, n-2]. So, n-1 must be >= 2 for gmpy2.mpz_random.
        # And n-3 must be > 0 for mpz_random to have a range.
        
        max_possible_unique_random_bases = 0
        if n_mpz_for_random_generation > 3: # mpz(3) - 3 = 0, so n must be > 3
             max_possible_unique_random_bases = int(n_mpz_for_random_generation - 3)


        actual_bases_to_generate = min(num_random_bases_to_generate, max_possible_unique_random_bases)
        
        if actual_bases_to_generate <= 0 and num_random_bases_to_generate > 0 and n_mpz_for_random_generation > 3 :
             messagebox.showwarning("Bases Warning", f"Cannot generate {num_random_bases_to_generate} random bases for n={n_mpz_for_random_generation}. Not enough unique options.")
             # We might still proceed if some default bases can be used or if user insists.
             # For now, let's return empty if we can't generate what's asked.
             # Or should we return a default like [2] if n is 3?
             # The calling function check_prime will handle this better with its existing logic.
             # Let's return an empty list, and check_prime can decide to use default_small_primes_bases if needed.
             return [] # Indicates couldn't generate requested randoms.

        generated_bases_set = set()
        # Ensure random_state is initialized, (done globally now)

        if actual_bases_to_generate > 0:
            attempts = 0
            # Generous max_attempts, especially if n is huge and collisions are truly unlikely.
            # If actual_bases_to_generate is small (e.g. 7), this is 700.
            MAX_GENERATION_ATTEMPTS = actual_bases_to_generate * 100 

            # Get the current random state object ONCE before the loop
            current_random_state = gmpy2.random_state()

            while len(generated_bases_set) < actual_bases_to_generate and attempts < MAX_GENERATION_ATTEMPTS:
                # Generate random base in [2, n-2]
                # mpz_random(state, limit) generates in [0, limit-1]
                # So, limit should be (n-2) - 2 + 1 = n-3 (value of n_mpz_for_random_generation - 3)
                # And then add 2 to shift to [2, n-2]
                if n_mpz_for_random_generation - 3 > 0 : # ensure limit for mpz_random is positive
                    # mpz_random's second arg is an exclusive upper bound for generated numbers starting from 0.
                    # So, mpz_random(state, X) gives numbers in [0, X-1].
                    # We want numbers in [2, n-2]. The size of this range is (n-2) - 2 + 1 = n-3.
                    # So we generate a random number in [0, (n-3)-1] i.e. [0, n-4]
                    # by calling mpz_random(state, n-3).
                    # Then we add 2 to this result, to get a range of [2, n-4+2] = [2, n-2].
                    # Pass the SAME state object to each call
                    rand_base_mpz = gmpy2.mpz_random(current_random_state, n_mpz_for_random_generation - 3) + mpz(2)
                    generated_bases_set.add(int(rand_base_mpz)) # Store as int
                else:
                    # This case (n_mpz_for_random_generation - 3 <= 0) implies n <= 3.
                    # If n=3, max_possible_unique_random_bases is 0, so actual_bases_to_generate should be 0.
                    # This loop (actual_bases_to_generate > 0) should not run for n <= 3 normally.
                    # Breaking here is a safeguard if somehow entered.
                    break 
                attempts += 1
            
            # Warning message if not enough unique bases were generated
            # Show warning only if we intended to generate some, and generated less than planned from the request.
            if len(generated_bases_set) < actual_bases_to_generate and actual_bases_to_generate > 0:
                 messagebox.showwarning("Bases Warning", f"Could only generate {len(generated_bases_set)} unique random bases out of {actual_bases_to_generate} planned (from {num_random_bases_to_generate} requested for n). Max attempts: {attempts}.")
            elif len(generated_bases_set) < num_random_bases_to_generate and num_random_bases_to_generate == actual_bases_to_generate and actual_bases_to_generate > 0:
                 # This case is for when max_possible_unique_random_bases was not a constraint, but we still failed to generate num_random_bases_to_generate
                 messagebox.showwarning("Bases Warning", f"Could only generate {len(generated_bases_set)} unique random bases out of {num_random_bases_to_generate} requested for n. Max attempts: {attempts}.")

        bases_to_test = sorted(list(generated_bases_set))
        
    return bases_to_test

def check_prime():
    """
    Main function triggered by the 'Check Prime' button.
    Obtains the number n, decides on the testing method, and displays the result.
    """
    input_string_n = text_number.get("1.0", tk.END).strip()

    if not input_string_n:
        return
    if input_string_n == "0":
        root.quit()
        return

    start_time_overall = time.time()

    # Update progress bar immediately for responsiveness
    if progress_bar:
        progress_bar['value'] = 0
    root.update_idletasks()

    if check_direct_mersenne_expression(input_string_n, start_time_overall, root, progress_bar):
        return

    n_mpz = parse_input_to_mpz(input_string_n) # Changed from parse_input_to_int to get mpz directly

    if n_mpz is None:
        if progress_bar: progress_bar['value'] = 0
        return # Error already shown by parse_input_to_mpz

    # Handle n=0, n=1, n=negative (already handled by parse_input_to_mpz if it returns None for these)
    # but if parse_input_to_mpz is lenient:
    if n_mpz <= 0:
        update_result_text(f"The number must be a positive integer greater than 0 for primality testing.")
        if progress_bar: progress_bar['value'] = 0
        return
    if n_mpz == 1:
        update_result_text("1 is neither prime nor composite (by definition).")
        if progress_bar: progress_bar['value'] = 0
        return
        
    # Initial progress update
    current_progress_val = 5
    if progress_bar:
        progress_bar['value'] = current_progress_val
    root.update_idletasks()

    # Step 0: Direct check with gmpy2.is_prime() for small numbers or as a quick path
    # For very large numbers, is_prime() itself can be slow as it's deterministic.
    # Let's use it for smaller numbers for speed and accuracy.
    # Threshold can be adjusted. For numbers > IS_PRIME_THRESHOLD, use our probabilistic method.
    IS_PRIME_THRESHOLD = 10**6 # Example threshold
    
    if n_mpz < IS_PRIME_THRESHOLD:
        is_prime_gmpy_result = gmpy2.is_prime(n_mpz)
        end_time_check = time.time()
        result_str = "prime" if is_prime_gmpy_result else "composite"
        method_str = "gmpy2.is_prime()"
        if n_mpz == 2 or n_mpz == 3 or n_mpz == 5 or n_mpz == 7: # Smallest primes
             result_str = "prime" # Ensure they are marked prime
        elif n_mpz % 2 == 0 and n_mpz > 2:
            result_str = "composite, divisible by 2"
        elif n_mpz % 3 == 0 and n_mpz > 3:
            result_str = "composite, divisible by 3"
        elif n_mpz % 5 == 0 and n_mpz > 5:
             result_str = "composite, divisible by 5"
        elif n_mpz % 7 == 0 and n_mpz > 7:
             result_str = "composite, divisible by 7"
             
        update_result_text(f"The number is {result_str}.\n(Verified by {method_str} in {end_time_check - start_time_overall:.4f} seconds)")
        if progress_bar: progress_bar['value'] = PROGRESS_BAR_MAX
        return

    # Step 0.5: Check against known Mersenne primes by value (if not caught by direct expression)
    if check_known_mersenne_primes(n_mpz, start_time_overall, root, progress_bar):
        return
        
    current_progress_val = 10
    if progress_bar: progress_bar['value'] = current_progress_val
    root.update_idletasks()

    # Step 1: Classical Filter
    filter_result = classical_filter(n_mpz) # classical_filter expects mpz
    if filter_result:
        end_time_check = time.time()
        update_result_text(f"{filter_result}.\n(Verified by classical filter in {end_time_check - start_time_overall:.4f} seconds)")
        if progress_bar: progress_bar['value'] = PROGRESS_BAR_MAX
        return

    current_progress_val = 25
    if progress_bar: progress_bar['value'] = current_progress_val
    root.update_idletasks()
    
    # Step 2: Parse bases for Euler Test
    bases_input_str = entry_a.get().strip()
    # Pass n_mpz to parse_bases_input for random generation range.
    selected_bases_int_list = parse_bases_input(bases_input_str, n_mpz)

    if selected_bases_int_list is None: # Error in parsing bases
        if progress_bar: progress_bar['value'] = 0 # Reset progress
        # Error message already shown by parse_bases_input
        return

    # If parse_bases_input returned empty (e.g. couldn't generate randoms for small n),
    # and we still want to proceed, we might use a default set of small primes.
    # This logic can be refined. For now, if it's empty, let's try small primes.
    if not selected_bases_int_list and n_mpz > 3 : # n_mpz > 3 ensures there's at least base 2 to test
        # Fallback to a few small prime bases if random generation failed or wasn't requested robustly for small n
        # This ensures we at least try something if input was e.g. "1" random base for n=4
        # Default small primes
        default_small_primes_bases = [2, 3, 5, 7, 11, 13, 17]
        # Filter them to be < n_mpz
        selected_bases_int_list = [b for b in default_small_primes_bases if b < n_mpz]
        if not selected_bases_int_list and n_mpz == mpz(3): # Special case for n=3, only base 2
             selected_bases_int_list = [2]
        elif not selected_bases_int_list and n_mpz > 3: # if all defaults are too large
             # This case should be rare if n is reasonably large.
             # If n is e.g. 5, [2,3] would be selected.
             # If no bases can be selected, the test will effectively be skipped.
             messagebox.showwarning("Bases Warning", f"Could not determine suitable bases for n={n_mpz}. Using defaults if possible, or no bases.")


    if not selected_bases_int_list:
        # This means no bases were specified, random generation failed/wasn't applicable, AND fallback defaults are also unsuitable (e.g. n is too small like 2)
        # Or if n=3 and [2] was selected, this block is skipped.
        # For n=2, it's already handled by is_prime or direct check.
        # If we reach here with no bases for a larger n, it's an issue.
        # However, gmpy2.is_prime likely caught n=2.
        # If n=3, selected_bases_int_list should be [2].
        # This block is more a safeguard.
        if n_mpz > 2: # Only show warning if n is something that should have been testable
             update_result_text(f"Could not perform Euler test as no suitable bases were provided or could be determined (e.g., number is too small for chosen/default bases, or random generation failed).")
        # If n_mpz was 2, it's prime, already handled.
        # If n_mpz was 1, also handled.
        if progress_bar: progress_bar['value'] = 0
        return

    # Step 3: Euler Probabilistic Primality Test (Parallel)
    update_result_text(f"Testing with Euler test using bases: {selected_bases_int_list}...")
    root.update_idletasks()

    euler_results = run_euler_tests_parallel(n_mpz, selected_bases_int_list, progress_bar, root, current_progress_val)

    end_time_overall = time.time()
    total_time = end_time_overall - start_time_overall

    all_passed = True
    failed_bases = []
    passed_bases = []

    for base, passed_test in euler_results:
        if passed_test:
            passed_bases.append(base)
        else:
            all_passed = False
            failed_bases.append(base)
            # If any base fails, n is definitely composite (if gcd(base,n)=1 was met in worker)
            # Or the base was unsuitable (e.g. gcd(base,n)!=1), which also implies composite if base < n.
            # The worker function euler_test_single_base returns (base, False) if gcd(a,n)!=1.
            # So, a False here means either Euler's criterion failed OR gcd(a,n)!=1 was found.
            # If gcd(a,n)!=1 and a < n, then n is composite.
            
            # Check if the failure was due to gcd(a,n) != 1
            # We need to re-check gcd here as the worker doesn't explicitly return this info, only pass/fail.
            # This is a bit redundant but useful for a more informative message.
            # Alternatively, the worker could return a more detailed status.
            factor_found_with_base = None
            if mpz(base) < n_mpz : # only makes sense if base < n
                common_divisor = gmpy2.gcd(mpz(base), n_mpz)
                if common_divisor != 1:
                    factor_found_with_base = common_divisor

            if factor_found_with_base and factor_found_with_base != n_mpz : # Ensure factor is not n itself
                update_result_text(f"The number is composite.\nFailed Euler test for base {base} (found factor {factor_found_with_base}).\nTested in {total_time:.4f} seconds.")
            else:
                update_result_text(f"The number is composite.\nFailed Euler test for base {base}.\nTested in {total_time:.4f} seconds.")
            
            if progress_bar: progress_bar['value'] = PROGRESS_BAR_MAX
            return # Stop on first failure

    if all_passed:
        # If all selected bases passed the Euler test
        if not euler_results: # Should not happen if selected_bases_int_list was not empty
             update_result_text(f"No Euler tests were performed. Result inconclusive. (Time: {total_time:.4f}s)")
        else:
            update_result_text(f"The number is likely prime (passed Euler test for bases: {passed_bases}).\nTested in {total_time:.4f} seconds.")
    
    if progress_bar: progress_bar['value'] = PROGRESS_BAR_MAX


def parse_input_to_mpz(input_str):
    """
    Parses an input string (number or mathematical expression) using sympy
    and converts it to a gmpy2.mpz object.
    Returns an mpz object or None on error (and shows a messagebox).
    """
    try:
        # Allow evaluation of expressions like 2**127-1
        # For very large numbers from expressions, sympy might be slow or hit limits.
        # We might need to be careful here.
        # Using a timeout or direct gmpy2 parsing if possible for simple integers.
        
        # Try direct int conversion first for simple large numbers
        try:
            if input_str.isdigit() or (input_str.startswith('-') and input_str[1:].isdigit()):
                 n_mpz = mpz(input_str)
                 if n_mpz <= 0: # Primality typically for > 1
                     messagebox.showerror("Input Error", f"Number {input_str} must be a positive integer greater than 1 for primality testing.")
                     return None
                 return n_mpz
        except ValueError:
            pass # Not a simple integer string, try sympy

        # If not a simple integer string, try sympy for expressions
        # Check for potential harmful expressions before sympify - basic check
        if any(kw in input_str for kw in ['import', 'eval', 'exec', 'lambda', '__']):
            messagebox.showerror("Input Error", "Input contains potentially unsafe expressions.")
            return None

        number_expr = sympy.sympify(input_str)
        if not number_expr.is_number:
            messagebox.showerror("Input Error", f"Expression '{input_str}' did not evaluate to a number.")
            return None
        
        # Convert to string then to mpz to handle potentially huge numbers from sympy
        n_mpz = mpz(str(number_expr))

        if n_mpz <= 0: # Primality typically for > 1
             messagebox.showerror("Input Error", f"Evaluated number {n_mpz} must be a positive integer greater than 1 for primality testing.")
             return None
        return n_mpz
        
    except Exception as e:
        messagebox.showerror("Input Error", f"Could not parse '{input_str}'. Please insert a valid integer or mathematical expression.\\nDetails: {e}")
        return None

# -------------------  IMPROVED GUI DESIGN  -------------------

def center_window(window, width=700, height=700):
    """
    Helper function to center the window on the screen.
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# Create the main window
root = tk.Tk()
root.title("Prime Number Test")
center_window(root, 750, 780)  # Slightly enlarged window for more space

# --- Professional Look: Colors and Fonts ---
BG_COLOR = "#2C3E50"         # Dark blue
INPUT_BG_COLOR = "#34495E"   # Slightly lighter dark blue
TEXT_COLOR = "#ECF0F1"       # Very light gray / almost white
TITLE_TEXT_COLOR = "#FFFFFF"   # White
BUTTON_BG_COLOR = "#E67E22"   # Orange
BUTTON_FG_COLOR = "#FFFFFF"   # White
BUTTON_ACTIVE_BG_COLOR = "#F39C12" # Lighter orange
BORDER_COLOR = "#233140"      # Darker shade of blue for borders
SCROLLBAR_BG_COLOR = "#34495E"

root.configure(bg=BG_COLOR)

# Fonts
try:
    # Attempt to use more modern fonts if available
    TITLE_FONT = ("Segoe UI", 16, "bold")
    LABELFRAME_TITLE_FONT = ("Segoe UI", 13, "bold") # New font for LabelFrame titles
    LABEL_FONT = ("Segoe UI", 12)
    INSTRUCTION_TEXT_FONT = ("Segoe UI", 10)      # Smaller font for instruction text
    BUTTON_FONT = ("Segoe UI", 13, "bold")
    RESULT_FONT = ("Segoe UI", 12)
except tk.TclError:
    # Fallback to Helvetica if preferred fonts are not available
    TITLE_FONT = ("Helvetica", 14, "bold") 
    LABELFRAME_TITLE_FONT = ("Helvetica", 12, "bold") # New font for LabelFrame titles
    LABEL_FONT = ("Helvetica", 11)         
    INSTRUCTION_TEXT_FONT = ("Helvetica", 9)       # Smaller font for instruction text
    BUTTON_FONT = ("Helvetica", 12, "bold")
    RESULT_FONT = ("Helvetica", 11)        

# Label frame for instructions
instructions_frame = tk.LabelFrame(
    root, text="Instructions", bg=BG_COLOR, fg=TITLE_TEXT_COLOR,
    font=LABELFRAME_TITLE_FONT, bd=2, relief="solid", borderwidth=1, highlightbackground=BORDER_COLOR # Used new font
)
instructions_frame.pack(fill="x", padx=20, pady=(15,5)) # Slightly adjusted padding

instruction_text = (
    "This program uses sympy.isprime for numbers less than 10^20.\n"
    "For larger numbers, it first applies a classical filter (trial division by small primes\n"
    "and numbers of the form 6k±1). If the number passes this filter, an Euler-based test (a^((N-1)/2) % N == ±1) \n"
    "is then used with multiple bases.\n\n"
    "A 'likely prime' result from the Euler-based test indicates a high probability\n"
    "that the number is prime.\n\n"
    "Pseudoprimes are non-genuine primes. For enhanced results, several bases (e.g., 2, 3, 5, 7, 11, 13)\n"
    "will be tested concurrently using multiprocessing.\n\n"
    "Note: You can also input mathematical expressions. Example: 2**13-1, 15!-1\n"    
)

instructions_label = tk.Label(
    instructions_frame, text=instruction_text, bg=BG_COLOR, fg=TEXT_COLOR,
    font=INSTRUCTION_TEXT_FONT, justify="left", wraplength=680 # Used new smaller font
)
instructions_label.pack(padx=15, pady=(5,10)) # Slightly adjusted padding

# Frame for input fields
input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.pack(padx=20, pady=10, fill="x")

# Input Number + Scrollbar
tk.Label(
    input_frame, text="Enter the number (or expression):", bg=BG_COLOR, fg=TEXT_COLOR,
    font=LABEL_FONT
).grid(row=0, column=0, sticky="w", padx=5, pady=(5,0))

# Frame for the text area and scrollbar
text_area_frame = tk.Frame(input_frame, bg=INPUT_BG_COLOR, relief="solid", borderwidth=1, highlightthickness=1, highlightbackground=BORDER_COLOR)
text_area_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,10), sticky="ew")

text_number = tk.Text(
    text_area_frame, height=3, width=38, bg=INPUT_BG_COLOR, fg=TITLE_TEXT_COLOR,
    insertbackground=TITLE_TEXT_COLOR, font=LABEL_FONT, relief="flat", borderwidth=0, highlightthickness=0
)
text_number.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_y = tk.Scrollbar(text_area_frame, command=text_number.yview, relief="flat", bg=SCROLLBAR_BG_COLOR, troughcolor=INPUT_BG_COLOR, activerelief="flat")
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

text_number.config(yscrollcommand=scrollbar_y.set)

# Input Base 'a'
tk.Label(
    input_frame, text="Bases 'a' (e.g., 5 for 5 random bases, or 2,3,7 for specific bases):", bg=BG_COLOR, fg=TEXT_COLOR,
    font=LABEL_FONT
).grid(row=2, column=0, sticky="w", padx=5, pady=(5,0))

entry_a = tk.Entry(
    input_frame, width=60, bg=INPUT_BG_COLOR, fg=TITLE_TEXT_COLOR, # A bit wider
    insertbackground=TITLE_TEXT_COLOR, font=LABEL_FONT, relief="solid", borderwidth=1, highlightthickness=1, highlightbackground=BORDER_COLOR
)
entry_a.insert(0, "5")
entry_a.grid(row=3, column=0, padx=5, pady=(0,10), sticky="w")

# Configure grid column weights for input_frame to make text_number and entry_a expandable if needed
input_frame.grid_columnconfigure(0, weight=1)


# Frame for the "Check Prime" button
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=15)

check_button = tk.Button(
    button_frame, text="Check Primality", command=check_prime,
    bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=BUTTON_FONT, 
    relief="raised", bd=2, padx=20, pady=5, # Larger button
    activebackground=BUTTON_ACTIVE_BG_COLOR, activeforeground=BUTTON_FG_COLOR
)
check_button.pack()

# Frame for the Progress Bar
progress_frame = tk.Frame(root, bg=BG_COLOR)
progress_frame.pack(fill="x", padx=20, pady=(5, 5)) # Smaller padding around the progress bar

progress_bar = ttk.Progressbar(
    progress_frame, 
    orient="horizontal", 
    length=300, 
    mode='determinate'
    # maximum will be set later if needed, default is 100
)
progress_bar.pack(fill="x", expand=True, padx=5, pady=5)

# Label frame for results
result_frame = tk.LabelFrame(
    root, text="Result", bg=BG_COLOR, fg=TITLE_TEXT_COLOR,
    font=LABELFRAME_TITLE_FONT, bd=2, relief="solid", borderwidth=1, highlightbackground=BORDER_COLOR # Use LabelFrame Title Font
)
result_frame.pack(fill="both", expand=True, padx=20, pady=(10,20)) # Larger padding

# Make the result_frame's content area (where text area will go) expand
result_frame.grid_rowconfigure(0, weight=1)
result_frame.grid_columnconfigure(0, weight=1)

# Create a Text widget for results with a Scrollbar
result_text_area = tk.Text(
    result_frame, 
    wrap=tk.WORD, # Wrap text at word boundaries
    bg=BG_COLOR, 
    fg=TEXT_COLOR, 
    font=RESULT_FONT,
    relief="flat", # Flat relief to blend with the frame
    borderwidth=0,
    highlightthickness=0,
    padx=10, # Padding inside the text area
    pady=10
)
result_text_area.grid(row=0, column=0, sticky="nsew") # Use grid to place it

result_scrollbar = ttk.Scrollbar( # Use ttk.Scrollbar for better styling
    result_frame, 
    orient="vertical", 
    command=result_text_area.yview
)
result_scrollbar.grid(row=0, column=1, sticky="ns") # Place scrollbar next to text area

result_text_area.config(yscrollcommand=result_scrollbar.set, state="disabled") # Link scrollbar and set initial state to disabled

# Helper function to update the result_text_area
def update_result_text(new_text):
    result_text_area.config(state="normal")
    result_text_area.delete("1.0", tk.END)
    result_text_area.insert(tk.END, new_text)
    result_text_area.config(state="disabled")

if __name__ == '__main__':
    root.mainloop()
# -------------------  END OF PRIME NUMBERS GUI  -------------------
