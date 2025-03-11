import tkinter as tk
from tkinter import messagebox
import sympy
import math
import multiprocessing
import gmpy2
from gmpy2 import mpz, powmod

# -------------------  LOGIC  -------------------

big_num = 10**20
basic_field = [2, 3, 5, 7, 11, 13]
big_num2 = 10**12

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

def fermat_test(args):
    """
    Performs the Fermat test for a given base 'a':
      - Computes powmod(a, n-1, n) using gmpy2.
      - If the result equals 1, the test 'passes' for that base.
    """
    n, a = args
    n_mpz = mpz(n)
    a_mpz = mpz(a)
    r = powmod(a_mpz, n_mpz - 1, n_mpz)
    if r == 1:
        return (a, True)
    else:
        return (a, False)

def run_fermat_tests(n, bases):
    """
    Runs the Fermat test in parallel for multiple bases.
    Returns a list of (base, pass/fail) tuples.
    """
    pool = multiprocessing.Pool(processes=len(bases))
    args = [(n, a) for a in bases]
    results = pool.map(fermat_test, args)
    pool.close()
    pool.join()
    return results

# -------------------  GUI FUNCTIONS  -------------------

def get_input():
    """
    Reads a number (or mathematical expression) from the text field
    and attempts to parse it with sympy. Returns an integer or None on error.
    """
    input_string = text_number.get("1.0", tk.END).strip()
    try:
        number_expr = sympy.sympify(input_string)
        number_int = int(number_expr) if number_expr.is_number else None
        if number_int is None:
            raise ValueError
    except Exception:
        messagebox.showerror("Input Error", "Please insert a valid integer or mathematical expression")
        return None
    return number_int

def get_a():
    """
    Reads the base (a) from the corresponding input field
    and returns it as an integer or None on error.
    """
    input_string = entry_a.get().strip()
    try:
        number_int = int(input_string)
    except Exception:
        messagebox.showerror("Input Error", "Please insert only integer values")
        return None
    return number_int

def check_prime():
    """
    Main function triggered by the 'Check Prime' button.
    Obtains the number n, decides on the testing method, and displays the result.
    """
    n = get_input()
    if n is None:
        return
    if n == 0:
        root.quit()
        return

    # If the number is less than 10^20, use sympy.isprime (fast check)
    if n < big_num:
        if sympy.isprime(n):
            result_text = "Number is prime."
        else:
            result_text = "Number is composite."
        result_label.config(text=result_text)
        return

    # For large numbers, first apply the classical filter
    filter_result = classical_filter(n)
    if filter_result is not None:
        result_label.config(text=filter_result)
        return

    # Get the user-specified base and construct the list of bases
    base_input = get_a()
    if base_input is None:
        return
    default_bases = [2, 3, 5, 7, 11, 13]
    bases = sorted(set([base_input] + default_bases))

    # Inform the user that the tests are running
    result_label.config(text="Running Fermat tests, please wait...")
    root.update_idletasks()

    # Run the Fermat tests in parallel
    results = run_fermat_tests(n, bases)

    # Evaluate results
    composite_found = False
    results_text = ""
    for base, passed in results:
        if passed:
            results_text += f"Base {base}: Pass\n"
        else:
            results_text += f"Base {base}: Fail\n"
            composite_found = True

    if composite_found:
        final_text = "Number is composite based on Fermat test(s):\n" + results_text
    else:
        final_text = "Number is prime or pseudoprime based on Fermat tests:\n" + results_text
    result_label.config(text=final_text)

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
center_window(root, 700, 700)  # Set size and center
root.configure(bg="#2E2E2E")

# Fonts and colors
title_font = ("Helvetica", 14, "bold")
label_font = ("Helvetica", 11)
button_font = ("Helvetica", 11, "bold")

# Label frame for instructions
instructions_frame = tk.LabelFrame(
    root, text="Instructions", bg="#2E2E2E", fg="white",
    font=label_font, bd=2, relief="groove"
)
instructions_frame.pack(fill="x", padx=15, pady=15)

instruction_text = (
    "This program employs a classical algorithm (for numbers < 10^20) and an improved method\n"
    "for finding prime numbers using the small Fermat theorem.\n\n"
    "When it yields the outcome: prime or pseudoprime, it reflects a probability result,\n"
    "with pseudoprimes having a low likelihood.\n\n"
    "Pseudoprimes are non-genuine primes. For enhanced results, several bases (e.g., 2, 3, 5, 7, 11, 13)\n"
    "will be tested concurrently using multiprocessing.\n\n"
    "Note: You can also input mathematical expressions. Example: 2**13-1, 15!-1\n"    
)

instructions_label = tk.Label(
    instructions_frame, text=instruction_text, bg="#2E2E2E", fg="white",
    font=label_font, justify="left", wraplength=650
)
instructions_label.pack(padx=10, pady=10)

# Frame for input fields
input_frame = tk.Frame(root, bg="#2E2E2E")
input_frame.pack(padx=15, pady=10, fill="x")

tk.Label(
    input_frame, text="Enter the number:", bg="#2E2E2E", fg="white",
    font=label_font
).grid(row=0, column=0, sticky="e", padx=5, pady=5)

text_number = tk.Text(
    input_frame, height=3, width=30, bg="#1C1C1C", fg="white",
    insertbackground="white", font=label_font
)
text_number.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(
    input_frame, text="Enter the basis a:", bg="#2E2E2E", fg="white",
    font=label_font
).grid(row=1, column=0, sticky="e", padx=5, pady=5)

entry_a = tk.Entry(
    input_frame, width=10, bg="#1C1C1C", fg="white",
    insertbackground="white", font=label_font
)
entry_a.insert(0, "2")
entry_a.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Frame for the "Check Prime" button
button_frame = tk.Frame(root, bg="#2E2E2E")
button_frame.pack(pady=5)

check_button = tk.Button(
    button_frame, text="Check Prime", command=check_prime,
    bg="#424242", fg="white", font=button_font
)
check_button.pack()

# Label frame for results
result_frame = tk.LabelFrame(
    root, text="Result", bg="#2E2E2E", fg="white",
    font=label_font, bd=2, relief="groove"
)
result_frame.pack(fill="both", expand=True, padx=15, pady=15)

result_label = tk.Label(
    result_frame, text="", wraplength=650, justify="left",
    bg="#2E2E2E", fg="white", font=label_font
)
result_label.pack(padx=10, pady=10, fill="both", expand=True)

if __name__ == '__main__':
    root.mainloop()
# -------------------  END OF PRIME NUMBERS GUI  -------------------
