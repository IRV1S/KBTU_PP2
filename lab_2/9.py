n = int(input())
arr = list(map(int, input().split()))


min_val = min(arr)
max_val = max(arr)


for i in range(n):
    if arr[i] == max_val:
        arr[i] = min_val


print(' '.join(map(str, arr)))