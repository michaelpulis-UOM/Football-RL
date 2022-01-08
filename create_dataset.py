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
            'foul': self.FOUL,

        }

        self.file_limit = 100

        self.ID_to_str = { v:k for k,v in self.good_events.items()}

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
    # one hot encoded of location
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
            

    # Dataset specifications:
    # x:
    # float: action ID (0 = PASS, 1 = SHOOT...etc)
    # float: x coordinate of action
    # float: y coordinate of action

    # y1:
    # one hot encoded vector of next location
    # y2:
    # x value of next location
    # y3:
    # y value of next location
    def createDatasetMultY(self):

        x, y1, y2, y3 = [], [], [], []
        for i in range(len(self.events)-1):

            action = self.events[i]
            next_action = self.events[i+1]

            x_entry = [self.getIDFromAction(action), action['location'][0], action['location'][1]]
            y_class = np.zeros((len(self.good_events)))
            y_class[int(self.getIDFromAction(next_action))] = 1
            
            y_pos = self.getEndLocationFromAction(next_action)
            if(y_pos is None): continue
            
            x.append(x_entry)
            y1.append(y_class)
            y2.append(y_pos[0]/120)
            y3.append(y_pos[1]/80)

        return np.array(x), np.array(y1), np.array(y2), np.array(y3)

    def getEndLocationFromAction(self, action):
        try:
            action_type = self.getIDFromAction(action)
            if(action_type == self.SHOOT): return action['location']
            if(action_type == self.PASS): return action['pass']['end_location']
            if(action_type == self.CARRY): return action['carry']['end_location']
        except Exception as e:
            print("Failed:", e)
            return None

    def loadFile(self, file_location):
        
        with open(file_location, 'r', encoding='utf-8') as file:
            game = json.load(file)
            
        if(self.events is None):
            self.events = self.filter_game(game)
        else:
            self.events = [*self.events, *self.filter_game(game)]

    def loadFilesFromDir(self, dir):
        files = glob.glob(dir)
        for file in tqdm(files[:self.file_limit]):
            self.loadFile(file)

    
def main():
    datasetMaker = CreateDataset()
    datasetMaker.loadFile('data.json')
    # datasetMaker.loadFilesFromDir('events/*.json')

    x, y1, y2 = datasetMaker.createDatasetMultY()
    print(len(x))
    print(x[0], y1[0], y2[0])

if __name__ == "__main__":
    main()

# for i in range(len(game)) [(4):len(game)-self.possession_limit]:
        #     current_n = [a for a in game[i: i + self.possession_limit]]
        #     self.getXfromN(current_n)
        #     dataset.append(current_n)