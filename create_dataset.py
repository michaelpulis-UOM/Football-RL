import glob
import numpy as np 
import json
from tqdm import tqdm


class CreateDataset():
    
    def __init__ (self):
        # Initialising Class Variables
        self.PASS = 0
        self.SHOOT = 1
        self.CARRY = 2
        self.CLEAR = 3
        self.FOUL = 4

        self.possession_limit = 5

        self.games = None
        self.events = None
        self.good_events = {
            
            'pass': self.PASS,
            'shot': self.SHOOT,
            'carry':self.CARRY,
            'clearance':self.CLEAR,
            # 'foul won': self.FOUL,
            'foul committed': self.FOUL,

        }

    def filter_game(self, dataset):
        return [ 
                    a for a in dataset 
                    if  ('type' in a)
                    and (a['type']['name'].lower() in self.good_events) 
                    and ('location' in a)
                ]
            
    def getIDFromAction(self, item):
        return 1.0 * self.good_events[item['type']['name'].lower()]

    # Dataset specifications:
    # x:
    # float: action ID (0 = PASS, 1 = SHOOT...etc)
    # float: x coordinate of action
    # float: y coordinate of action

    # y:
    # softmax between categories
    def createDataset(self):

        x, y = [], []
        for i in range(len(self.events)-1):

            action = self.events[i]
            next_action = self.events[i+1]

            x_entry = [self.getIDFromAction(action), action['location'][0], action['location'][1]]
            y_entry = np.zeros((len(self.good_events)))
            y_entry[int(self.getIDFromAction(next_action))] = 1
            
            x.append(x_entry)
            y.append(y_entry)

        return np.array(x), np.array(y)
            

    def loadFile(self, file_location):
        
        with open(file_location, 'r', encoding='utf-8') as file:
            game = json.load(file)
            
        if(self.events is None):
            self.events = self.filter_game(game)
        else:
            self.events = [*self.events, *self.filter_game(game)]

    def loadFilesFromDir(self, dir):
        files = glob.glob(dir)
        for file in tqdm(files):
            self.loadFile(file)

    
def main():
    datasetMaker = CreateDataset()
    datasetMaker.loadFilesFromDir('events/*.json')

    x, y = datasetMaker.createDataset()
    print(len(x))
    print(x[0], y[0])

if __name__ == "__main__":
    main()

# for i in range(len(game)) [(4):len(game)-self.possession_limit]:
        #     current_n = [a for a in game[i: i + self.possession_limit]]
        #     self.getXfromN(current_n)
        #     dataset.append(current_n)