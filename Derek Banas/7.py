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


# ---------- TUPLES ----------
tuple_1 = (1, 2, 3, 4, 5)
print(tuple_1)
print(tuple_1[0:2])
print(len(tuple_1))
print(tuple_1.count(1))
print(tuple_1.index(1))

tuple_2 = tuple_1 + (6, 7, 8, 9, 10)
print(tuple_2)
print(f"tuple_1 * 2: {tuple_1 * 2}")
print(tuple_1[0])

print(2 in tuple_1)

for i in tuple_2:
    print(i, end=" ")
    print(i % 2 == 0, end=" ")

# Convert a List into a Tuple
list_1 = [1, 2, 3, 4, 5]
tuple_1 = tuple[int, ...](list_1)
print(type(tuple_1))

# Convert a Tuple into a List
list_1 = list(tuple_1)
print(type(list_1))

print(max(tuple_1))
print(min(tuple_1))
