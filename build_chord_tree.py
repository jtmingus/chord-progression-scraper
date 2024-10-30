from chord_tree_node import ChordTreeNode


def getChordTree(processedChords):
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
