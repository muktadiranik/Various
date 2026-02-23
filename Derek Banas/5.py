def add_numbers(*numbers):
    total = 0
    for number in numbers:
        total += number
    return total


print(add_numbers(1, 2, 3, 4, 5))


global_name = "Alice"


def change_global_name():
    global global_name
    global_name = "Bob"


change_global_name()
print(global_name)


def solve_equation(equation) -> tuple[float, float] | bool:
    x, operator, y, equal, result = equation.split()
    x, y, result = int(x), int(y), int(result)
    if operator == "+":
        return result - y, result - x
    elif operator == "-":
        return result + y, result + x
    elif operator == "*":
        return result / y, result / x
    elif operator == "/":
        return result * y, result * x
    else:
        return False


print(solve_equation("5 + 8 = 13"))
print(solve_equation("5 - 8 = 13"))
print(solve_equation("5 * 8 = 13"))
print(solve_equation("5 / 8 = 13"))


def check_prime_number(number) -> bool | None:
    for i in range(2, number):
        if number % 2 == 0:
            return False
        return True
    return None


print(check_prime_number(11))
print(check_prime_number(12))


def get_prime_numbers(num_range) -> list[int]:
    prime_numbers = []
    for i in range(num_range):
        if check_prime_number(i):
            prime_numbers.append(i)
    return prime_numbers


print(get_prime_numbers(10))


# Create function that calculates the rectangle area
def calculate_rectangle_area(width, height) -> float:
    if width < 0 or height < 0:
        raise ValueError("Width and height must be positive")
    return width * height


print(calculate_rectangle_area(10, 20))


# Create function that calculates the rectangle perimeter
def calculate_rectangle_perimeter(width, height) -> float:
    if width < 0 or height < 0:
        raise ValueError("Width and height must be positive")
    return 2 * (width + height)


print(calculate_rectangle_perimeter(10, 20))


# Create function that calculates the circle area
import math


def calculate_circle_area(radius) -> float:
    if radius < 0:
        raise ValueError("Radius must be positive")
    return math.pi * radius * radius


print(calculate_circle_area(10))


# Create function that calculates the circle perimeter
def calculate_circle_perimeter(radius) -> float:
    if radius < 0:
        raise ValueError("Radius must be positive")
    return 2 * math.pi * radius


print(calculate_circle_perimeter(10))
