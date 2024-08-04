N = int(input("Anzahl Bahnhöfe:\n"))
M = int(input("Hauptbahnhof:\n"))

for i in set(range(N)) - {M}:
    print(f"{i} {M}")
