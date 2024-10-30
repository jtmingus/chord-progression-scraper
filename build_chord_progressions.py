from unique_chords import UniqueChords
from processed import Processed

unique_chords = UniqueChords()
processed = Processed()
chords = processed.getChords()


f = open("output/final_progressions.csv", "r+")


for chord in chords:
    ids = chord[-1].split(",")
    if len(ids) != 4:
        continue

    entry = ",".join(list(map(lambda id: unique_chords.getHtmlForId(id), ids)))
    f.write(entry + "\n")

f.close()
