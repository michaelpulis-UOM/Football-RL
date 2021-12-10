import cv2
import numpy as np
import json
import glob
import itertools
from itertools import tee, zip_longest
from tqdm import tqdm
import matplotlib.pyplot as plt

class Statistics():
    def __init__(self):
        self.posession_limit = 10

    def loadSingleFile(self, fileName):
        with open(fileName, "r") as file:
            if(self.events == None):
                self.events = json.load(file)
            else:
                self.events.append(json.load(file))

    def loadFilesFromDirectory(self, mappingName, dirName):
        file_names = [dirName+ a.split('\\')[1] for a in glob.glob(mappingName)]
        print(f"INFO: Loaded {len(file_names)} files...")
        self.events = []

        for name in tqdm(file_names):
            with open(name, "r", encoding='UTF-8') as file:
                self.events.append(json.load(file))

    def getPosessionChains(self):
        lastNumber = -1
        chain_length = 0
        chains = [0 for i in range(self.posession_limit + 1)]
        for game in self.events:
            lastNumber = -1
            chain_length = 0
            for event in game[4:]:
                id = event['team']['id']
                if lastNumber == id: 
                    chain_length += 1
                else:
                    if(chain_length <= self.posession_limit):
                        chains[chain_length] += 1
                    lastNumber = id
                    chain_length = 1
            # print(id, chain_length)
        
        return chains[1:]

    def drawHistogramAtLeastN(self, data, title):
        atLeastData = []
        for i, value in enumerate(data):
            atLeastData.append(sum(data[i:]))
        
        self.drawHistogram(atLeastData, title)

    def drawHistogram(self, data, title):
        plt.figure(), 
        plt.bar(range(self.posession_limit+1)[1:], data) 
        self.add_value_labels(plt.gca(), spacing=5)

        plt.ylim(0, max(data)*1.2)
        plt.xticks(range(self.posession_limit+1)[1:])
        plt.title(title)
        plt.xlabel("Sequence Length")
        plt.ylabel("Frequency")

    # https://stackoverflow.com/posts/48372659/revisions
    def add_value_labels(self, ax, spacing=5):
        """Add labels to the end of each bar in a bar chart.

        Arguments:
            ax (matplotlib.axes.Axes): The matplotlib object containing the axes
                of the plot to annotate.
            spacing (int): The distance between the labels and the bars.
        """

        # For each bar: Place a label
        for rect in ax.patches:
            # Get X and Y placement of label from rect.
            y_value = rect.get_height()
            x_value = rect.get_x() + rect.get_width() / 2

            # Number of points between bar and label. Change to your liking.
            space = spacing
            # Vertical alignment for positive values
            va = 'bottom'

            # If value of bar is negative: Place label below bar
            if y_value < 0:
                # Invert space to place label below
                space *= -1
                # Vertically align label at top
                va = 'top'

            # Use Y value as label and format number with one decimal place
            if(int(y_value) == y_value): label = "{:.0f}".format(y_value)
            else: label = "{:.1f}".format(y_value)

            # Create annotation
            ax.annotate(
                label,                      # Use `label` as label
                (x_value, y_value),         # Place label at end of the bar
                xytext=(0, space),          # Vertically shift label by `space`
                textcoords="offset points", # Interpret `xytext` as offset in points
                ha='center',                # Horizontally center label
                va=va)                      # Vertically align label differently for
                                            # positive and negative values.

def main():
    statistics = Statistics()
    statistics.loadFilesFromDirectory("three-sixty/*", "events/")
    # statistics.loadSingleFile("data.json")
    posession_chain = statistics.getPosessionChains()
    statistics.drawHistogram(posession_chain, "Number of sequences that have X events")
    statistics.drawHistogramAtLeastN(posession_chain, "Number of sequences that have at least X events")
    plt.show()


if __name__ == "__main__":
    main()