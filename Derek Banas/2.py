for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
    print(f"{i}")

list_1 = [i for i in range(10) if i % 2 == 0]
list_2 = [i for i in range(10) if i % 2 == 1]

print(list_1)
print(list_2)


float_num = 1.2468
print(f"rounded to two decimal places: {round(float_num, 2)}")

money = 1000
interest_rate = 15
interest_rate = interest_rate * 0.1
print(f"interest rate: {interest_rate}")

for year in range(10):
    money += money * interest_rate
    print(f"year {year + 1}: {money}")


i = 0.1 + 0.1 + 0.1 - 0.3
print(i)

i = 0.11111111111111111111111111111111
j = 0.00000000000000010000000000000001

print(i + j)


# from random import randint, randrange
#
# flag = True
# num = randint(1, 10)
# while flag:
#     num += 1
#     print(num)
#     if num == 10:
#         break
#
# print(f"type(randrange)", type(randrange))

# custom_range = randrange(0, 10, 1)
# flag = True
# num = 0
# while flag:
#     num += 1
#     print(num)
#     if num == custom_range:
#         flag = False


"""
    #
   ###
  #####
 #######
#########
    #
"""
"""
1st line: 3 spaces and 1 hash
2nd line: 2 spaces and 3 hash
3rd line: 1 space and 5 hash
4th line: 0 space and 7 hash
5th line: 1 space and 9 hash
6th line: 2 spaces and 11 hash
7th line: 3 spaces and 13 hash
"""

for i in range(5):
    print(" " * (5 - i) + "#" * (2 * i + 1))

"""
***********
  *******
   *****
    ***
     *
     
1st line: 0 spaces and 11 star
2nd line: 2 spaces and 7 star
3rd line: 3 spaces and 5 star
4th line: 4 spaces and 3 star
5th line: 5 spaces and 1 star
"""

for i in range(5, 0, -1):
    print(" " * (5 - i), "*" * (2 * i + 1))

print("# ---------- PROBLEM : DRAW A PINE TREE ----------")
"""
     *
    ***
   *****
  *******
***********
  *******
   *****
    ***
     *
     
1st line: 5 spaces and 1 star
2nd line: 4 spaces and 3 star
3rd line: 3 spaces and 5 star
4th line: 2 spaces and 7 star
5th line: 0 spaces and 11 star
6th line: 2 spaces and 7 star
7th line: 3 spaces and 5 star
8th line: 4 spaces and 3 star
9th line: 5 spaces and 1 star 
"""

for i in range(6):
    print(" " * (5 - i) + "*" * (2 * i + 1))
for i in range(4, -1, -1):
    print(" " * (4 - i), "*" * (2 * i + 1))
