"""Class to handle reading and writing chords that have already been processed."""


class Processed:
    def __init__(self):
        self.f = open("output/processed.txt", "r+")
        self.uniqueChordStrings = set()
        self.chords = self.__getChordsToProcess()

    def __getChordsToProcess(self):
        lines = self.f.readlines()
        chords = []
        for line in lines[1:]:
            if not line.strip():
                continue
            chords.append(line.strip().split())
            self.uniqueChordStrings.add(line.strip())
        return chords

    def getChords(self):
        return self.chords

    def isProcessed(self, chord):
        return " ".join(chord) in self.uniqueChordStrings

    def writeChord(self, chord):
        chordString = " ".join(chord)
        if chordString not in self.uniqueChordStrings:
            self.f.write(" ".join(chord) + "\n")
