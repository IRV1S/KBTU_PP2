n = int(input())
result = list(map(int, input().split()))
counter = 0
for i in result:
    if i > 0:
        counter += 1
print(counter)
