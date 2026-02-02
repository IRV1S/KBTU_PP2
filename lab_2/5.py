n = int(input())

if n == 1:
    print("YES")
else:
    power_of_two = False
    current = 1

    while current <= n:
        current *= 2
        if current == n:
            power_of_two = True
            break

    if power_of_two:
        print("YES")
    else:
        print("NO")