import random

stations = []

N = int(input("Stationscount:\n"))
D = 0


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] + b[1]) ** 2) ** 0.5


for i in range(N):
    currentStation = (random.randrange(N*10), random.randrange(N*10))
    for s in stations:
        D += distance(currentStation, s)
    stations.append(currentStation)

print(int(10*D//N))
print(N)
for s in stations:
    print(f"{s[0]} {s[1]}")
