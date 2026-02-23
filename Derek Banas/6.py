sample_dict = {"name": "John", "age": 30, "city": "New York"}

print(sample_dict["name"])
print(sample_dict.get("age"))
print(sample_dict.keys())
print(sample_dict.values())
print(sample_dict.items())

print("city" in sample_dict)
print("New" in sample_dict["city"])

for key, value in sample_dict.items():
    print(key, value)

print(sample_dict.get("number", None))

del sample_dict["name"]
print(sample_dict)

sample_dict["name"] = "John"
print(sample_dict)

sample_dict.clear()
print(sample_dict)

sample_dict = {"name": "John", "age": 30, "city": "New York"}
print(sample_dict)

sample_dict = dict(name="John", age=30, city="New York")
print(sample_dict)


def enter_customer_name() -> list[str] | None:
    customer_name_list = []
    while True:
        customer_name = input("Enter customer name: ")
        if customer_name.lower() == "quit":
            break
        confirm = input("Confirm customer name (y/n): ")
        if confirm.lower() == "quit":
            break
        if confirm.lower() == "y":
            customer_name_list.append(customer_name)

    return customer_name_list


# print(enter_customer_name())
"""
f = n + (n - 1) + (n - 2) + ... + 1 
"""


def factorial(num) -> float:
    if num == 1 or num == 0:
        return 1
    return num * factorial(num - 1)


print(factorial(5))

"""
0 + 1 = 1
1 + 1 = 2
1 + 2 = 3
2 + 3 = 5
3 + 5 = 8
"""


def fibonacci(num) -> float:
    if num == 0 or num == 1:
        return num
    return fibonacci(num - 1) + fibonacci(num - 2)


print(fibonacci(8))
