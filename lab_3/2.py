n = int(input())

for d in [2, 3, 5]:
    while n % d == 0:
        n //= d

print("Yes" if n == 1 else "No")