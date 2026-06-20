import sys

import time

def slow_print(text, delay=0.1):

    for char in text:

        sys.stdout.write(char)

        sys.stdout.flush()

        time.sleep(delay)

    print()

print("攻撃戦だ" * 5)

print("掛け声をどうぞ")
 
s = input(":").strip()

answer = "将軍様のために"

if s == answer:

    print("正解ニダ")

    for _ in range(50):

        print(answer)

else:

    print("不正解ニダ")

    print("お前は非国民ニダ処刑します")

    slow_print("パｧｧｧｧｧｧｧｧｧｧｧｧｧｧｧｧｧｧｧｧｧｧﾝ", 0.02)

    time.sleep(1)

    slow_print("game ♂ver", 0.1)

 