number = input().strip()
is_valid = True

for digit in number:
    if int(digit) % 2 != 0:
        is_valid = False
        break

if is_valid:
    print("Valid")
else:
    print("Not valid")