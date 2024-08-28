"""Class representing all unique chords found from HookTheory."""


class UniqueChords:
    def __init__(self):
        self.file = open("output/unique_chords.csv", "r+")
        self.uniqueChords = set()
        self.__processUniqueChords()

    def __processUniqueChords(self):
        lines = self.file.readlines()
        for line in lines[1:]:
            if not line.strip():
                continue
            id, html = line.strip().split(",")
            self.uniqueChords.add(id)

    def hasChord(self, id: str) -> bool:
        return id in self.uniqueChords

    def writeNewChord(self, id: str, html: str):
        if id in self.uniqueChords:
            return
        self.uniqueChords.add(id)
        self.file.write(id + "," + html + "\n")
