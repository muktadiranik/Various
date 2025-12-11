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

poem = "Mary had a little lamb \n\
Its fleece was white as snow \n\
And everywhere that Mary went \n\
The lamb was sure to go"

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


# ---------- PROBLEM : ANALYZE THE FILE ----------
try:
    with open("poem.txt", mode="r", encoding="utf-8") as file:
        while True:
            line = file.readline()
            print(f"line: {line}")
            print([(word, len(word)) for word in line.split()])
            print(
                f"word: {line.split()}, character count: {[(len(word)) for word in line.split()]}"
            )
            print(f"word count: {len(line.split())}")
            if not line:
                break
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
