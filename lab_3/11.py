class Pair:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def add(self, other):
        sum_a = self.a + other.a
        sum_b = self.b + other.b
        return Pair(sum_a, sum_b)


a1, b1, a2, b2 = map(int, input().split())

pair1 = Pair(a1, b1)
pair2 = Pair(a2, b2)

result = pair1.add(pair2)

print(f"Result: {result.a} {result.b}")