import sys

def main():
    # Read all input at once to handle both space-separated and line-separated cases
    data = sys.stdin.read().split()
    if not data:
        return
        
    try:
        # First number is N
        n = int(data[0])
        # Next N numbers are the integers to check
        # Use range-based comprehension to avoid Pylance slice-overload ambiguity
        numbers = [int(data[i]) for i in range(1, min(n + 1, len(data)))]
        
        # Use all() to check if every number is non-negative (>= 0)
        if all(x >= 0 for x in numbers):
            print("Yes")
        else:
            print("No")
            
    except (ValueError, IndexError):
        return

if __name__ == "__main__":
    main()
