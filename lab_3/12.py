class Employee:
    def __init__(self, name, base_salary):
        self.name = name
        self.base_salary = base_salary

    def total_salary(self):
        return float(self.base_salary)


class Manager(Employee):
    def __init__(self, name, base_salary, bonus_percent):
        super().__init__(name, base_salary)
        self.bonus_percent = bonus_percent

    def total_salary(self):
        return self.base_salary * (1 + self.bonus_percent / 100)


class Developer(Employee):
    def __init__(self, name, base_salary, completed_projects):
        super().__init__(name, base_salary)
        self.completed_projects = completed_projects

    def total_salary(self):
        return self.base_salary + (self.completed_projects * 500)


class Intern(Employee):
    def __init__(self, name, base_salary):
        super().__init__(name, base_salary)


data = input().split()

if data[0] == "Manager":
    emp = Manager(data[1], int(data[2]), int(data[3]))
elif data[0] == "Developer":
    emp = Developer(data[1], int(data[2]), int(data[3]))
else:  # Intern
    emp = Intern(data[1], int(data[2]))

total = emp.total_salary()
print(f"Name: {emp.name}, Total: {total:.2f}")