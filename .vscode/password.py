import random
print("roulette(only 8 people)")
a=input("what name:")
b=input("what name:")
c=input("what name:")
d=input("what name:")
e=input("what name:")
f=input("what name:")
g=input("what name:")
h=input("what name:")
dict={
    1:a,
    2:b,
    3:c,
    4:d,
    5:e,
    6:f,
    7:g,
    8:h,
}
s=random.randint(1,8)
print(dict[s])

