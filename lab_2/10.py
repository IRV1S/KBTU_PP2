n = int(input())
arr = list(map(int, input().split()))

arr.sort()

arr.reverse()


print(' '.join(map(str, arr)))