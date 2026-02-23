import re

# [ ]   : Match what is in the brackets
# [^ ]  : Match anything not in the brackets
# ( )   : Return surrounded submatch
# .     : Match any 1 character or space
# +     : Match 1 or more of what proceeds
# ?     : Match 0 or 1
# *     : Match 0 or More
# *?    : Lazy match the smallest match
# \b    : Word boundary
# ^     : Beginning of String
# $     : End of String
# \n    : Newline
# \d    : Any 1 number
# \D    : Anything but a number
# \w    : Same as [a-zA-Z0-9_]
# \W    : Same as [^a-zA-Z0-9_]
# \s    : Same as [\f\n\r\t\v]
# \S    : Same as [^\f\n\r\t\v]
# {5}   : Match 5 of what proceeds the curly brackets
# {5,7} : Match values that are between 5 and 7 in length
# ($m)  : Allow ^ on multiline string


the_string = "The cat cat fell fell out the window"
_regex = re.compile(r"(\b\w+)\s+\1")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


the_string = "<a href='#'><b>The Link</b></a>"
_regex = re.compile(r"<b>(.*?)</b>")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)
print(_regex.sub(r"\1", the_string))

the_string = "412-555-1212"
_regex = re.compile(r"(\d{3})-(\d{3}-\d{4})")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)
print(_regex.sub(r"(\1)\2", the_string))

the_string = "https://www.youtube.com http://www.google.com"
_regex = re.compile(r"(https?://([\w.]+))")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)
print(_regex.sub(r"<a href=\"\1\">\2</a>\n", the_string))

the_string = "One two three four"
_regex = re.compile(r"\b\w{5}\b")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


the_string = "1. Bread 2. Apples 3. Lettuce"
_regex = re.compile(r"(?<=\d.\s)\w+")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)
print(_regex.sub(r"1", the_string))


the_string = "<h1>I'm Important</h1> <h1>So am I</h1>"
_regex = re.compile(r"(?<=<h1>).+?(?=</h1>)")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)
print(_regex.sub(r"1", the_string))


the_string = "8 Apples $3, 1 Bread $1, 1 Cereal $4"
_regex = re.compile(r"(?<!\$)\d+")
print(_regex)
matches = re.findall(_regex, the_string)
print(matches)
print("Matches :", len(matches))
for i in matches:
    print(i)
print(_regex.sub(r"1", the_string))

matches = [int(i) for i in matches]
print(matches)

from functools import reduce

print(reduce((lambda x, y: x + y), matches))
