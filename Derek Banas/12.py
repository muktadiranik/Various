# ---------- ITERABLES ----------
sample_1 = iter("Sample")
print(next(sample_1), next(sample_1))
for char in sample_1:
    print(char, next(sample_1))


class Alphabet:
    def __init__(self):
        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.letters) - 1:
            raise StopIteration
        self.index += 1
        return self.letters[self.index]


alphabet = Alphabet()
for letter in alphabet:
    print(letter, end=" ")


dict_1 = {"first_name": "Derek", "last_name": "Banas"}
print(dict_1)

for key in dict_1.keys():
    print(key, dict_1[key])


# ---------- PROBLEM ----------
# Create a class that returns values from the Fibonacci
# sequence each time next is called
# Sample Output
# Fib : 1
# Fib : 2
# Fib : 3
# Fib : 5


class FibonacciGenerator:
    def __init__(self):
        self.first = 0
        self.second = 1

    def __iter__(self):
        return self

    def __next__(self):
        fib_num = self.first + self.second
        self.first = self.second
        self.second = fib_num
        return fib_num


fibonacci_sequence = FibonacciGenerator()
for i in fibonacci_sequence:
    print("i :", i)
    if i > 100:
        break

for i in range(5):
    print("next(fibonacci_sequence) :", next(fibonacci_sequence))


print(list(map(lambda x: x**2, range(5))))
print([x**2 for x in range(5)])

print(list(filter(lambda x: x % 2 == 0, range(5))))
print([x for x in range(5) if x % 2 == 0])

# Generate a list of 50 values and take them to the power
# of 2 and return all that are multiples of 8
print([x**2 for x in range(50) if x % 8 == 0])

# Multiply all values in one list times all values in
# another
print([x * y for x in range(1, 5) for y in range(2, 6)])

# Generate a list of 10 values, multiply them by 2 and
# return multiples of 8
print([x for x in [i * 2 for i in range(10)] if x % 8 == 0])

import random

print([x for x in [random.randint(1, 1001) for i in range(50)] if x % 9 == 0])

multi_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(multi_list)
print(multi_list[0][1])
print(col[1] for col in multi_list)
print([multi_list[i][i] for i in range(len(multi_list))])


# ---------- GENERATOR FUNCTIONS ----------
# A generator function returns a result generator when called
# They can be suspended and resumed during execution of
# your program to create results over time rather then
# all at once

# We use generators when we want to big result set, but
# we don't want to slow down the program by creating
# it all at one time

# Create a generator that calculates primes and returns
# the next prime on command


def is_even(num):
    if num % 2 == 0:
        return True
    return False


def is_odd(num):
    if not num % 2 == 0:
        return True
    return False


def is_prime(num):
    for i in range(2, num):
        if num % i == 0:
            return False
    return True


def generate_even(max_num):
    for num in range(max_num):
        if is_even(num):
            yield num


def generate_odd(max_num):
    for num in range(max_num):
        if is_odd(num):
            yield num


def generate_prime(max_num):
    for num in range(2, max_num):
        if is_prime(num):
            yield num


even = generate_even(100)
print(next(even))
print(next(even))
print(next(even))

odd = generate_odd(100)
print(next(odd))
print(next(odd))
print(next(odd))

prime = generate_prime(100)
print(next(prime))
print(next(prime))
print(next(prime))


double = (x * 2 for x in range(10))
print(next(double))
print(next(double))
print(next(double))

for num in double:
    print(num)
