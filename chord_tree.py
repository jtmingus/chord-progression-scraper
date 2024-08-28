"""Class representing a chord in a chord progression.

This class functions as a node in a tree. Each chord can have N number of chords that follow it, each child is itself a ChordTreeNode. The chord ID is based on HookTheory's chord notation."""

from collections import defaultdict


class ChordTreeNode:
    def __init__(self, chord_ID: str, html: str, probability: float, path: str):
        self.chord_ID = chord_ID
        self.html = html
        self.probability = probability
        self.path = path
        self.children = defaultdict(lambda: ChordTreeNode)

    def __str__(self):
        return "{} {} {} {} - with children: {}".format(
            self.chord_ID, self.html, self.probability, self.path, len(self.children)
        )
