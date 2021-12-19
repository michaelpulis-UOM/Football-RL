import numpy as numpy 
import json

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
        self.good_events = {
            'pass':0,
            'shot':0,
            'carry':0,
            'Clearance':0,
            'Foul Won':0,
            'Foul Committed':0,
        }

    def filter_game(self, dataset):
        return [ a for a in dataset if a['type']['name'].lower() in self.good_events]
            

    def loadFile(self, file_location):
        
        with open(file_location, 'r') as file:
            game = json.load(file)
            
        game = self.filter_game(game)
        last_possession_id = None
        dataset = []
    
        for i in range(len(game)) [(4):len(game)-self.possession_limit]:
            current_n = [a['type']['name'] for a in game[i: i + self.possession_limit]]
            dataset.append(current_n)

        flat = []
        for item in dataset:
            for a in item:
                flat.append(a)
        
        print(set(flat))
        # print(dataset)
        # for a in dataset:
        #     print(a)

def main():
    datasetMaker = CreateDataset()
    datasetMaker.loadFile("data.json")


if __name__ == "__main__":
    main()


