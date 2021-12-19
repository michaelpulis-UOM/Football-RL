import cv2
import numpy as np
import json
import glob
import itertools
from itertools import tee, zip_longest
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


class Statistics():
    def __init__(self):
        self.possession_limit = 100

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
                if(self.isMaleGame(name.split("/")[1].replace(".json", ""))):
                    self.events.append(json.load(file))
    
        print(f"INFO: Loaded {len(self.events)} games" )

    def getPossessionChains(self):
        lastNumber = -1
        chain_length = 0
        chains = [0 for i in range(self.possession_limit + 1)]
        for game in self.events:
            lastNumber = -1
            chain_length = 0
            offset = 4
            for i, event in enumerate(game[offset:]):
                id = event['team']['id']
                if lastNumber == id and chain_length < self.possession_limit: 
                    chain_length += 1
                else:
                    if(event['type']['name'] == 'Pressure' and game[i+offset]['team']['id'] == lastNumber and not(chain_length >= self.possession_limit)): continue
                    else:
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
        plt.bar(range(self.possession_limit+1)[1:], data) 
        self.add_value_labels(plt.gca(), spacing=5)

        plt.ylim(0, max(data)*1.2)
        plt.xticks(range(self.possession_limit+1)[1:])
        plt.title(title)
        plt.xlabel("Sequence Length")
        plt.ylabel("Frequency")

    def getEventsStatistics(self, title):
        current_events = {}
        for game in self.events:
            for event in game[4:]:
                if(event['type']['name'] in current_events): current_events[event['type']['name']] += 1
                else: current_events[event['type']['name']] = 1
        
        items  = current_events.items()
        names = [a[0] for a in items]
        values = [a[1] for a in items]


        plt.bar(names, values)
        plt.xticks(names, labels=names, rotation='vertical')
        plt.title(title)
        self.add_value_labels(plt.gca(), spacing=5)
        # plt.show()

    def loadMatchData(self):
        self.matches = {}
        files = glob.glob('matches/**/*.json', recursive=True)
        for filename in files:
            temp_j = None
            with open(filename, 'r', encoding='utf_8') as file:
                temp_j = json.load(file)
            
            for item in temp_j:
                if(item['home_team']['home_team_gender'].lower() == 'male'):
                    self.matches[item['match_id']] = item

    def getGoalsScoredInMatch(self, match_id):

        match_id = int(str(match_id).replace('.json', ''))
        return self.matches[match_id]['home_score'] + self.matches[match_id]['away_score']

    def getTotalMatchXG(self, id):
        match = None
        with open("events/"+str(id)+".json", 'r', encoding='utf_8') as file:
            match = json.load(file)
        
        totalXG = 0.0
        for event in match:
            if(event['type']['name'] == 'Shot'):
                totalXG += event['shot']['statsbomb_xg']
        
        return totalXG

    def isMaleGame(self, id):
        id = int(id)
        return self.matches[id]['home_team']['home_team_gender'].lower() == 'male'
        
    def getPossessionChainsFromDataset(self):
        
        possessions = []
        last_possession_number = -1
        chain = 0
        
        print("INFO: Loading Possession Chains from Dataset")
        for game in tqdm(self.events):
            chain = 0
            for event in game:
                if(event['possession'] != last_possession_number or chain >= self.possession_limit):
                    possessions.append(chain)
                    chain = 1
                    last_possession_number = event['possession']
                else:
                    chain += 1

                # print(event['type']['name'], chain)

            # exit()

        result = [ 0 for i in range(self.possession_limit+1)]

        for i in possessions:
            result[i] += 1

        return result[1:]

    def compareXG(self):
        ids = list(self.matches.keys())
        goals = []
        xg = []

        for id in tqdm(ids):
            goals.append(self.getGoalsScoredInMatch(id))
            xg.append(self.getTotalMatchXG(id))

        plt.scatter(goals, xg)
        plt.title("Goals Scored vs xG Generated")
        plt.ylabel('xG')
        plt.xlabel('Goals')
        plt.show()

        print(sum(goals) , " vs " , sum(xg))
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
    statistics.loadMatchData()

    statistics.loadFilesFromDirectory("three-sixty/*", "events/")
    possession_chain = statistics.getPossessionChainsFromDataset()
    # print(possession_chain)
    # statistics.loadSingleFile("data.json")
    statistics.getEventsStatistics("Frequency of each event")
    # possession_chain = statistics.getPossessionChains()
    # statistics.drawHistogram(possession_chain, "Number of sequences that have X events")
    # statistics.drawHistogramAtLeastN(possession_chain, "Number of sequences that have at least X events")
    plt.show()

    # statistics.loadMatchData()
    # statistics.compareXG()


if __name__ == "__main__":
    main()