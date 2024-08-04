import math
from typing import Annotated

import networkx as nx
import numpy as np
import uvicorn
from fastapi import File, UploadFile, Form
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

scores = {}

tasksCount = 4


@app.get("/", response_class=HTMLResponse)
def root():
    res = []
    with open("preset.html") as f:
        res.append(f.read())
    res.append('<a href="/scores"><h2 style="margin-bottom:2em">Zur Bestenliste</h2></a>')
    for i in range(1, tasksCount+1):
        res.append(
            f"""<form method="post" action="/upload{i}" enctype="multipart/form-data" title="Aufgabe {i}">
                <h3 style="margin-top:0">Aufgabe {i}</h3>
                <h4>Eingabe</h4>
                <a href="/inputs/input{i}.txt" download>
                    Eingabedatei herunterladen
                </a><br>
                <h4>Abgabe</h4>
                <input type="text" name="team" placeholder="Teamname" required>
                <input
                type="file"
                name="file"
                accept=".txt"
                value="Abgabedatei auswählen"
                title="Abgabedatei auswählen"
                />
                <input type="submit" value="Abgabe hochladen">
            </form>""")
    res.append("</body></html>")
    return "".join(res)


@app.get("/scores", response_class=HTMLResponse)
def scoresHTML():
    ret = []
    with open("preset.html") as f:
        ret.append(f.read())

    ret.append("<h2>Bestenliste</h2>")
    ret.append("<table><tr><th>Teamname</th><th>A1</th><th>A2</th><th>A3</th><th>A4</th><th>Gesamt</th></tr>")

    for team, score in sorted(scores.items(), key=lambda x: x[1][-1], reverse=True):
        ret.append(
            f"<tr><td>{team}</td><td>{score[0]}</td><td>{score[1]}</td><td>{score[2]}</td><td>{score[3]}</td><td>{score[4]}</td><tr>")

    ret.append('</table><a href="/"><h2 style="margin-bottom:2em">Zurück</h2></a></body></html>')
    return "".join(ret)


def genarateUploadHTML(n, succes, res, score):
    ret = []
    with open("preset.html") as f:
        ret.append(f.read())

    if succes:
        ret.append("<p>Die Abgabe wurde erfolgreich hochgeladen</p>")
        ret.append(f"<p>Ihr habt eine Durchschnittliche kürzeste Strecke von {int(100 * res) / 100 if math.inf != res else 'unendlich '}km, damit erreicht ihr eine Punktzahl von {score} für Aufgabe {n}.</p>")
    else:
        ret.append("<p>Die Abgabe ist fehlgeschlagen</p>")
        ret.append(f"<p>{res}</p>")

    ret.append('<a href="/"><h2 style="margin-bottom:2em">Zurück</h2></a></body></html>')
    return "".join(ret)


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] + b[1]) ** 2) ** 0.5


def calc_score(abgabe, n):
    S = 0
    N = 0
    stations = []
    with open(f"inputs/input{n}.txt") as f:
        S = int(f.readline().strip())
        N = int(f.readline().strip())
        for l in f:
            x, y = map(int, l.strip().split())
            stations.append((x, y))
    try:
        connenctions = []

        for l in abgabe:
            a, b = map(int, str(l, "UTF-8").strip().split())
            d = distance(stations[a], stations[b])
            S -= d
            if S < 0:
                return False, "Mehr Schiene verbaut als vorhanden", 0
            connenctions.append((a, b, d))

        G = nx.Graph()
        G.add_weighted_edges_from(connenctions)
        if len(G.nodes) < N:
            return False, "Nicht alle Bahnhöfe wurden angebunden", 0
        fw = nx.floyd_warshall_numpy(G)
        return True, np.sum(fw) / fw.size, int(S * fw.size / np.sum(fw))

    except Exception as E:
        return False, "Fehler im Eingabe-Format", 0


for i in range(1, tasksCount + 1):
    @app.post(f"/upload{i}", response_class=HTMLResponse)
    def upload(team: Annotated[str, Form()], file: UploadFile = File(...), i = i):
        try:
            succes, res, score = calc_score(file.file, i)
            print(f"{team} hat Aufgabe {i} abgegeben und {score} Punkte erzielt.")

            if team not in scores.keys():
                scores[team] = [0 for _ in range(tasksCount+1)]

            scores[team][i-1] = max(scores[team][i-1], score)
            scores[team][-1] = sum(scores[team][:-1])

            file.file.close()
            return genarateUploadHTML(i, succes, res, score)

        except Exception:
            return "There was an error uploading the file"
        finally:
            file.file.close()


    @app.get(f"/inputs/input{i}.txt")
    def a(i = i):
        def iterfile():
            with open(f"./inputs/input{i}.txt", mode="rb") as file_like:
                yield from file_like


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
