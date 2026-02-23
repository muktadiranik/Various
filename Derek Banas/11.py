def do_math(func, *args):
    return func(*args)


def multiply(*args):
    total = 1
    for arg in args:
        total *= arg
    return total


print(multiply(1, 2, 3))
print(do_math(multiply, 1, 2, 3))


def get_func_multiply_by_num(num):
    def multiply_by(value):
        return num * value

    return multiply_by


multiply_by_5 = get_func_multiply_by_num(5)
print(multiply_by_5(10))


def get_func_addition_by_num(num):
    def add_by(value):
        return num + value

    return add_by


add_by_5 = get_func_addition_by_num(5)
print(add_by_5(10))


func_list = [get_func_multiply_by_num, get_func_addition_by_num]
for func in func_list:
    print(func.__str__(), func(5)(10))


def is_odd(value):
    return value % 2 != 0


def is_even(value):
    return value % 2 == 0


def change_list(_list, func):
    odd_list = []
    even_list = []

    for i in _list:
        if func(i):
            odd_list.append(i)
        else:
            even_list.append(i)
    # odd_list = odd_list.append(i for i in _list if func(i))
    # even_list = even_list.append(i for i in _list if not func(i))
    odd_list_shortcut = [i for i in _list if func(i)]
    even_list_shortcut = [i for i in _list if not func(i)]

    return odd_list, even_list, odd_list_shortcut, even_list_shortcut


list_1 = range(1, 21)
print(change_list(list_1, is_odd))


def typed_function(name: str, age: int, weight: float) -> dict[str, int]:
    return {"name": name, "age": age, "weight": weight}


print(typed_function("Derek", 41, 165.5))
print(typed_function.__annotations__)


# ---------- ANONYMOUS FUNCTIONS : LAMBDA ----------
# lambda is like def, but rather then assign the function
# to a name it just returns it. Because there is no name
# that is why they are called anonymous functions. You
# can however assign a lambda function to a name.

# This is their format
# lambda arg1, arg2,... : expression using the args

# lambdas are used when you need a small function, but
# don't want to junk up your code with temporary
# function names that may cause conflicts

add = lambda *args: sum(args)
print(add(1, 2, 3))

func_list = [lambda x: x**2, lambda x: x**3, lambda x: x**4]
for func in func_list:
    print(func(2))


func_dict = {
    "power 2": lambda x: x**2,
    "power 3": lambda x: x**3,
    "power 4": lambda x: x**4,
}

print(func_dict["power 2"](2))


import random

dict_key = random.choice(list(func_dict.keys()))
print(f"{dict_key}: {func_dict[dict_key](2)}")


flip_list = []
for i in range(101):
    flip_list.append(random.choice(["H", "T"]))
print(flip_list)
print(f"Heads: {flip_list.count('H')}")
print(f"Tails: {flip_list.count('T')}")


# ---------- MAP ----------
# Map allows us to execute a function on each item in a list
list_1 = range(1, 6)
print(list(map((lambda x: x**2), list_1)))

print(list(map(lambda x, y: x + y, [1, 2, 3], [1, 2, 3])))


# ---------- FILTER ----------
# Filter selects items from a list based on a function
print(list(filter(lambda x: x % 2 == 0, range(1, 21))))


# ---------- REDUCE ----------
# Reduce receives a list and returns a single result
from functools import reduce

print(reduce(lambda x, y: x + y, range(1, 6)))
print(reduce(lambda x, y: x * 5 + y * 5, range(1, 6)))
