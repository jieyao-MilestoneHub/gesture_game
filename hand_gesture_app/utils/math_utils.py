import random

# 隨機生成計算題目
def generate_question(operation):
    if operation == 'add':
        # 確保答案在 1 到 5 之間
        while True:
            num1 = random.randint(1, 5)
            num2 = random.randint(1, 5)
            answer = num1 + num2
            if 1 <= answer <= 5:
                question = f"{num1} + {num2}"
                return question, answer
    elif operation == 'subtract':
        # 確保答案在 -5 到 5 之間，且不為0
        while True:
            num1 = random.randint(-5, 5)
            num2 = random.randint(-5, 5)
            answer = num1 - num2
            if -5 <= answer <= 5 and answer != 0:
                question = f"{num1} - ({num2})"
                return question, answer
    elif operation == 'mixed':
        # 隨機選擇加減法
        op = random.choice(['add', 'subtract'])
        return generate_question(op)