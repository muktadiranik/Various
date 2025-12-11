# Programming involves listing all the things that must happen to solve a problem
# When writing a program first determine step-by-step what needs to happen
# Then convert those steps into the language being Python in this situation

# Every language has the following
# 1. The ability to accept input and store it in many ways
# 2. The ability to output information to the screen, files, etc.
# 3. The ability to conditionally do one thing or another thing
# 4. The ability to do something multiple times
# 5. The ability to make mathematical calculations
# 6. The ability to change data
# 7. (Object-Oriented Programming) Model real-world objects using code

# ---------- Hello World ----------

name = input("What is your name? ")
print(f"Hello {name}")

num_1, num_2 = input("Enter two numbers: ").split()
try:
    num_1 = int(num_1)
    num_2 = int(num_2)
except Exception as e:
    print(e)
else:
    print(num_1 + num_2)

summation = num_1 + num_2
difference = num_1 - num_2
product = num_1 * num_2
quotient = num_1 / num_2

print("{} + {} = {}".format(num_1, num_2, summation))
print("{} - {} = {}".format(num_1, num_2, difference))
print("{} * {} = {}".format(num_1, num_2, product))
print("{} / {} = {}".format(num_1, num_2, quotient))


# ---------- CALCULATOR ----------
num_1, operator, num_2 = input("Enter calculation").split()

if operator == "+":
    print("{} + {} = {}".format(num_1, num_2, int(num_1) + int(num_2)))
elif operator == "-":
    print("{} - {} = {}".format(num_1, num_2, int(num_1) - int(num_2)))
elif operator == "*":
    print("{} * {} = {}".format(num_1, num_2, int(num_1) * int(num_2)))
elif operator == "/":
    print("{} / {} = {}".format(num_1, num_2, int(num_1) / int(num_2)))
else:
    print("Use either + - * or / next time")

