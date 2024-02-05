a = "[['Паша', 2000], ['Миша', 5000]]"
c = a.split(', ')
b = []
for i in c:
    b.append(i.split(', '))

print(a)
print()
print(c)
print()
for i in b: print(i)