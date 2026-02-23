import sys


print(sys.argv)

if len(sys.argv) == 1:
    print("Please enter a number")
    sys.exit()
else:
    password = sys.argv[1]
    print(password)
