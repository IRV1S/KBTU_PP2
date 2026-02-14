import math


class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2


radius = int(input())

circle = Circle(radius)

area = circle.area()

print(f"{area:.2f}")