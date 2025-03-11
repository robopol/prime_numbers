# Prime Numbers Repository

This repository contains various materials and scripts related to prime numbers: from theoretical documents to sample programs for primality testing and number factorization.

## Contents

- **[Methods of finding prime numbers.pdf](Methods%20of%20finding%20prime%20numbers.pdf)**  
  A document providing a theoretical and practical overview of prime number testing methods.

- **[prime_numbers.pdf](prime_numbers.pdf)**  
  Another document containing notes on prime number theory and testing examples.

- **[number_decomposition.py](number_decomposition.py)**  
  A Python script that factors a given number into its prime factors (factorization algorithm).

- **[prime_numbers.py](prime_numbers.py)**  
  A main Python script for prime testing and other operations involving large numbers.

- **[prime-numbers-test.html](prime-numbers-test.html)**  
  An HTML application that uses Pyodide to test if a given number is prime directly in the browser (no Python installation required).

- **prime_test GUI**  
  (Folder or file) A graphical user interface (e.g., Tkinter) for prime testing.

- **[setup_prime_test.exe](setup_prime_test.exe)**  
  An executable or installer for Windows, possibly providing an easy way to install/use the prime testing application.

## Algorithm Capabilities

This algorithm combines a classical filtering method with a parallelized Fermat primality test optimized by GMP via gmpy2. Its key features include:

- **Efficient Small Divisor Filtering:**  
  Quickly eliminates composite numbers by checking divisibility using small primes (e.g., 2, 3, 5, 7, 11, 13) and potential divisors of the form 6k±1.

- **Parallelized Fermat Testing:**  
  Runs Fermat tests for multiple bases concurrently using Python's multiprocessing, allowing rapid detection of composite numbers.

- **GMP-based Optimization:**  
  Leverages the highly optimized GMP library through gmpy2 to perform modular exponentiation on extremely large numbers efficiently.

- **High Performance on Large Numbers:**  
  Benchmarks on standard desktop PCs show that the algorithm can test very large numbers (e.g., up to 2**100000) in just a few seconds.

- **Robust Filtering of Pseudoprimes:**  
  The combination of classical filtering and Fermat testing effectively identifies pseudoprimes, making this approach competitive with the Miller-Rabin test in both speed and reliability.

## Installation and Usage

1. **Documents (.pdf)**  
   - These files contain theoretical explanations, methods, and guides on prime numbers.

2. **Python Scripts (.py)**  
   - Make sure you have Python 3.8+ installed.
   - Run them from a terminal/command prompt, for example:
     ```bash
     python prime_numbers.py
     ```

3. **HTML Application (prime-numbers-test.html)**  
   - Open this file in a modern web browser.
   - It uses Pyodide so you can run prime tests directly in the browser, no local Python installation required.

4. **GUI or .exe**  
   - If the `.exe` file is provided, you can launch it directly on Windows.
   - Alternatively, run the `prime_test GUI` (Python script) to open a graphical interface.

## License

This project is licensed under the [MIT License](LICENSE).

---

If you have any questions or suggestions, please open an [issue](../../issues) or submit a [pull request](../../pulls).  
Thank you for using this repository!
