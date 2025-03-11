import tkinter as tk
from tkinter import messagebox
import sympy
import math
import multiprocessing
import gmpy2
from gmpy2 import mpz, isqrt

def check_divisor(args):
    """
    Top-level function for multiprocessing.
    Returns the divisor if it divides n, otherwise None.
    """
    n, d = args
    n_mpz = mpz(n)
    d_mpz = mpz(d)
    return d if n_mpz % d_mpz == 0 else None

def decompose_number(n):
    """
    Decomposes the given number n into its prime factors.
    Uses GMP (via gmpy2) for optimized arithmetic and parallelizes
    trial division over candidate divisors with all available CPU cores.
    Returns a list of tuples (prime, exponent).
    """
    n = mpz(n)  # Convert to GMP integer
    factors = []
    
    # Factor out small primes 2 and 3
    for p in [2, 3]:
        count = 0
        while n % p == 0:
            count += 1
            n //= p
        if count > 0:
            factors.append((p, count))
    if n == 1:
        return factors
    
    # If the remaining number is prime, add it directly
    if sympy.isprime(int(n)):
        factors.append((int(n), 1))
        return factors

    # Main loop: use trial division with candidates of the form 6k ± 1
    # Continue until n becomes prime or 1
    while n > 1 and not sympy.isprime(int(n)):
        limit = isqrt(n) + 1  
        candidates = []
        k = 1
        while True:
            d1 = 6*k - 1
            d2 = 6*k + 1
            if d1 > limit:
                break
            candidates.append(int(d1))
            if d2 <= limit:
                candidates.append(int(d2))
            k += 1

        if not candidates:
            # No more candidates to test; n is prime or 1
            break

        # Parallel test: check which candidates divide n
        # Use all CPU cores
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            results = pool.map(check_divisor, [(n, d) for d in candidates])

        # Filter out None values; keep only actual divisors
        candidate_factors = [r for r in results if r is not None]
        candidate_factors.sort()
        if not candidate_factors:
            # No factor found -> n is prime
            break

        # Take the smallest factor found
        factor = candidate_factors[0]
        count = 0
        while n % factor == 0:
            count += 1
            n //= factor
        factors.append((factor, count))

    # If something remains and is > 1, it's prime
    if n > 1:
        factors.append((int(n), 1))
    return factors

def get_input_number(text_widget):
    """
    Reads the input from the given Text widget, evaluates it using sympy,
    and returns an integer or None on error.
    """
    input_str = text_widget.get("1.0", tk.END).strip()
    try:
        num = int(sympy.sympify(input_str))
        return num
    except Exception:
        messagebox.showerror("Input Error", "Please insert a valid integer or mathematical expression")
        return None

def decompose_and_display():
    """
    Reads the number from the text widget, decomposes it, and displays the result.
    If the user enters 0, the application quits.
    """
    num = get_input_number(text_number)
    if num is None:
        return
    if num == 0:
        root.quit()
        return

    result_label.config(text="Decomposing, please wait...")
    root.update_idletasks()

    try:
        factors = decompose_number(num)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during decomposition: {e}")
        return
    
    # Format the output (e.g., "2^3 * 5 * 7^2")
    output_parts = []
    for prime, exp in factors:
        if exp == 1:
            output_parts.append(str(prime))
        else:
            output_parts.append(f"{prime}^{exp}")
    output_text = " * ".join(output_parts)
    result_label.config(text=f"Decomposition: {output_text}")

def center_window(window, width=700, height=500):
    """
    Helper function to center the window on the screen.
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# Main Tkinter code
root = tk.Tk()
root.title("Prime Decomposition")
center_window(root, 700, 500)
root.configure(bg="#2E2E2E")

label_font = ("Helvetica", 12)
button_font = ("Helvetica", 12, "bold")

instruction_text = (
    "Prime Decomposition of Large Numbers\n"
    "Enter a number (you can use mathematical expressions, e.g., 2**100) below.\n"    
)
instruction_label = tk.Label(
    root, text=instruction_text, bg="#2E2E2E", fg="white",
    font=label_font, justify="center"
)
instruction_label.pack(padx=10, pady=10)

frame_input = tk.Frame(root, bg="#2E2E2E")
frame_input.pack(padx=10, pady=10)

tk.Label(
    frame_input, text="Enter the number:", bg="#2E2E2E", fg="white", font=label_font
).grid(row=0, column=0, padx=5, pady=5, sticky="e")

text_number = tk.Text(frame_input, height=3, width=40, bg="#1C1C1C", fg="white", font=label_font)
text_number.grid(row=0, column=1, padx=5, pady=5, sticky="w")

button_decompose = tk.Button(
    root, text="Decompose Number", command=decompose_and_display,
    bg="#424242", fg="white", font=button_font
)
button_decompose.pack(padx=10, pady=10)

result_label = tk.Label(
    root, text="", bg="#2E2E2E", fg="white", font=label_font,
    wraplength=650, justify="center"
)
result_label.pack(padx=10, pady=10)

if __name__ == "__main__":
    # Na Windows môže byť pre bezpečnosť dobré pridať aj multiprocessing.freeze_support()
    # multiprocessing.freeze_support()
    root.mainloop()
