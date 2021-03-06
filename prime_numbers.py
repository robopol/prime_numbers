# *************************************************************************
# Prime nubers test
#
# Author: ing. Robert Polak
# Contact Info: robopol@robopol.sk
# website: https://www.robopol.sk
# Purpose:
#           An efficient algorithm for determining large primes.
#
# 'type: console program' 
# Copyright notice: This code is Open Source and should remain so.
# *************************************************************************
from logging import BASIC_FORMAT
import sys
import math

print("***********************************************************************************")
print("Prime number test:")
print("")
print("This program uses a classical algorithm (for numbers < 10ˆ14) and ")
print("improved finding of prime numbers using a small Fermat theorem.")
print("If it gets the statement: prime or pseudoprime, then it is a probability")
print("result, with pseudoprimes having a low probability.")
print("Pseudoprimes are false primes. For a better result changes the basis a = 3,4,5,7...")
print("")
print("To end the program, press 0 and the enter.")
print("***********************************************************************************")

# defining the necessary constants.
b_first=251
big_num=10**14
big_num2=10**14
basic_field=[2,3,5,7]
global basic_a
basic_a=False
global last_n
last_n=0
# Function for entering an numbers
def get_input():
    while True:
        try:
            print("Enter the number:")
            input_string=sys.stdin.readline()
            number_int=int(input_string)
        except Exception:
            print("Please insert only integer values")
            continue
        break
    return number_int

# Function for entering "a"
def get_a():
    while True:
        try:
            print("Enter the basis a:")
            input_string=sys.stdin.readline()
            number_int=int(input_string)
        except Exception:
            print("Please insert only integer values")
            continue
        break
    return number_int

# Infinite while loop.
while True:
    n=number=get_input()
    stop=False
    if last_n==n:
        basic_a=True
    else:
        basic_a=False
    last_n=n

    # end of program    
    if number == 0:
        break
    # filtering to basic conditions
    for divisor in basic_field:
        if number % divisor == 0:
            print("Number is composite, the first divisor is:",divisor)
            stop=True
            break
 
    # filtering by classical algorithm to prime numbers n<big_num
    if number < big_num and stop == False and basic_a == False:
        divisor_1=1
        divisor_2=1
        k=1
        range = round(math.sqrt(n)+1)       
        while divisor_1 <= range:           
            divisor_1=6*k+1
            divisor_2=6*k-1
            k+=1
            if divisor_1 % 5 != 0:
                if n % divisor_1 == 0:
                    print("Number is composite, the first divisor is:", divisor_1)
                    stop=True
                    break
            if divisor_2 % 5 != 0:
                if n % divisor_2 == 0:
                    print("Number is composite, the first divisor is:", divisor_2)
                    stop=True
                    break  
        if stop==False: 
            print("Number is prime")
            break    

    # filtering by Robopol algorithm n>big_num, more information: https://robopol.sk/blog/
    # 1 step: filtering to magic formula 24
    if stop == False and n > big_num:
        if basic_a == False:
            # 1 step: filtering to magic formula 24
            magic=(n**2-1) % 24
            if magic > 0:
                print("Number is composite, magic formula nˆ2 Mod 24=0, see: https://robopol.sk/blog/program-na-prvočísla")
                stop=True
                break
        # filtering by classical algorithm to prime numbers divisor<big_num2.
        if basic_a == False:
            divisor_1=1
            divisor_2=1
            k=1
            range = round(math.sqrt(big_num2)+1)
            while divisor_1 <= range:
                divisor_1=6*k+1
                divisor_2=6*k-1
                k+=1
                if divisor_1 % 5 != 0:
                    if n % divisor_1 == 0:
                        print("Number is composite, the first divisor is:", divisor_1)
                        stop=True
                        break       
                if divisor_1 % 5 != 0:
                    if n % divisor_2 == 0:
                        print("Number is composite, the first divisor is:", divisor_2)
                        stop=True
                        break
            basic_a=True  
        
        # Filtering by an improved algorithm of a small Fermat theorem, create: robopol.sk.
        if stop == False:
            # The basis of the power of Fermat's theorem.
            a=get_a()
            if a == 0:
                break
            print("wait")
            # defining the necessary constants.
            cycle_end=cycle= int(a**b_first % n)
            complet_end=complet=b_first
            euler=(n - 1)//2
            k=euler
            # We define an array of residues, numbers.
            field_num=[b_first]
            field_res=[cycle]
            # We will fill these fields.
            while complet < euler:
                if 2*complet >= euler:
                    break
                cycle=cycle**2
                if cycle > n:
                    cycle=cycle % n
                    if cycle == 0: cycle=n
                complet=2*complet
                field_num=field_num + [complet]
                field_res=field_res + [cycle]
            
            # Main algorithm.                       
            while k > b_first:
                index=0
                for num in field_num:
                    if num < k: 
                        maximum = num
                        max_cycle = field_res [index]
                    index +=1
                complet_end += maximum
                cycle_end = cycle_end*max_cycle
                if cycle_end > n:
                    cycle_end=cycle_end % n
                    if cycle_end == 0: cycle_end=n
                k= euler - complet_end                

            # determination of conditions for prime numbers.
            remainder = int((cycle_end * a ** k) % n)
            print ("remainder is:", remainder)
            # Robopol test, if remainder is n-1 for (n-1)/2 and remainder is 1 for n-1, number is probably prime.            
            if remainder == 1:
                print("Number is prime or pseudoprime, pseudoprimes are very unlikely.")
                print(" It is also recommended to try the calculation for several bases a = 2,3,4,5…")
            if remainder == n-1:
                print("Number is strong probably prime.")
                print(" It is also recommended to try the calculation for several bases a = 2,3,4,5…") 
            if remainder != n-1 and remainder != 1:
                print("Number is composite.")