import sys
import math
import sympy

def get_input():
    while True:
        try:
            print("Enter the number:")
            input_string = sys.stdin.readline()
            number_int = int(input_string)
        except Exception:
            print("Please insert only integer values")
            continue
        break
    return number_int

def get_a():
    while True:
        try:
            print("Enter the basis a:")
            input_string = sys.stdin.readline()
            number_int = int(input_string)
        except Exception:
            print("Please insert only integer values")
            continue
        break
    return number_int

print("""
Prime Number Test:

This program employs a classical algorithm (for numbers < 10^20) and an improved method
for finding prime numbers using the small Fermat theorem.
When it yields the outcome: prime or pseudoprime, it reflects a probability result,
with pseudoprimes having a low likelihood.
Pseudoprimes are non-genuine primes. For enhanced results, consider changing the base 'a' to 3, 4, 5, 7, and so on.

To conclude the program, press 0 and then press Enter.
""")
b_first=100;big_num=10**20;basic_a=False;last_n=0;basic_field=[2,3,5,7,11,13];big_num2=10**12;stop=False

while True:
    if basic_a==False:
        n = get_input()
        stop=False;basic_a=False    
    if n == 0:
        break
    # filtering with sympy library
    if n < big_num:        
        if sympy.isprime(n):
            print("Number is prime.")
        else:
            print("Number is composite")                   

    if n > big_num:                    
        if basic_a == False and stop == False:
            # filtering to basic conditions
            for divisor in basic_field:
                if n % divisor == 0:
                    print("Number is composite, the first divisor is:",divisor)
                    stop=True
                    break
        # filtering by classical algorithm to prime numbers divisor<big_num2.
        if basic_a == False and stop == False:
            divisor_1=1
            divisor_2=1
            k=1
            range = round(math.sqrt(big_num2)+1)
            while divisor_1 <= range:
                divisor_1=6*k-1
                divisor_2=6*k+1
                k+=1                
                if n % divisor_1 == 0:
                    print("Number is composite, the first divisor is:", divisor_1)
                    stop=True
                    break                
                if n % divisor_2 == 0:
                    print("Number is composite, the first divisor is:", divisor_2)
                    stop=True
                    break          
            
        if stop == False:
            a = get_a()
            if a == 0:
                basic_a = False                
                continue
            basic_a=True
            print("Please wait...")
            cycle_end = cycle = int(a ** b_first % n)
            complet_end = complet = b_first
            euler = (n - 1) // 2
            k = euler
            field_num = [b_first]
            field_res = [cycle]            
            while complet < euler:
                if 2 * complet >= euler:
                    break
                cycle = cycle ** 2
                if cycle > n:
                    cycle = cycle % n
                    if cycle == 0: cycle=n                    
                complet = 2 * complet
                field_num.append(complet)
                field_res.append(cycle)                
            
            index = len(field_num) - 1
            while k > b_first and index >= 0:
                num = field_num[index]
                if num < k: 
                    maximum = num
                    max_cycle = field_res[index]
                    complet_end += maximum
                    cycle_end = cycle_end * max_cycle
                    if cycle_end > n:
                        cycle_end = cycle_end % n
                    k = euler - complet_end
                index -= 1                

            remainder = int((cycle_end * a ** k) % n)            
            if remainder == 1:
                print("Number is prime or pseudoprime, pseudoprimes are very unlikely. Remainder is 1")
                print("It is also recommended to try the calculation for several bases a = 2,3,4,5…")
            elif remainder == n - 1:
                print("Number is strong probably prime. Remainder is n-1")
                print(" It is also recommended to try the calculation for several bases a = 2,3,4,5…") 
            else:
                print("Number is composite.")
