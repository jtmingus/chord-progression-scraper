"""Script to verify any chord progressions missed by extract_chords_v2.

This script was duplicated from extract_chords_v2.py and was only used as final verification that all 4-chord progressions were found.
"""

import requests
from unique_chords import UniqueChords
from processed import Processed
from to_process import ToProcess
import time
import traceback
from chord_tree import ChordTreeNode
import password
import json

CHORD_PROGRESSION_LENGTH = 4
MIN_CHORD_PROBABILITY = 0.005


def getAuthToken():
    headers = {"Content-Type": "application/json"}
    data = {"username": "jtmingus", "password": password.password}
    r = requests.post(
        "https://api.hooktheory.com/v1/users/auth",
        headers=headers,
        data=json.dumps(data),
    )
    j = r.json()
    return j["activkey"]


activKey = getAuthToken()
headers = {"Authorization": "Bearer " + activKey}

uniqueChords = UniqueChords()
toProcess = ToProcess()
processed = Processed()
processedChords = processed.getChords()


def jsonToChord(obj) -> list:
    if not uniqueChords.hasChord(obj["chord_ID"]):
        uniqueChords.writeNewChord(obj["chord_ID"], obj["chord_HTML"])
    return [
        obj["chord_ID"],
        obj["chord_HTML"],
        str(obj["probability"]),
        obj["child_path"],
    ]


def getNextChords(path: str, backoff=30):
    global activKey, headers
    print("making request")
    try:
        r = requests.get(
            "https://api.hooktheory.com/v1/trends/nodes?cp={}".format(path),
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.Timeout as e:
        print("connection error. Retrying...")
        time.sleep(10)
        activKey = getAuthToken()
        headers = {"Authorization": "Bearer " + activKey}
        return getNextChords(path, backoff)

    # make sure we don't exceed rate limits.
    if int(r.headers["X-Rate-Limit-Remaining"]) < 1:
        print("sleeping for {} seconds".format(r.headers["X-Rate-Limit-Reset"]))
        time.sleep(int(r.headers["X-Rate-Limit-Reset"]) + 5)
        return getNextChords(path, backoff)
    if r.text.strip() == "[]null":
        print("no results")
        return []
    j = r.json()
    if "status" in j and int(j["status"]) != 200:
        if backoff > 120:
            raise Exception("Too long of backoff")
        print("backing off for {} seconds".format(backoff))
        time.sleep(backoff)
        return getNextChords(path, backoff * 2)
    print("response results: {}".format(len(j)))
    return j


def getChordTree():
    root = ChordTreeNode("", "", 1.0, "")
    # Start at first chords
    for chord in sorted(processedChords, key=lambda chord: len(chord[-1].split(","))):
        id, html, probability, path = chord
        chordNode = ChordTreeNode(id, html, probability, path)

        pathChords = path.strip().split(",")
        currNode = root
        for pathSegment in pathChords[:-1]:
            if pathSegment not in currNode.children:
                print(
                    "ERROR processing {}. Missing segment: {}".format(
                        chord, pathSegment
                    )
                )
            currNode = currNode.children[pathSegment]
        currNode.children[id] = chordNode

    return root


chordTree = getChordTree()

q = [(chordTree, 0)]

chordsToProcess = []

# Find all nodes that don't have children up to 4 chords.
while len(q):
    node, level = q.pop(0)
    # print(node)
    if (
        level < CHORD_PROGRESSION_LENGTH
        and float(node.probability) >= MIN_CHORD_PROBABILITY
        and len(node.children) == 0
    ):
        print("Need to process {}".format(node.path))
        chordsToProcess.append([node.chord_ID, node.html, node.probability, node.path])

    for childNode in node.children.values():
        q.append((childNode, level + 1))


toProcess.writeChords(chordsToProcess)


# Populate missing chords
while len(chordsToProcess):
    chord = chordsToProcess.pop(0)
    id, html, probability, path = chord
    level = len(path.split(","))

    if level >= CHORD_PROGRESSION_LENGTH:
        processed.writeChord(chord)
        continue

    print("processing node: {}".format(" ".join(chord)))

    processed.writeChord(chord)

    try:
        nextJsonChords = getNextChords(path)
        for jsonChord in nextJsonChords:
            newChord = jsonToChord(jsonChord)
            chordsToProcess.append(newChord)
    except Exception as e:
        print("EXITING ", e)
        print(traceback.format_exc())
        chordsToProcess.append(chord)
        toProcess.writeChords(chordsToProcess)
        exit()
