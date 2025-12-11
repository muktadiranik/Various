# ---------- READING & WRITING TEXT ----------
import os

try:
    with open("data.txt", mode="w", encoding="utf-8") as file:
        file.write("Hello World")
except Exception as e:
    print(e)
finally:
    file.close()
    print(file.closed)

try:
    with open("data.txt", mode="r", encoding="utf-8") as file:
        print(file.read())
except Exception as e:
    print(e)
finally:
    file.close()
    print(file.closed)

try:
    os.rename("data.txt", "text.txt")
except Exception as e:
    print(e)
finally:
    print(os.getcwd())
    print(os.listdir("."))
    os.remove("text.txt")

poem = "Mary had a little lamb"
"Its fleece was white as snow"
"And everywhere that Mary went"
"The lamb was sure to go"

try:
    with open("poem.txt", mode="w", encoding="utf-8") as file:
        file.write(poem)
except Exception as e:
    print(e)
finally:
    file.close()
    print(file.closed)

try:
    with open("poem.txt", mode="r", encoding="utf-8") as file:
        print(file.readline())
except Exception as e:
    print(e)
finally:
    file.close()
    print(file.closed)


# ---------- PROBLEM : Fibonacci sequence ----------
def fibonacci_sequence(num):
    if num == 0:
        return 0
    if num == 1:
        return 1
    return fibonacci_sequence(num - 1) + fibonacci_sequence(num - 2)


def print_fibonacci_sequence():
    print([fibonacci_sequence(i) for i in range(10)])


print_fibonacci_sequence()
