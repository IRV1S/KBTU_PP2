def string_calculator():
    triple_to_digit = {
        "ONE": 1, "TWO": 2, "THR": 3, "FOU": 4, "FIV": 5,
        "SIX": 6, "SEV": 7, "EIG": 8, "NIN": 9, "ZER": 0
    }

    digit_to_triple = {v: k for k, v in triple_to_digit.items()}

    expression = input().strip()

    if '+' in expression:
        num1_str, num2_str = expression.split('+')
        operator = '+'
    elif '-' in expression:
        num1_str, num2_str = expression.split('-')
        operator = '-'
    elif '*' in expression:
        num1_str, num2_str = expression.split('*')
        operator = '*'

    def parse_number(num_str):
        triples = [num_str[i:i + 3] for i in range(0, len(num_str), 3)]
        digits = [triple_to_digit[triple] for triple in triples]
        result = 0
        for digit in digits:
            result = result * 10 + digit
        return result

    def format_number(num):
        if num == 0:
            return "ZER"

        digits = []
        temp = abs(num)
        while temp > 0:
            digits.append(temp % 10)
            temp //= 10
        digits.reverse()

        result = ""
        for digit in digits:
            result += digit_to_triple[digit]

        if num < 0:
            result = "-" + result

        return result

    num1 = parse_number(num1_str)
    num2 = parse_number(num2_str)

    if operator == '+':
        result_num = num1 + num2
    elif operator == '-':
        result_num = num1 - num2
    elif operator == '*':
        result_num = num1 * num2

    print(format_number(result_num))


string_calculator()