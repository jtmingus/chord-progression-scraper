"""Class to handle reading and writing chords that need to be processed."""


class ToProcess:
    def __init__(self):
        f = open("output/to_process.txt", "r")
        self.uniqueChords = set()
        self.chords = self.__getChordsToProcess(f)
        f.close()

    def __getChordsToProcess(self, file):
        lines = file.readlines()
        self.header = lines[0]
        chords = []
        for line in lines[1:]:
            if not line.strip():
                continue
            chords.append(line.strip().split())
        return chords

    def getChords(self):
        return self.chords

    def writeChords(self, chords):
        open("output/to_process.txt", "w").close()
        f = open("output/to_process.txt", "w")
        f.write(self.header)
        for chord in chords:
            f.write(" ".join(chord) + "\n")
        f.close()
