"""Script to read 4-chord progressions from HookTheory's API.

This script is written to be run in batches, so it reads/writes already processed chord progressions via helper classes. It continuously calls HookTheory's API to find chord progressions. For each chord, it finds all chords that have more than a 0.5% chance of following it.
"""

import requests
from unique_chords import UniqueChords
from processed import Processed
from to_process import ToProcess
import time
import traceback
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
toProcessChords = toProcess.getChords()
processed = Processed()


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

    print("receive response")
    # make sure we don't exceed rate limits.
    if int(r.headers["X-Rate-Limit-Remaining"]) < 1:
        print("sleeping for {} seconds".format(r.headers["X-Rate-Limit-Reset"]))
        time.sleep(int(r.headers["X-Rate-Limit-Reset"]) + 5)
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
    return j


while len(toProcessChords):
    chord = toProcessChords.pop(0)
    id, html, probability, path = chord
    level = len(path.split(","))

    if processed.isProcessed(chord):
        print("already processed")
        continue

    # Skip low probability.
    if float(probability) < MIN_CHORD_PROBABILITY:
        print("skipping")
        continue

    if level >= CHORD_PROGRESSION_LENGTH:
        processed.writeChord(chord)
        continue

    print("processing node: {}".format(" ".join(chord)))

    processed.writeChord(chord)

    # Don't go beyond 4 levels
    if level == CHORD_PROGRESSION_LENGTH:
        break

    try:
        nextJsonChords = getNextChords(path)
        for jsonChord in nextJsonChords:
            newChord = jsonToChord(jsonChord)
            toProcessChords.append(newChord)
    except Exception as e:
        print("EXITING ", e)
        print(traceback.format_exc())
        toProcessChords.append(chord)
        toProcess.writeChords(toProcessChords)
        exit()
