import sys

def main():
    # Read entire input and split by whitespace
    input_data = sys.stdin.read().split()
    if not input_data:
        return
        
    try:
        n = int(input_data[0])
        
        # A spans from index 1 to n
        a = [int(input_data[i]) for i in range(1, n + 1)]
        
        # B spans from index n+1 to 2n
        b = [int(input_data[i]) for i in range(n + 1, 2 * n + 1)]
        
        # Using zip and sum to compute the dot product
        # sum of A[i] * B[i] for i in 0..n-1
        dot_product = sum(x * y for x, y in zip(a, b))
        
        print(dot_product)
        
    except (ValueError, IndexError):
        # Handle cases where input data might be incomplete or malformed
        return

if __name__ == "__main__":
    main()
