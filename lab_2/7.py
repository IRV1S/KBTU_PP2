n = int(input())
index = 1
numbers = list(map(int, input().split()))
total = max(numbers)
for i in numbers:
    if i == total:
        print(index)
    index += 1